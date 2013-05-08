# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ralph_pricing.views.base import Base
from ralph_pricing.models import UsageType, ExtraCostType, Venture
from ralph_pricing.forms import DateRangeForm


def currency(value):
    return '{:,.2f} {}'.format(value or 0, settings.CURRENCY).replace(',', ' ')


class AllVentures(Base):
    template_name = 'ralph_pricing/ventures.html'

    def __init__(self, *args, **kwargs):
        super(AllVentures, self).__init__(*args, **kwargs)
        self.form = None

    def get_data(self, start, end):
        ventures = Venture.objects.order_by('name')
        data = []
        for venture in ventures:
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
            data.append(row)
        return data

    def get_header(self):
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

    def get_context_data(self, **kwargs):
        context = super(AllVentures, self).get_context_data(**kwargs)
        if self.request.GET.get('start'):
            form = DateRangeForm(self.request.GET)
        else:
            today = datetime.date.today()
            form = DateRangeForm(
                initial={
                    'start': today - datetime.timedelta(days=31),
                    'end': today,
                },
            )
        if form.is_valid():
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            data=self.get_data(start, end)
            context.update(data=data)
        context.update({
            'section': 'all-ventures',
            'form': form,
            'header': self.get_header(),
        })
        return context


class TopVentures(AllVentures):
    def get_data(self, start, end):
        ventures = Venture.objects.root_nodes().order_by('name')
        data = []
        for venture in ventures:
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
            data.append(row)
        return data

    def get_context_data(self, **kwargs):
        context = super(TopVentures, self).get_context_data(**kwargs)
        context.update({
            'section': 'top-ventures',
        })
        return context
