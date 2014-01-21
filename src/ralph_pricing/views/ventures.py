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
from django.db.models import Sum

from ralph_pricing.views.reports import Report, currency
from ralph_pricing.models import UsageType, ExtraCostType, Venture, DailyUsage
from ralph_pricing.forms import DateRangeForm

logger = logging.getLogger(__name__)


class AllVentures(Report):
    '''
        Reports for all ventures
    '''
    template_name = 'ralph_pricing/ventures_all.html'
    Form = DateRangeForm
    section = 'all-ventures'
    report_name = _('All Ventures Report')

    @staticmethod
    def _get_visible_usage_types():
        return UsageType.objects.exclude(show_in_report=False).order_by('name')

    @staticmethod
    def get_data(*a, **k):
        return AllVentures.get_data_new(*a, **k)

    @staticmethod
    def get_data_new(warehouse, start, end, show_in_ralph=False, forecast=False, **kwargs):
        ventures = Venture.objects.order_by('name')
        usage_types = AllVentures._get_visible_usage_types()
        total_count = usage_types.count() + 1
        data = {}
        totals = {}
        values = []
        print("ventures preparsing")
        for i, venture in enumerate(ventures):
            count, price, cost = venture.get_assets_count_price_cost(
                start, end,
            )
            path = '/'.join(
                v.name for v in venture.get_ancestors(include_self=True),
            )

            data[venture.id] = {
                'id': venture.id,
                'path': path,
                'is_active': venture.is_active,
                'department': venture.department,
                'business_segment': venture.business_segment,
                'profit_center': venture.profit_center,
                # 'asset_count': count,
                # 'asset_price': currency(price),
                # 'asset_cost': currency(cost),
            }

        print("\nusages")

        for i, usage_type in enumerate(usage_types):
            print("\n\nut: {0}".format(usage_type.name))
            usage_type_count = 'usage_{0}_count'.format(usage_type.id)
            usage_type_cost = 'usage_{0}_cost'.format(usage_type.id)

            # usage count per venture
            ut_report_query = DailyUsage.objects.filter(
                date__gte=start,
                date__lte=end
            )
            if show_in_ralph:
                ut_report_query.filter(pricing_venture__is_active=True)

            ut_report = ut_report_query.values('pricing_venture').annotate(
                total_usage=Sum('value')
            )

            for p in ut_report:
                if p['pricing_venture'] in data:
                    venture_row = data[p['pricing_venture']]
                    venture_row[usage_type_count] = p['total_usage']

            # for every usage price in report range
            for usage_price in usage_type.usageprice_set.filter(
                end__gte=start,
                start__lte=end
            ):
                print("up: {0}".format(str(usage_price)))
                up_start = max(start, usage_price.start)
                up_end = min(end, usage_price.end)

                price = usage_price.forecast_price if forecast else usage_price.price

                if usage_type.by_cost:
                    cost = usage_price.forecast_cost if forecast else usage_price.cost

                    dailyusages = DailyUsage.objects.filter(
                        date__gte=up_start,
                        date__lte=up_end,
                        type=usage_type.id,
                        warehouse_id=warehouse.id,
                    )
                    total_usage = sum([D(dailyusage.value) for dailyusage in dailyusages])
                    if total_usage == 0:
                        price = 0
                    else:
                        price = D(cost / total_usage / ((up_end - up_start).days + 1))

                up_report_query = DailyUsage.objects.filter(
                    date__gte=up_start,
                    date__lte=up_end
                )
                if show_in_ralph:
                    up_report_query.filter(pricing_venture__is_active=True)

                up_report = up_report_query.values('pricing_venture').annotate(
                    total_usage=Sum('value')
                )
                print("query completed; going for items")
                for p in up_report:
                    if p['pricing_venture'] in data:
                        venture_row = data[p['pricing_venture']]
                        # use defaultdict
                        venture_row[usage_type_cost] = venture_row.get(usage_type_cost, 0) + D(p['total_usage']) * price
                        # venture_row[usage_type_count] = venture_row.get(usage_type_count, 0) + p['total_usage']

        import ipdb; ipdb.set_trace()

    @staticmethod
    def get_data_old(
        warehouse,
        start,
        end,
        show_in_ralph=False,
        forecast=False,
        **kwargs
    ):
        '''
            Generate raport for all ventures

            :param integer warehouse: Id warehouse for which is generate report
            :param datetime start: Start of the time interval
            :param datetime end: End of the time interval
            :param boolean show_in_ralph: if true, show only active ventures
            :param boolean forecast: if true, generate forecast raport
            :returns list: List of lists with report data and percent progress
            :rtype list:
        '''
        # 'show_in_ralph' == 'show only active' checkbox in gui
        ventures = Venture.objects.filter(venture_id=671).order_by('name')
        total_count = ventures.count() + 1  # additional step for post-process
        data = []
        totals = {}
        values = []
        start_time = time.clock()
        for i, venture in enumerate(ventures):
            if show_in_ralph and not venture.is_active:
                continue
            # logger.info('\n=================\n')
            venture_start_time = time.clock()
            asset_start_time = time.clock()
            values_row = {}
            values.append(values_row)
            count, price, cost = venture.get_assets_count_price_cost(
                start, end,
            )
            path = '/'.join(
                v.name for v in venture.get_ancestors(include_self=True),
            )
            row = [
                venture.venture_id,
                path,
                venture.is_active,
                venture.department,
                venture.business_segment,
                venture.profit_center,
                count,
                currency(price),
                currency(cost),
            ]
            column = len(row)
            asset_end_time = time.clock()
            # logger.info(u'{0}: asset time: {1} '.format(path, asset_end_time - asset_start_time))
            usages_start_time = time.clock()
            for usage_type in AllVentures._get_visible_usage_types():
                count, price = venture.get_usages_count_price(
                    start,
                    end,
                    usage_type,
                    warehouse.id if usage_type.by_warehouse else None,
                    forecast=forecast,
                )
                row.append(count)
                column += 1
                if usage_type.show_value_percentage:
                    row.append('')
                    totals[column] = totals.get(column, 0) + count
                    values_row[column] = count
                    column += 1
                if price is None:
                    row.append('NO PRICE')
                else:
                    row.append(currency(price))
                column += 1
                if usage_type.show_price_percentage:
                    row.append('')
                    totals[column] = totals.get(column, 0) + count
                    values_row[column] = price
                    column += 1
            usages_end_time = time.clock()
            # logger.info(u'{0}: usages time: {1} '.format(path, usages_end_time - usages_start_time))
            extra_cost_start_time = time.clock()
            for extra_cost_type in ExtraCostType.objects.order_by('name'):
                row.append(currency(venture.get_extra_costs(
                    start,
                    end,
                    extra_cost_type,
                )))
            progress = (100 * i) // total_count
            data.append(row)
            extra_cost_end_time = time.clock()
            venture_end_time = time.clock()
            # logger.info(u'{0}: extra cost time: {1} '.format(path, extra_cost_end_time - extra_cost_start_time))
            # logger.info(u'{0}: total venture time: {1}'.format(path, venture_end_time - venture_start_time))
            # import ipdb; ipdb.set_trace()
            yield min(progress, 99), data
        for row, values_row in zip(data, values):
            for column, total in totals.iteritems():
                if total:
                    row[column] = '{:.2f}%'.format(
                        100 * values_row[column] / total,
                    )
        end_time = time.clock()
        logger.info(u'total_time: {0} '.format(end_time - start_time))
        yield 100, data

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
        for usage_type in AllVentures._get_visible_usage_types():
            header.append(_("{} count").format(usage_type.name))
            if usage_type.show_value_percentage:
                header.append(_("{} count %").format(usage_type.name))
            header.append(_("{} price").format(usage_type.name))
            if usage_type.show_price_percentage:
                header.append(_("{} price %").format(usage_type.name))
        for extra_cost_type in ExtraCostType.objects.order_by('name'):
            header.append(extra_cost_type.name)
        return header
