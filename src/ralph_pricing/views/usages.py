# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect

from ralph_pricing.app import Scrooge
from ralph_pricing.forms import UsagesFormSet
from ralph_pricing.menus import usages_menu
from ralph_pricing.models import UsageType
from ralph_pricing.views.base import Base


class Usages(Base):
    template_name = 'ralph_pricing/usages.html'

    def __init__(self, *args, **kwargs):
        super(Usages, self).__init__(*args, **kwargs)
        self.formset = None
        self.usage_type = None
        self.usage_type_name = None

    def init_args(self):
        self.usage_type_name = self.kwargs.get('usage')
        if self.usage_type_name is not None:
            self.usage_type = get_object_or_404(
                UsageType,
                name=self.usage_type_name,
            )

    def post(self, *args, **kwargs):
        self.init_args()
        if self.usage_type:
            self.formset = UsagesFormSet(
                self.request.POST,
                queryset=self.usage_type.usageprice_set.order_by('start'),
            )
            self.formset.usage_type = self.usage_type
            for form in self.formset.extra_forms:
                if form.has_changed():
                    form.instance.type = self.usage_type
            if self.formset.is_valid():
                self.formset.save()
                messages.success(self.request, "Usage prices updated.")
                return HttpResponseRedirect(self.request.path)
            else:
                messages.error(self.request, "Please fix the errors.")
        return super(Usages, self).get(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.init_args()
        if self.usage_type_name:
            self.formset = UsagesFormSet(
                queryset=self.usage_type.usageprice_set.order_by('start'),
            )
        return super(Usages, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Usages, self).get_context_data(**kwargs)

        if self.usage_type:
            by_warehouse = self.usage_type.by_warehouse
            by_internet_provider = self.usage_type.by_internet_provider
        else:
            by_warehouse = None
            by_internet_provider = None

        by_cost = self.usage_type.by_cost if self.usage_type else None
        by_team = self.usage_type.by_team if self.usage_type else None
        context.update({
            'section': 'usages',
            'sidebar_items': usages_menu(
                '/{0}/usages'.format(Scrooge.url_prefix),
                self.usage_type_name
            ),
            'sidebar_selected': self.usage_type_name,
            'by_cost': by_cost,
            'by_warehouse': by_warehouse,
            'by_team': by_team,
            'by_internet_provider': by_internet_provider,
            'formset': self.formset,
            'hidden': {
                'by_cost': ['price', 'forecast_price'],
                'not_by_cost': ['cost', 'forecast_cost'],
                'not_by_warehouse': ['warehouse'],
                'not_by_team': ['team', 'team_members_count'],
                'not_by_internet_provider': ['internet_provider'],
            }
        })
        return context
