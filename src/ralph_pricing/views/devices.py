# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext_lazy as _

from ralph.util import plugin as plugin_runner
from ralph_pricing.forms import DeviceReportForm
from ralph_pricing.models import Device
from ralph_pricing.plugins import reports  # noqa
from ralph_pricing.plugins.reports.base import AttributeDict
from ralph_pricing.views.base_plugin_report import BasePluginReport

logger = logging.getLogger(__name__)


class Devices(BasePluginReport):
    """
    Devices raport class for building devices reports. Contains hard coded
    label for columns. This class is sent to a queue in order to generate
    report
    """
    template_name = 'ralph_pricing/devices.html'
    Form = DeviceReportForm
    section = 'devices'
    report_name = _('Devices Report')
    schema_name = 'schema_devices'

    @classmethod
    def get_plugins(cls):
        """
        Returns list of plugins to call
        """
        base_plugins = [
            AttributeDict(name='Information', plugin_name='information'),
        ]
        base_usage_types_plugins = cls._get_base_usage_types_plugins(
            filter_={'show_in_devices_report':  True}
        )
        regular_usage_types_plugins = cls._get_regular_usage_types_plugins(
            filter_={'show_in_devices_report': True}
        )
        plugins = (base_plugins + base_usage_types_plugins +
                   regular_usage_types_plugins)
        return plugins

    @classmethod
    def _get_ventures(self, venture, use_subventures=True):
        return [venture] + (
            list(venture.get_descendants()) if use_subventures else []
        )

    @classmethod
    def _get_devices(cls, start, end, ventures):
        """
        Returns devices for given venture. Valid devices are only ones that
        have some dailydevices with this venture between start and end.
        """
        return Device.objects.filter(
            dailydevice__date__gte=start,
            dailydevice__date__lte=end,
            dailydevice__pricing_venture__in=ventures,
            is_virtual=False,
        ).distinct().order_by('name')

    @classmethod
    def _get_report_data(cls, start, end, ventures, forecast, devices):
        """
        Use plugins to get usages data per device for given venture. Each
        plugin has to return value in following format:

        data_from_plugin = {
            'device_id': {
                'field1_name': value,
                'field2_name': value,
                ...
            },
            ...
        }

        :param date start: Start of date interval for report
        :param date end: End of date interval for report
        :param boolean forecast: Forecast prices or real
        :param Venture venture: Venture to generate report for
        :param list devices: List of devices to generate report for
        :returns dict: Complete report data for all ventures
        :rtype dict:
        """
        logger.debug("Getting devices report data")
        data = {device.id: {} for device in devices}
        for plugin in cls.get_plugins():
            try:
                plugin_report = plugin_runner.run(
                    'reports',
                    plugin.plugin_name,
                    ventures=ventures,
                    start=start,
                    end=end,
                    forecast=forecast,
                    type='costs_per_device',
                    **plugin.get('plugin_kwargs', {})
                )
                for device_id, device_usage in plugin_report.iteritems():
                    if device_id in data:
                        data[device_id].update(device_usage)
            except KeyError:
                logger.warning(
                    "Usage {0} has no plugin connected".format(plugin.name)
                )
            except Exception as e:
                logger.exception("Report generate error: {0}".format(e))
        return data

    @classmethod
    def get_data(
        cls,
        start,
        end,
        venture,
        forecast=False,
        use_subventures=True,
        **kwargs
    ):
        """
        Main method. Create a full report for devices in venture. Process of
        creating report consists of two parts. First of them is collecting all
        required data from plugins. Second step is preparing data to render in
        html report.

        :returns tuple: percent of progress and report data
        :rtype tuple:
        """
        logger.info("Generating report from {0} to {1}".format(start, end))
        ventures = cls._get_ventures(venture, use_subventures)
        devices = cls._get_devices(start, end, ventures)
        data = cls._get_report_data(
            start,
            end,
            ventures,
            forecast,
            devices
        )
        yield 100, cls._prepare_final_report(data, devices)
