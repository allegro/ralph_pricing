# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from ralph_scrooge.app import Scrooge
from ralph_scrooge.forms import UsagesFormSet
from ralph_scrooge.sidebar_menus import usages_menu
from ralph_scrooge.models import UsageType
from ralph_scrooge.views.base import Base


class UsageTypes(Base):
    template_name = 'ralph_scrooge/usage_types.html'
    submodule_name = 'usage-types'

    def __init__(self, *args, **kwargs):
        super(UsageTypes, self).__init__(*args, **kwargs)
        self.formset = None
        self.usage_type = None
        self.usage_type_id = None

    def init_args(self):
        self.usage_type_id = self.kwargs.get('usage_type_id')
        if self.usage_type_id is not None:
            self.usage_type = get_object_or_404(
                UsageType,
                pk=self.usage_type_id,
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
        return super(UsageTypes, self).get(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.init_args()
        if self.usage_type_id:
            self.formset = UsagesFormSet(
                queryset=self.usage_type.usageprice_set.order_by('start'),
            )
        return super(UsageTypes, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UsageTypes, self).get_context_data(**kwargs)

        if self.usage_type:
            by_warehouse = self.usage_type.by_warehouse
        else:
            by_warehouse = None

        by_cost = self.usage_type.by_cost if self.usage_type else None
        context.update({
            'sidebar_items': usages_menu(
                '/{0}/usage-types'.format(Scrooge.url_prefix),
                self.usage_type_id
            ),
            'sidebar_selected': self.usage_type_id,
            'by_cost': by_cost,
            'by_warehouse': by_warehouse,
            'formset': self.formset,
            'hidden': {
                'by_cost': ['price', 'forecast_price'],
                'not_by_cost': ['cost', 'forecast_cost'],
                'not_by_warehouse': ['warehouse'],
            }
        })
        return context
