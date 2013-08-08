# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.utils.translation import ugettext_lazy as _

from ralph_pricing.views.reports import Report, currency
from ralph_pricing.models import UsageType, ExtraCostType, Venture
from ralph.business.models import Venture as ralph_venture
from ralph_pricing.forms import DateRangeForm


class AllVentures(Report):
    template_name = 'ralph_pricing/ventures_all.html'
    Form = DateRangeForm
    section = 'all-ventures'
    report_name = _('All Ventures Report')

    @staticmethod
    def get_data(start, end, show_in_ralph=False, **kwargs):
        ventures = Venture.objects.order_by('name')
        total_count = ventures.count() + 1  # additional step for post-process
        data = []
        totals = {}
        values = []
        for i, venture in enumerate(ventures):
            show_venture = ralph_venture.objects.get(
                id=venture.venture_id
            ).show_in_ralph
            if show_in_ralph and not show_venture:
                continue
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
                show_in_ralph,
                venture.department,
                venture.business_segment,
                venture.profit_center,
                count,
                currency(price),
                currency(cost),
            ]
            column = len(row)
            for usage_type in UsageType.objects.order_by('name'):
                count, price = venture.get_usages_count_price(
                    start,
                    end,
                    usage_type,
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
            for extra_cost_type in ExtraCostType.objects.order_by('name'):
                row.append(currency(venture.get_extra_costs(
                    start,
                    end,
                    extra_cost_type,
                )))
            progress = (100 * i) // total_count
            data.append(row)
            yield min(progress, 99), data
        for row, values_row in zip(data, values):
            for column, total in totals.iteritems():
                if total:
                    row[column] = '{:.2f}%'.format(
                        100 * values_row[column] / total,
                    )
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
        for usage_type in UsageType.objects.order_by('name'):
            header.append(_("{} count").format(usage_type.name))
            if usage_type.show_value_percentage:
                header.append(_("{} count %").format(usage_type.name))
            header.append(_("{} price").format(usage_type.name))
            if usage_type.show_price_percentage:
                header.append(_("{} price %").format(usage_type.name))
        for extra_cost_type in ExtraCostType.objects.order_by('name'):
            header.append(extra_cost_type.name)
        return header


class TopVentures(AllVentures):
    template_name = 'ralph_pricing/ventures_top.html'
    section = 'top-ventures'
    report_name = _('Top Ventures Report')

    @staticmethod
    def get_data(start, end, show_in_ralph=False, **kwargs):
        ventures = Venture.objects.root_nodes().order_by('name')
        total_count = ventures.count() + 1  # additional step for post-process
        data = []
        totals = {}
        values = []
        for i, venture in enumerate(ventures):
            show_venture = ralph_venture.objects.get(
                id=venture.venture_id
            ).show_in_ralph
            if show_in_ralph and not show_venture:
                continue
            values_row = {}
            values.append(values_row)
            count, price, cost = venture.get_assets_count_price_cost(
                start,
                end,
                descendants=True,
            )
            row = [
                venture.venture_id,
                venture.name,
                ralph_venture.objects.get(id=venture.venture_id).show_in_ralph,
                venture.department,
                venture.business_segment,
                venture.profit_center,
                count,
                currency(price),
                currency(cost),
            ]
            column = len(row)
            for usage_type in UsageType.objects.order_by('name'):
                count, price = venture.get_usages_count_price(
                    start,
                    end,
                    usage_type,
                    descendants=True,
                )
                row.append(count)
                column += 1
                if usage_type.show_value_percentage:
                    row.append('')
                    totals[column] = totals.get(column, 0) + count
                    values_row[column] = count
                    column += 1
                row.append(currency(price))
                column += 1
                if usage_type.show_price_percentage:
                    row.append('')
                    totals[column] = totals.get(column, 0) + price
                    values_row[column] = price
                    column += 1
            for extra_cost_type in ExtraCostType.objects.order_by('name'):
                row.append(currency(venture.get_extra_costs(
                    start,
                    end,
                    extra_cost_type,
                    descendants=True,
                )))
            progress = (100 * i) // total_count
            data.append(row)
            yield min(progress, 99), data
        for row, values_row in zip(data, values):
            for column, total in totals.iteritems():
                if total:
                    row[column] = '{:.2f}%'.format(
                        100 * values_row[column] / total,
                    )
        yield 100, data
