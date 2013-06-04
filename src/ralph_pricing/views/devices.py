# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from ralph_pricing.forms import DateRangeVentureForm
from ralph_pricing.menus import ventures_menu
from ralph_pricing.models import (
    DailyDevice,
    DailyPart,
    Device,
    Venture,
)

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
                '',
            ]
            data.append(row)
        for usage in venture.get_daily_usage(start,end):
            row = [
                '{} (Venture Usage)'.format(usage.type),
                '',
                '',
                '',
                '',
                currency(usage.value),
                '',
                '',
                '',
                '',
                '',
            ]
            data.append(row)
        for i, device in enumerate(devices):
            count, price, cost = venture.get_assets_count_price_cost(
                start,
                end,
                device_id=device.id,
            )
            parts = device.get_daily_parts(start, end)
            usages = device.get_daily_usage(start, end)
            cols = len(parts) if len(parts) > len(usages) else len(usages)
            for col in range(cols):
                try:
                    part_name = parts[col].get('name', '')
                    part_price = currency(parts[col].get('price', 0))
                    part_cost = currency(parts[col].get('cost', 0))
                except IndexError:
                    part_name, part_price, part_cost = '', '', ''
                try:
                    usage_name = usages[col].get('name', '')
                    usage_value = currency(usages[col].get('value', ''))
                except IndexError:
                    usage_name, usage_value = '', ''
                status = device.get_deprecated_status(start, end, venture)
                row = [
                    device.name if col == 0 else '',
                    device.sn if col == 0 else '',
                    device.barcode if col == 0 else '',
                    status if col == 0 else '',
                    currency(price) if col == 0 else '',
                    currency(cost) if col == 0 else '',
                    part_name,
                    part_price,
                    part_cost,
                    usage_name,
                    usage_value,
                ]
                data.append(row)
            progress = (100 * i) // total_count
            yield progress, data

    @staticmethod
    def get_header(**kwargs):
        header = [
            _("Device"),
            _("SN"),
            _("Barcode"),
            _("Is deprecation"),
            _("Asset price"),
            _("Asset cost"),
            _("Component name"),
            _("Component price"),
            _("Component cost"),
            _("Usage name"),
            _("Usage value"),
        ]
        return header
