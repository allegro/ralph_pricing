# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.translation import ugettext_lazy as _

from ralph_pricing.forms import DateRangeVentureForm
from ralph_pricing.menus import ventures_menu
from ralph_pricing.models import DailyDevice, Device, DailyPart
from ralph_pricing.models import Venture
from ralph_pricing.views.reports import Report, currency


class Devices(Report):
    template_name = 'ralph_pricing/devices.html'
    Form = DateRangeVentureForm
    section = 'devices'

    @staticmethod
    def get_data(start, end, venture, **kwargs):
        if not venture:
            return
        devices_ids = DailyDevice.objects.filter(
            date__gte=start,
            date__lte=end,
            pricing_venture=venture,
        ).values_list('pricing_device_id', flat=True).distinct()
        total_count = len(devices_ids)
        devices = Device.objects.filter(id__in=devices_ids)
        data = []
        for i, device in enumerate(devices):
            row = [
                device.name,
                device.sn,
                device.barcode,
                device.get_deprecated_status(start, end, venture),
                currency(device.get_device_price(start, end, venture)),
                device.get_daily_parts(start, end),
                device.get_daily_usage(start, end)
            ]
            progress = (100 * i) // total_count
            data.append(row)
            yield progress, data

    @staticmethod
    def get_header(**kwargs):
        header = [
            _("Device"),
            _("SN"),
            _("Barcode"),
            _("Is deprecation"),
            _("Quoted price"),
            _("Components"),
            _("Usages"),
        ]
        return header
