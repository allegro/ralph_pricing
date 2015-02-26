# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict, defaultdict
from datetime import timedelta

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.models import HistoricalService, ServiceEnvironment
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.report.base import BaseReportPlugin

logger = logging.getLogger(__name__)


@register(chain='scrooge_reports')
class Information(BaseReportPlugin):
    def costs(self, start, end, service_environments=None, *args, **kwargs):
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
        info = {}

        # historical business lines
        day_after_end = end + timedelta(days=1)
        # get records that are active (even partially) between
        # <start date 00:00:00> and <end date 23:59:59>
        # there are 4 possible cases of record activity:
        #         start                 end
        #           |____________________|
        # 1)    |____________________________|
        # 2)    |_______|
        # 3)           |_________|
        # 4)                        |________|
        # in cases 1 and 2 start has to be between active_from and active_end
        # in cases 3 and 4 active_from has to be between start and end
        if not service_environments:
            service_environments = ServiceEnvironment.objects.all()
        services_history = HistoricalService.objects.filter(
            (Q(active_from__lte=start) & Q(active_to__gte=start)) |  # 1-2
            (Q(active_from__gte=start) & Q(active_from__lt=day_after_end)),
            id__in=service_environments.values_list(
                'service',
                flat=True
            ).distinct(),
        ).select_related('business_line', 'profit_center').order_by(
            'history_id'
        )
        services = {}
        profit_centers = defaultdict(list)
        for service_history in services_history:
            services[service_history.id] = service_history.history_object
            profit_centers[service_history.id].append(
                service_history.profit_center
            )
        for service_environment in service_environments:
            info[service_environment.id] = {
                'id': service_environment.id,
                'service': service_environment.service.name,
                'environment': service_environment.environment.name,
                'profit_center': ' / '.join([
                    ' - '.join(
                        (pc.name, pc.description or '')
                    ) for pc in set(profit_centers[
                        service_environment.service.id
                    ])
                ]),
                'business_line': ' / '.join(set([
                    pc.business_line.name for pc in profit_centers[
                        service_environment.service.id
                    ]
                ])),
            }
        return info

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
        schema['id'] = {
            'name': _("ID"),
        }
        schema['service'] = {
            'name': _("Service"),
        }
        schema['environment'] = {
            'name': _("Environment"),
        }
        schema['profit_center'] = {
            'name': _("Profit center"),
        }
        schema['business_line'] = {
            'name': _("Business Line"),
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
