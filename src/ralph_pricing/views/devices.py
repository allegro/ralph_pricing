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
from ralph_pricing.models import DailyDevice
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
        ids = DailyDevice.objects.filter(
            date__gte=start,
            date__lte=end,
            pricing_venture=venture,
        ).values_list('pricing_device', flat=True).distinct()
        devices_ids = list(set(ids))
        total_count = len(devices_ids)
        for i, id in enumerate(devices_ids):
            device = DailyDevice.objects.filter(pricing_device=id)[0]
            row = [
                    device.name,
                    device.pricing_device.sn,
                    device.pricing_device.barcode,
                    device.is_deprecated,
                    currency(
                        device.pricing_device.get_device_price(
                            start,
                            end,
                            venture,
                        )
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
