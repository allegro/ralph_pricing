# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect

from django.utils.translation import ugettext_lazy as _

from ralph_pricing.views.reports import Report, currency
from ralph_pricing.models import Venture
from ralph_pricing.menus import ventures_menu
from ralph_pricing.models import DailyDevice
from ralph_pricing.forms import DateRangeVentureForm


class Devices(Report):
    template_name = 'ralph_pricing/devices.html'
    Form = DateRangeVentureForm
    section = 'devices'

    @staticmethod
    def get_data(start, end, venture, **kwargs):
        data = []
        if venture:
            devices = DailyDevice.objects.filter(pricing_venture=venture)
            total_count = devices.count()
            for i, device in enumerate(devices):
                row = [
                        device.name,
                        device.pricing_device.sn,
                        device.pricing_device.barcode,
                        device.is_deprecated,
                        currency(
                            device.get_devices_price(start, end, venture)
                        ),
                    ]
                progress = (100 * i) // total_count
                yield progress, row

    @staticmethod
    def get_header(**kwargs):
        header = [
            _("Device"),
            _("SN"),
            _("Barcode"),
            _("Is deprecation"),
            _("Quoted price"),
            _("Components"),
        ]
        return header
