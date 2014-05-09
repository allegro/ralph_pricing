# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict, defaultdict
from decimal import Decimal as D

from django.db.models import Sum, Count
from django.utils.translation import ugettext_lazy as _

from ralph_pricing.models import DailyDevice
from ralph_pricing.plugins.base import register
from ralph_pricing.plugins.reports.usage import UsageBasePlugin


logger = logging.getLogger(__name__)


@register(chain='reports')
class Deprecation(UsageBasePlugin):
    def get_assets_count_and_cost(self, start, end, ventures):
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

        return assets_report_query.values('pricing_venture')\
            .annotate(assets_price=Sum('price'))\
            .annotate(assets_cost=Sum('daily_cost'))\
            .annotate(assets_count=Count('id'))

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
        }
        schema['assets_cost'] = {
            'name': _("Assets cost"),
            'currency': True,
            'total_cost': True,
        }
        return schema

    def dailyusages_header(self, usage_type):
        """
        Header for assets count column on dailyusages report.
        """
        return _('Assets count')
