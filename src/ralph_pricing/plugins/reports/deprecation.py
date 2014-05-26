# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict, defaultdict
from decimal import Decimal as D

from django.db.models import Count, Max, Sum
from django.utils.translation import ugettext_lazy as _

from ralph_pricing.models import DailyDevice
from ralph_pricing.plugins.base import register
from ralph_pricing.plugins.reports.usage import UsageBasePlugin


logger = logging.getLogger(__name__)


@register(chain='reports')
class Deprecation(UsageBasePlugin):
    def get_assets_count_and_cost(
        self,
        start,
        end,
        ventures,
        group_by='pricing_venture',
    ):
        """
        Returns sum of devices price and daily_costs for every venture in given
        time period

        :param datatime start: Begin of time interval for deprecation
        :param datatime end: End of time interval for deprecation
        :param list ventures: List of ventures
        :returns dict: query with selected devices for give venture
        :rtype dict:
        """
        assets_report_query = DailyDevice.objects.filter(
            pricing_device__is_virtual=False,
            date__gte=start,
            date__lte=end,
            pricing_venture__in=ventures,
        )

        return assets_report_query.values(group_by).annotate(
            assets_cost=Sum('daily_cost')
        ).annotate(
            assets_count=Count('id')
        ).order_by(
            group_by
        )

    def total_cost(self, start, end, ventures, **kwargs):
        assets_report_query = DailyDevice.objects.filter(
            date__gte=start,
            date__lte=end,
            pricing_venture__in=ventures,
        ).aggregate(assets_cost=Sum('daily_cost'))
        return D(assets_report_query['assets_cost'] or 0)

    def costs(self, **kwargs):
        """
        Return usages and costs for given ventures. Format of
        returned data must looks like:

        usages = {
            'venture_id': {
                'field_name': value,
                ...
            },
            ...
        }

        :returns dict: usages and costs
        """
        logger.debug("Get deprecation usage")
        # TODO: calc blades
        report_days = (kwargs['end'] - kwargs['start']).days + 1
        assets_count_and_cost = self.get_assets_count_and_cost(
            kwargs['start'],
            kwargs['end'],
            kwargs['ventures'],
        )

        usages = {}
        for asset in assets_count_and_cost:
            usages[asset['pricing_venture']] = {
                'assets_count': asset['assets_count'] / report_days,
                'assets_cost': asset['assets_cost'],
            }
        return usages

    def costs_per_device(self, start, end, ventures, **kwargs):
        """
        Return usages and costs for devices in venture. Format of
        returned data must looks like:

        usages = {
            'device_id': {
                'field_name': value,
                ...
            },
            ...
        }

        :returns dict: usages and costs
        """
        logger.debug("Get deprecation of devices")
        report_days = (end - start).days + 1
        assets_count_and_cost = self.get_assets_count_and_cost(
            start,
            end,
            ventures,
            group_by='pricing_device'
        ).annotate(
            is_deprecated_sum=Sum('is_deprecated')
        ).annotate(
            deprecation_rate=Max('deprecation_rate')
        )

        usages = {}
        for asset in assets_count_and_cost:
            # if there is not is_deprecated=True record, then asset is
            # definitely not deprecated
            if asset['is_deprecated_sum'] == 0:
                deprecation_status = _('No')
            # if all records have is_deprecated=True, then asset is deprecated
            elif asset['is_deprecated_sum'] == asset['assets_count']:
                deprecation_status = _('Yes')
            # if asset has some records with is_deprecated=True and some with
            # is_deprecated=False, then it's partially deprecated
            else:
                deprecation_status = _('Partially')

            usages[asset['pricing_device']] = {
                'assets_count': asset['assets_count'] / report_days,
                'assets_cost': asset['assets_cost'],
                'is_deprecated': deprecation_status,
                'deprecation_rate': asset['deprecation_rate']
            }
        return usages

    def dailyusages(self, start, end, ventures, **kwargs):
        """
        Returns count of devices per venture per day. Result format:
            result = {
                day: {
                    venture: value,
                    veture: value,
                    ...
                },
                ...
            }

        :rtype: dict
        """
        logger.debug("Getting deprecation daily usages per venture")
        result = defaultdict(dict)
        dailyusages = DailyDevice.objects.filter(
            pricing_venture__in=ventures,
            date__gte=start,
            date__lte=end,
        ).values(
            'date',
            'pricing_venture',
        ).annotate(
            devices=Count('id')
        )
        for d in dailyusages:
            result[d['date']][d['pricing_venture']] = d['devices']
        return result

    def schema(self, **kwargs):
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
        """
        logger.debug("Get deprecation schema")
        schema = OrderedDict()
        schema['assets_count'] = {
            'name': _("Assets count"),
            'rounding': 3,
        }
        schema['assets_cost'] = {
            'name': _("Assets cost"),
            'currency': True,
            'total_cost': True,
        }
        return schema

    def schema_devices(self, **kwargs):
        """
        Build schema for deprecation columns of devices.
        """
        schema = self.schema(**kwargs)
        schema['deprecation_rate'] = {
            'name': _('Deprecation rate'),
            'rounding': 1,
        }
        schema['is_deprecated'] = {
            'name': _('Deprecated'),
        }
        return schema

    def dailyusages_header(self, usage_type):
        """
        Header for assets count column on dailyusages report.
        """
        return _('Assets count')
