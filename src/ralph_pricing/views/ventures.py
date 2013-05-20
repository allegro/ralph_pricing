# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from ralph_pricing.views.reports import Report, currency
from ralph_pricing.models import UsageType, ExtraCostType, Venture
from ralph_pricing.forms import DateRangeForm


class AllVentures(Report):
    template_name = 'ralph_pricing/ventures.html'
    Form = DateRangeForm
    section = 'all-ventures'

    @staticmethod
    def get_data(start, end, **kwargs):
        ventures = Venture.objects.order_by('name')
        total_count = ventures.count()
        for i, venture in enumerate(ventures):
            count, price = venture.get_assets_count_price(start, end)
            path = '/'.join(
                v.name for v in venture.get_ancestors(include_self=True),
            )
            row = [
                venture.venture_id,
                path,
                venture.department,
                count,
                currency(price),
            ]
            for usage_type in UsageType.objects.order_by('name'):
                count, price = venture.get_usages_count_price(
                    start,
                    end,
                    usage_type,
                )
                row.append(count)
                if price is None:
                    row.append('NO PRICE')
                else:
                    row.append(currency(price))
            for extra_cost_type in ExtraCostType.objects.order_by('name'):
                row.append(currency(venture.get_extra_costs(
                    start,
                    end,
                    extra_cost_type,
                )))
            progress = (100 * i) // total_count
            yield progress, row

    @staticmethod
    def get_header(**kwargs):
        header = [
            _("ID"),
            _("Venture"),
            _("Department"),
            _("Assets count"),
            _("Assets price"),
        ]
        for usage_type in UsageType.objects.order_by('name'):
            header.append(_("{} count").format(usage_type.name))
            header.append(_("{} price").format(usage_type.name))
        for extra_cost_type in ExtraCostType.objects.order_by('name'):
            header.append(extra_cost_type.name)
        return header


class TopVentures(AllVentures):
    section = 'top-ventures'

    @staticmethod
    def get_data(start, end):
        ventures = Venture.objects.root_nodes().order_by('name')
        total_count = ventures.count()
        for i, venture in enumerate(ventures):
            count, price = venture.get_assets_count_price(
                start,
                end,
                descendants=True,
            )
            row = [
                venture.venture_id,
                venture.name,
                venture.department,
                count,
                currency(price),
            ]
            for usage_type in UsageType.objects.order_by('name'):
                count, price = venture.get_usages_count_price(
                    start,
                    end,
                    usage_type,
                    descendants=True,
                )
                row.append(count)
                row.append(currency(price))
            for extra_cost_type in ExtraCostType.objects.order_by('name'):
                row.append(currency(venture.get_extra_costs(
                    start,
                    end,
                    extra_cost_type,
                    descendants=True,
                )))
            progress = (100 * i) // total_count
            yield progress, row

