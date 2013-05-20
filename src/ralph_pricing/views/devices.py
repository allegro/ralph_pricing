# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect

from ralph_pricing.views.base import Base
from ralph_pricing.models import Venture
from ralph_pricing.menus import ventures_menu
from ralph_pricing.models import DailyDevice

class Devices(Base):
    template_name = 'ralph_pricing/devices.html'

    def __init__(self, *args, **kwargs):
        super(Devices, self).__init__(*args, **kwargs)
        self.formset = None
        self.venture = None
        self.venture_id = None
        self.devices = None

    def init_args(self):
        self.venture_id = self.kwargs.get('venture')
        if self.venture_id is not None:
            self.venture = get_object_or_404(Venture, id=self.venture_id)

    def get(self, *args, **kwargs):
        self.init_args()
        if self.venture_id:
            self.devices = get_list_or_404(
                DailyDevice,
                pricing_venture=self.venture_id
            )









        return super(Devices, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Devices, self).get_context_data(**kwargs)
        context.update({
            'section': 'devices',
            'sidebar_items': ventures_menu(
                '/pricing/devices',
                self.venture_id
            ),
            'sidebar_selected': self.venture_id,
            'formset': self.formset,
            'devices': self.devices,
        })
        return context
