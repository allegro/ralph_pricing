# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect

from ralph_pricing.app import Scrooge
from ralph_pricing.forms import ExtraCostFormSet
from ralph_pricing.menus import extra_costs_menu
from ralph_pricing.models import ExtraCostType
from ralph_pricing.views.base import Base


class ExtraCosts(Base):
    template_name = 'ralph_pricing/extra_costs.html'

    def __init__(self, *args, **kwargs):
        super(ExtraCosts, self).__init__(*args, **kwargs)
        self.formset = None
        self.extra_cost_type = None
        self.extra_cost_type_id = None

    def init_args(self):
        self.extra_cost_type_id = self.kwargs.get('extra_cost')
        if self.extra_cost_type_id is not None:
            self.extra_cost_type = get_object_or_404(
                ExtraCostType,
                id=self.extra_cost_type_id
            )

    def post(self, *args, **kwargs):
        self.init_args()
        if self.extra_cost_type:
            self.formset = ExtraCostFormSet(
                self.request.POST,
                queryset=self.extra_cost_type.extracost_set.all(),
            )
            if self.formset.is_valid():
                for form in self.formset.extra_forms:
                    if form.has_changed():
                        form.instance.type = self.extra_cost_type
                self.formset.save()
                messages.success(self.request, "Extra costs updated.")
                return HttpResponseRedirect(self.request.path)
            else:
                messages.error(self.request, "Please fix the errors.")
        return super(ExtraCosts, self).get(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.init_args()
        if self.extra_cost_type:
            self.formset = ExtraCostFormSet(
                queryset=self.extra_cost_type.extracost_set.all(),
            )
        return super(ExtraCosts, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ExtraCosts, self).get_context_data(**kwargs)
        context.update({
            'section': 'extra-costs',
            'sidebar_items': extra_costs_menu(
                '/{0}/extra-costs'.format(Scrooge.url_prefix),
                self.extra_cost_type_id
            ),
            'sidebar_selected': self.extra_cost_type_id,
            'formset': self.formset,
        })
        return context
