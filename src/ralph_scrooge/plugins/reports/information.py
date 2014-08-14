# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.reports.base import BaseReportPlugin

logger = logging.getLogger(__name__)


@register(chain='scrooge_reports')
class Information(BaseReportPlugin):
    def costs(self, service_environments, *args, **kwargs):
        """
        Return information about given ventures

        usages = {
            'venture_id': {
                'field_name': value,
                ...
            },
            ...
        }

        :returns dict: information about ventures
        :rtype dict:
        """
        logger.debug("Get information usage")
        usages = {}
        for service_environment in service_environments:
            usages[service_environment.id] = {
                'service_id': service_environment.service.ci_uid,
                'service': service_environment.service.name,
                'environment': service_environment.environment.name,
            }
        return usages

    def costs_per_device(self, start, end, ventures, *args, **kwargs):
        """
        Return information about devices in given venture. Devies are filtered
        to match only those, who have any DailyDevice record in period of time.

        usages = {
            'device_id': {
                'field_name': value,
                ...
            },
            ...
        }

        :returns dict: information about devices in venture
        :rtype dict:
        """
        logger.debug("Get devices information")
        # devices = Device.objects.filter(
        #     dailydevice__date__gte=start,
        #     dailydevice__date__lte=end,
        #     dailydevice__pricing_venture__in=ventures,
        # ).distinct().values('id', 'asset_id', 'name', 'sn', 'barcode')
        # return dict(((device['id'], device) for device in devices))
        return {}

    def schema(self, *args, **kwargs):
        """
        Build schema for this usage. Format of schema looks like:

        schema = {
            'field_name': {
                'name': 'Verbous name',
                'next_option': value,
                ...
            },
            ...
        }

        :returns dict: schema for usage
        :rtype dict:
        """
        logger.debug("Get information schema")
        schema = OrderedDict()
        schema['service_id'] = {
            'name': _("ID"),
        }
        schema['service'] = {
            'name': _("Service"),
        }
        schema['environment'] = {
            'name': _("Environment"),
        }
        return schema

    def schema_devices(self, *args, **kwargs):
        """
        Build schema for devices information. Format is the same as in `schema`

        :returns dict: schema for devices information
        :rtype dict:
        """
        logger.debug("Get devices information schema")
        schema = OrderedDict()
        schema['barcode'] = {
            'name': _('Barcode'),
        }
        schema['sn'] = {
            'name': _('SN'),
        }
        schema['name'] = {
            'name': _('Device name'),
        }
        return schema

    def total_cost(self, *args, **kwargs):
        raise NotImplementedError()
