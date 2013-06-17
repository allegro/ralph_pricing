# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools

from django.utils.translation import ugettext_lazy as _

from ralph_pricing.forms import DateRangeVentureForm
from ralph_pricing.models import DailyDevice, Device
from ralph_pricing.views.reports import Report, currency


class Devices(Report):
    template_name = 'ralph_pricing/devices.html'
    Form = DateRangeVentureForm
    section = 'devices'
    report_name = _('Devices Report')

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
        for extracost in venture.get_extracost_details(start, end):
            row = [
                '{} (Extra Cost)'.format(extracost.type.name),
                '',
                '',
                '{} - {}'.format(extracost.start, extracost.end),
                '',
                currency(extracost.price),
                '',
                '',
                '',
                '',
            ]
            data.append(row)
        for usage in venture.get_daily_usages(start, end):
            row = [
                '',
                '',
                usage['name'],
                '',
                '',
                '',
                '',
                currency(usage['price']),
                usage['count'],
            ]
            data.append(row)
        for i, device in enumerate(devices):
            count, price, cost = venture.get_assets_count_price_cost(
                start,
                end,
                device_id=device.id,
            )
            data.append([
                device.name,
                '',
                '',
                device.sn,
                device.barcode,
                device.get_deprecated_status(start, end, venture),
                currency(price),
                currency(cost),
                '',
            ])
            for part in device.get_daily_parts(start, end):
                data.append([
                    '',
                    part['name'],
                    '',
                    '',
                    '',
                    part.get('deprecation', ''),
                    currency(part['price']),
                    currency(part['cost']),
                    '',
                ])

            for usage in device.get_daily_usages(start, end):
                data.append([
                    '',
                    '',
                    usage['name'],
                    '',
                    '',
                    '',
                    '',
                    currency(usage['price']),
                    usage['count'],
                ])
            progress = (100 * i) // total_count
            yield progress, data

    @staticmethod
    def get_header(**kwargs):
        header = [
            _("Device"),
            _("Component name"),
            _("Usage name"),
            _("SN"),
            _("Barcode"),
            _("Deprecation"),
            _("Price"),
            _("Cost"),
            _("Usage count"),
        ]
        return header
