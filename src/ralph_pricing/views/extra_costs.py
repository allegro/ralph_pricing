# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect

from ralph_pricing.forms import ExtraCostFormSet
from ralph_pricing.menus import ventures_menu
from ralph_pricing.models import Venture
from ralph_pricing.views.base import Base


class ExtraCosts(Base):
    template_name = 'ralph_pricing/extra_costs.html'

    def __init__(self, *args, **kwargs):
        super(ExtraCosts, self).__init__(*args, **kwargs)
        self.formset = None
        self.venture = None
        self.venture_id = None

    def init_args(self):
        self.venture_id = self.kwargs.get('venture')
        if self.venture_id is not None:
            self.venture = get_object_or_404(Venture, id=self.venture_id)

    def post(self, *args, **kwargs):
        self.init_args()
        if self.venture:
            self.formset = ExtraCostFormSet(
                self.request.POST,
                queryset=self.venture.extracost_set.order_by('start', 'type'),
            )
            if self.formset.is_valid():
                for form in self.formset.extra_forms:
                    if form.has_changed():
                        form.instance.pricing_venture = self.venture
                self.formset.save()
                messages.success(self.request, "Extra costs updated.")
                return HttpResponseRedirect(self.request.path)
            else:
                messages.error(self.request, "Please fix the errors.")
        return super(ExtraCosts, self).get(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.init_args()
        if self.venture:
            self.formset = ExtraCostFormSet(
                queryset=self.venture.extracost_set.order_by('start', 'type'),
            )
        return super(ExtraCosts, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ExtraCosts, self).get_context_data(**kwargs)
        context.update({
            'section': 'extra-costs',
            'sidebar_items': ventures_menu(
                '/pricing/extra-costs',
                self.venture_id
            ),
            'sidebar_selected': self.venture_id,
            'formset': self.formset,
        })
        return context
