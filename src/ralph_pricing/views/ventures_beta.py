# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
from collections import defaultdict
from decimal import Decimal as D

from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum, Count

from ralph_pricing.views.reports import Report, currency
from ralph_pricing.models import (
    DailyDevice,
    DailyUsage,
    ExtraCost,
    ExtraCostType,
    UsageType,
    Venture,
)
from ralph_pricing.forms import DateRangeForm

logger = logging.getLogger(__name__)


class AllVenturesBeta(Report):
    '''
        Reports for all ventures
    '''
    template_name = 'ralph_pricing/ventures_all.html'
    Form = DateRangeForm
    section = 'all-ventures'
    report_name = _('All Ventures Report Beta')

    @staticmethod
    def _get_visible_usage_types():
        return UsageType.objects.exclude(show_in_report=False).order_by('name')

    @staticmethod
    def _get_assets_costs(start, end, only_active=False):
        """
        Returns mini-report for assets costs per venture.

        Result format: list of dicts ie:
        [
            {
                'pricing_venture': 1,
                'assets_price': 1234,  # total price of assets in venture
                'assets_cost': 111,  # sum of daily costs (deprecation)
                'assets_count': 11.11,  # average count of assets
            }
        ]
        """
        assets_report_query = DailyDevice.objects.filter(
            pricing_device__is_virtual=False,
            date__gte=start,
            date__lte=end,
        )

        if only_active:
            assets_report_query = assets_report_query.filter(
                pricing_venture__is_active=True
            )

        assets_report = assets_report_query.values('pricing_venture')\
            .annotate(assets_price=Sum('price'))\
            .annotate(assets_cost=Sum('daily_cost'))\
            .annotate(assets_count=Count('id'))

        # calc blades
        # TODO
        return assets_report

    @staticmethod
    def _get_usage_type_costs_in_period(
        start,
        end,
        usage_type,
        usage_price,
        only_active=False,
        warehouse=None,
        forecast=False,
    ):
        up_start = max(start, usage_price.start)
        up_end = min(end, usage_price.end)
        days = (up_end - up_start).days + 1

        price = usage_price.forecast_price if forecast else \
            usage_price.price

        # if usage type has cost - price has to be calculated from cost
        # and total usage
        if usage_type.by_cost:
            cost = usage_price.forecast_cost if forecast else \
                usage_price.cost

            # get total usage in usage_price period
            total_usage = DailyUsage.objects.filter(
                date__gte=usage_price.start,
                date__lte=usage_price.end,
                type=usage_type.id,
            ).aggregate(total=Sum('value')).get('total_usage', 0)

            # calculate price for single unit usage
            if total_usage == 0:
                price = 0
            else:
                price = D(cost / total_usage / days)

        # query for usages in given period grouped by venture
        up_report_query = DailyUsage.objects.filter(
            date__gte=up_start,
            date__lte=up_end,
            type=usage_type,
        )
        if usage_type.by_warehouse:
            up_report_query = up_report_query.filter(
                warehouse_id=warehouse.id
            )
        if only_active:
            up_report_query = up_report_query.filter(
                pricing_venture__is_active=True
            )
        up_report = up_report_query.values('pricing_venture').annotate(
            total_usage=Sum('value')
        )

        for up in up_report:
            up['total_cost'] = D(up['total_usage']) * price

        return up_report

    @staticmethod
    def _get_usage_type_costs(
        start,
        end,
        usage_type,
        only_active=False,
        warehouse=None,
        forecast=False,
    ):
        report_days = (end - start).days + 1
        usage_type_count = 'usage_{0}_count'.format(usage_type.id)
        usage_type_cost = 'usage_{0}_cost'.format(usage_type.id)
        usage_type_report = defaultdict(dict)

        # total usage count per venture
        # calculated in single sql query total usage of usage type in given
        # period (from start to end) per venture
        ut_report_query = DailyUsage.objects.filter(
            date__gte=start,
            date__lte=end,
            type=usage_type,
        )
        if usage_type.by_warehouse:
            ut_report_query = ut_report_query.filter(
                warehouse_id=warehouse.id
            )

        if only_active:
            ut_report_query = ut_report_query.filter(
                pricing_venture__is_active=True
            )

        # query for sum of daily usages per venture
        ut_report = ut_report_query.values('pricing_venture').annotate(
            total_usage=Sum('value')
        )
        for p in ut_report:
            total_usage = p['total_usage'] / (report_days if usage_type.average else 1)
            usage_type_report[p['pricing_venture']][usage_type_count] = total_usage

        # total cost of daily usages is caluclated in many parts
        # every part is single period in which price/cost is definded for
        # usage type. For example if usage price is defined for (1.10-15.11),
        # (16.11-25.11) and (26.11-13.12) and report is calculated for
        # (1-30.11), there will be three parts: (1-15.11), (16-25.11),
        # (26-30.11)
        for usage_price in usage_type.usageprice_set.filter(
            end__gte=start,
            start__lte=end
        ):
            up_report = AllVenturesBeta._get_usage_type_costs_in_period(
                start,
                end,
                usage_type,
                usage_price,
                only_active,
                warehouse,
                forecast,
            )
            for p in up_report:
                venture_row = usage_type_report[p['pricing_venture']]
                venture_row[usage_type_cost] = \
                    venture_row.get(usage_type_cost, 0) + D(p['total_cost'])

        return usage_type_report

    @staticmethod
    def _get_extra_cost_report(
        start,
        end,
        extra_cost_type,
        only_active=False,
    ):
        extra_cost_report = defaultdict(dict)
        extra_cost_cost = 'extra_cost_{0}_cost'.format(extra_cost_type.id)

        ec_report = ExtraCost.objects.filter(
            type=extra_cost_type,
            end__gte=start,
            start__lte=end
        ).values('pricing_venture', 'price', 'end', 'start')

        for p in ec_report:
            days = (min(end, p['end']) - max(start, p['start'])).days
            venture_row = extra_cost_report[p['pricing_venture']]
            venture_row[extra_cost_cost] = \
                venture_row.get(extra_cost_cost, 0) + D(p['price']) * days

        return extra_cost_report

    @staticmethod
    def _get_usage_types_price_defined(usage_types, start, end):
        price_defined = {}
        total_days = (end - start).days
        for ut in usage_types:
            ut_days = 0
            # TODO: improve preformance
            for up in ut.usageprice_set.filter(
                end__gte=start,
                start__lte=end
            ):
                ut_days += (min(end, up.end) - max(start, up.start)).days
            price_defined[ut.id] = ut_days == total_days
        return price_defined

    @staticmethod
    def _prepare_final_report(
        start,
        end,
        data,
        ventures,
        usage_types,
        extra_costs,
    ):
        order = ['venture_id', 'path', 'is_active', 'department', 'business_segment', 'profit_center']
        final_data = []

        usage_types_price_defined = \
            AllVenturesBeta._get_usage_types_price_defined(
                usage_types,
                start,
                end,
            )

        for venture in ventures:
            venture_data = data.get(venture.id)
            if not venture_data:
                continue
            venture_row = []
            for field in order:
                venture_row.append(venture_data[field])

            # assets
            venture_row.append(venture_data.get('assets_count', 0))
            venture_row.append(currency(venture_data.get('assets_price', 0)))
            venture_row.append(currency(venture_data.get('assets_cost', 0)))

            # usages
            for usage in usage_types:
                usage_id = usage.id
                usage_type_count = 'usage_{0}_count'.format(usage_id)
                usage_type_cost = 'usage_{0}_cost'.format(usage_id)

                cost = currency(0)
                if venture_data.get(usage_type_count):
                    cost = currency(venture_data[usage_type_cost]) if usage_types_price_defined[usage_id] else 'NO PRICE'

                venture_row.extend([
                    '{:.2f}'.format(venture_data.get(usage_type_count, 0)),
                    cost
                ])

            # extra costs
            for extra_cost in extra_costs:
                extra_cost_id = extra_cost.id
                extra_cost_cost = 'extra_cost_{0}_cost'.format(extra_cost_id)

                venture_row.extend([
                    currency(venture_data.get(extra_cost_cost, 0))
                ])

            final_data.append(venture_row)
        return final_data

    @staticmethod
    def get_data(
        warehouse,
        start,
        end,
        show_in_ralph=False,
        forecast=False,
        **kwargs
    ):
        ventures = Venture.objects.order_by('name')
        if show_in_ralph:
            ventures = ventures.filter(is_active=True)

        usage_types = AllVenturesBeta._get_visible_usage_types()
        extra_cost_types = ExtraCostType.objects.all()
        total_count = usage_types.count() + extra_cost_types.count() + 2
        report_days = (end - start).days + 1
        progress = 1
        data = {}
        logger.info("Generating report from {0} to {1}".format(start, end))

        # ventures preparsing
        logger.info("Ventures preparsing")
        for i, venture in enumerate(ventures):
            path = '/'.join(
                v.name for v in venture.get_ancestors(include_self=True),
            )

            data[venture.id] = {
                'id': venture.id,
                'venture_id': venture.venture_id,
                'path': path,
                'is_active': venture.is_active,
                'department': venture.department,
                'business_segment': venture.business_segment,
                'profit_center': venture.profit_center,
            }
        yield progress / total_count, []

        # assets costs
        logger.info("Assets costs generating")
        for ar in AllVenturesBeta._get_assets_costs(start, end, show_in_ralph):
            if ar['pricing_venture'] in data:
                data[ar['pricing_venture']].update({
                    'assets_count': ar['assets_count'] / report_days,
                    'assets_cost': ar['assets_cost'],
                    'assets_price': ar['assets_price'] / report_days,
                })

        progress += 1
        yield progress / total_count, []

        # usages
        logger.info("Usages parsing")
        for i, usage_type in enumerate(usage_types):
            logger.info("usage type: {0}".format(usage_type.name))
            usage_type_report = AllVenturesBeta._get_usage_type_costs(
                start,
                end,
                usage_type,
                show_in_ralph,
                warehouse,
                forecast
            )

            for venture_id, venture_usage in usage_type_report.iteritems():
                if venture_id in data:
                    data[venture_id].update(venture_usage)

            progress += 1
            yield progress / total_count, []

        # extra costs
        logger.info("Calculating extra costs")
        for ec in extra_cost_types:
            logger.info("Extra cost: {0}".format(ec.name))
            extra_cost_report = AllVenturesBeta._get_extra_cost_report(
                start,
                end,
                ec,
                show_in_ralph,
            )

            for venture_id, venture_usage in extra_cost_report.iteritems():
                if venture_id in data:
                    data[venture_id].update(venture_usage)

            progress += 1
            yield progress / total_count, []

        # prepare final data
        final_data = AllVenturesBeta._prepare_final_report(
            start,
            end,
            data,
            ventures,
            usage_types,
            extra_cost_types,
        )
        yield 100, final_data

    @staticmethod
    def get_header(**kwargs):
        header = [
            _("ID"),
            _("Venture"),
            _("Active at %s" % datetime.date.today()),
            _("Department"),
            _("Business segment"),
            _("Profit center"),
            _("Assets count"),
            _("Assets price"),
            _("Assets cost"),
        ]
        for usage_type in AllVenturesBeta._get_visible_usage_types():
            header.append(_("{} count").format(usage_type.name))
            if usage_type.show_value_percentage:
                header.append(_("{} count %").format(usage_type.name))
            header.append(_("{} cost").format(usage_type.name))
            if usage_type.show_price_percentage:
                header.append(_("{} cost %").format(usage_type.name))
        for extra_cost_type in ExtraCostType.objects.order_by('name'):
            header.append(extra_cost_type.name)
        return header
