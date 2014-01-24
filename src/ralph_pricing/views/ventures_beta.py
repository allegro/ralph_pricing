# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
import time
from decimal import Decimal as D

from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum, Count

from ralph_pricing.views.reports import Report, currency
from ralph_pricing.models import (
    DailyDevice,
    DailyUsage,
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
    def get_data(warehouse, start, end, show_in_ralph=False, forecast=False, **kwargs):
        ventures = Venture.objects.order_by('name')
        usage_types = AllVenturesBeta._get_visible_usage_types()
        total_count = usage_types.count() + 2  # + ventures preparsing + assets
        report_days = (end - start).days + 1
        progress = 1
        data = {}
        totals = {}
        values = []

        def get_assets_costs():
            assets_report_query = DailyDevice.objects.filter(
                    pricing_device__is_virtual=False,
                    date__gte=start,
                    date__lte=end,
                )

            if show_in_ralph:
                assets_report_query = assets_report_query.filter(
                    pricing_venture__is_active=True
                )

            assets_report = assets_report_query.values('pricing_venture')\
                .annotate(assets_price=Sum('price'))\
                .annotate(assets_cost=Sum('daily_cost'))\
                .annotate(assets_count=Count('id'))

            # calc blades
            # todo
            return assets_report

        print("ventures preparsing")
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

        print("\n assets")
        for ar in get_assets_costs():
            if ar['pricing_venture'] in data:
                data[ar['pricing_venture']].update({
                    'assets_count': ar['assets_count'] / report_days,
                    'assets_cost': ar['assets_cost'],
                    'assets_price': ar['assets_price'],
                })

        print("\nusages")

        progress += 1
        yield progress / total_count, []

        # todo: check if in every day for ut in report there is price

        for i, usage_type in enumerate(usage_types):
            print("\n\nut: {0}".format(usage_type.name))
            usage_type_count = 'usage_{0}_count'.format(usage_type.id)
            usage_type_cost = 'usage_{0}_cost'.format(usage_type.id)

            # usage count per venture
            ut_report_query = DailyUsage.objects.filter(
                date__gte=start,
                date__lte=end,
                type=usage_type,
            )
            if usage_type.by_warehouse:
                ut_report_query = ut_report_query.filter(
                    warehouse_id=warehouse.id
                )

            if show_in_ralph:
                ut_report_query = ut_report_query.filter(
                    pricing_venture__is_active=True
                )

            ut_report = ut_report_query.values('pricing_venture').annotate(
                total_usage=Sum('value')
            )
            for p in ut_report:
                if p['pricing_venture'] in data:
                    venture_row = data[p['pricing_venture']]
                    total_usage = p['total_usage'] / (report_days if usage_type.average else 1)
                    venture_row[usage_type_count] = total_usage
            # if usage_type.id == 12:
            #     import ipdb; ipdb.set_trace()
            # for every usage price in report range
            for usage_price in usage_type.usageprice_set.filter(
                end__gte=start,
                start__lte=end
            ):
                print("up: {0}".format(str(usage_price)))
                up_start = max(start, usage_price.start)
                up_end = min(end, usage_price.end)
                days = (up_end - up_start).days + 1

                price = usage_price.forecast_price if forecast else usage_price.price

                if usage_type.by_cost:
                    cost = usage_price.forecast_cost if forecast else usage_price.cost

                    total_usage = DailyUsage.objects.filter(
                        date__gte=up_start,
                        date__lte=up_end,
                        type=usage_type.id,
                    ).aggregate(total=Sum('value')).get('total_usage', 0)
                    if total_usage == 0:
                        price = 0
                    else:
                        price = D(cost / total_usage / days)

                up_report_query = DailyUsage.objects.filter(
                    date__gte=up_start,
                    date__lte=up_end,
                    type=usage_type,
                )

                if usage_type.by_warehouse:
                    ut_report_query = ut_report_query.filter(
                        warehouse_id=warehouse.id
                    )

                if show_in_ralph:
                    up_report_query = up_report_query.filter(
                        pricing_venture__is_active=True
                    )

                up_report = up_report_query.values('pricing_venture').annotate(
                    total_usage=Sum('value')
                )
                print("query completed; going for items")
                for p in up_report:
                    if p['pricing_venture'] in data:
                        venture_row = data[p['pricing_venture']]
                        # use defaultdict
                        venture_row[usage_type_cost] = venture_row.get(usage_type_cost, 0) + D(p['total_usage']) * price

                progress += 1
                yield progress / total_count, []
            # import ipdb; ipdb.set_trace()

        # prepare final data
        order = ['venture_id', 'path', 'is_active', 'department', 'business_segment', 'profit_center']
        final_data = []
        for venture in ventures:
            venture_data = data.get(venture.id)
            if not venture_data:
                continue
            venture_row = []
            for field in order:
                venture_row.append(venture_data[field])

            # assets
            for asset_field in ('assets_count', 'assets_price', 'assets_cost'):
                venture_row.append(venture_data.get(asset_field, 0))

            # usages
            for usage in usage_types:
                usage_id = usage.id
                usage_type_count = 'usage_{0}_count'.format(usage_id)
                usage_type_cost = 'usage_{0}_cost'.format(usage_id)

                venture_row.extend([
                    '{:.2f}'.format(venture_data.get(usage_type_count, 0)),
                    currency(venture_data.get(usage_type_cost, 0))
                ])
            final_data.append(venture_row)
        # import ipdb; ipdb.set_trace()
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
            header.append(_("{} price").format(usage_type.name))
            if usage_type.show_price_percentage:
                header.append(_("{} cost %").format(usage_type.name))
        for extra_cost_type in ExtraCostType.objects.order_by('name'):
            header.append(extra_cost_type.name)
        return header
