# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import math
from datetime import date, datetime, timedelta
from optparse import make_option

from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.management.commands._scrooge_base import ScroogeBaseCommand
from ralph_scrooge.models import (
    DailyCost,
    DailyUsage,
    PricingObjectModel,
    PRICING_OBJECT_TYPES,
    UsageType,
)
from ralph_scrooge.plugins.cost.collector import Collector
from ralph_scrooge.utils.common import memoize, normalize_decimal

logger = logging.getLogger(__name__)


class Command(ScroogeBaseCommand):
    """
    Generate report with tenants instances and cost of particular flavors
    (if tenants are billed based on ceilometer) or simple usages.
    """
    option_list = ScroogeBaseCommand.option_list + (
        make_option(
            '-s', '--start',
            dest='start',
            default=None,
            help=_('Date from which generate report for'),
        ),
        make_option(
            '--end',
            dest='end',
            default=None,
            help=_('Date to which generate report for'),
        ),
        make_option(
            '--forecast',
            dest='forecast',
            default=False,
            action='store_true',
            help=_('Set to use forecast prices and costs'),
        ),
        make_option(
            '-p',
            dest='plugins',
            action='append',
            type='str',
            default=[],
            help=_('Plugins to calculate missing costs'),
        ),
        make_option(
            '-t',
            dest='type',
            type='choice',
            choices=['simple_usage', 'ceilometer'],
            default='ceilometer',
            help=_('Type of OpenStack usage'),
        ),
    )

    def __init__(self, *args, **kwargs):
        self.type = 'ceilometer'
        return super(Command, self).__init__(*args, **kwargs)

    @property
    def HEADERS(self):
        base_result = [
            'Service',
            'Environment',
            'Model',
            'OpenStack Tenant ID',
            'OpenStack Tenant',
        ]
        additional = []
        if self.type == 'ceilometer':
            additional = [
                'Flavor',
                'Total usage',
                'Instances (avg)',
                'Hour price',
                'Cost',
            ]
        elif self.type == 'simple_usage':
            additional = [
                'Resource',
                'Total usage',
                'Avg usage per day',
                'Unit price',
                'Cost',
            ]
        return base_result + additional

    def _calculate_missing_dates(self, start, end, forecast, plugins):
        """
        Calculate costs for dates on which costs were not previously calculated
        """
        collector = Collector()
        dates_to_calculate = collector._get_dates(start, end, forecast, False)
        plugins = [pl for pl in collector.get_plugins() if pl.name in plugins]
        for day in dates_to_calculate:
            collector.process(day, forecast, plugins)

    @memoize(skip_first=True)
    def _get_usage_prices(self, type_id, start, end, forecast):
        """
        Return usage type and it's prices between start and end.
        """
        usage_type = UsageType.objects.get(pk=type_id)
        prices = []
        for price in usage_type.usageprice_set.filter(
            start__lte=end,
            end__gte=start,
        ).order_by('start'):
            prices.append(price.forecast_price if forecast else price.price)
        return usage_type, ' / '.join(
            map(lambda x: unicode(normalize_decimal(x)), prices)
        )

    @memoize(skip_first=True)
    def _get_model(self, model_id):
        return PricingObjectModel.objects.get(pk=model_id)

    def _parse_date(self, date_):
        """
        Parse given date or returns default (yesterday).
        """
        if date_:
            return datetime.strptime(date_, '%Y-%m-%d').date()
        else:
            return date.today() - timedelta(days=1)

    def get_costs(self, start, end, forecast, filters):
        """
        Return tenants costs between start and end.
        """
        days = (end - start).days + 1
        costs = DailyCost.objects_tree.filter(
            date__gte=start,
            date__lte=end,
            pricing_object__type=PRICING_OBJECT_TYPES.TENANT,
            **filters
        ).filter(
            **{'forecast': True if forecast else False}
        ).values_list(
            'service_environment__service__name',
            'service_environment__environment__name',
            'pricing_object__model__name',
            'pricing_object_id',
            'pricing_object__name',
            'type_id'
        ).annotate(
            usage=Sum('value'),
            cost=Sum('cost')
        ).order_by('pricing_object__name', 'type__id')

        result = []
        for cost in costs:
            tmp = list(cost[:5])
            usage_type, prices = self._get_usage_prices(
                cost[5],
                start,
                end,
                forecast
            )
            total_usage = cost[-2]
            if self.type == 'ceilometer':
                # get average instances in one day
                avg_day_usage = math.ceil(total_usage / (24.0 * days))
            else:
                avg_day_usage = math.ceil(total_usage / float(days))
            tmp.extend([
                usage_type.name,
                total_usage,
                avg_day_usage,
                prices,
                cost[-1],
            ])
            result.append(tmp)
        return result

    def get_usages_without_cost(self, start, end, forecast, filters):
        """
        Return tenants usages (for which costs were not calculated, ex.
        because there is no price defined).
        """
        days = (end - start).days + 1
        cost_types = DailyCost.objects_tree.filter(
            date__gte=start,
            date__lte=end,
            pricing_object__type=PRICING_OBJECT_TYPES.TENANT,
            **filters
        ).filter(
            **{'forecast': True if forecast else False}
        ).values_list('type_id', flat=True).distinct()
        usages = DailyUsage.objects.filter(
            date__gte=start,
            date__lte=end,
            daily_pricing_object__pricing_object__type=(
                PRICING_OBJECT_TYPES.TENANT
            ),
            **filters
        ).exclude(
            type_id__in=cost_types
        ).values_list(
            'service_environment__service__name',
            'service_environment__environment__name',
            'daily_pricing_object__pricing_object__model__name',
            'daily_pricing_object__pricing_object_id',
            'daily_pricing_object__pricing_object__name',
            'type__name',
        ).annotate(
            usage=Sum('value'),
        ).order_by('service_environment__service__name', 'type__name')
        result = []
        for usage in usages:
            u = list(usage)
            # get average instances in one day
            if self.type == 'ceilometer':
                avg_day_usage = math.ceil(u[-1] / (24.0 * days))
            else:
                avg_day_usage = math.ceil(u[-1] / float(days))
            result.append(u + [avg_day_usage] + ['-'] * 2)
        return result

    def get_data(self, start, end, forecast, plugins, *args, **options):
        start = self._parse_date(start)
        end = self._parse_date(end)

        self._calculate_missing_dates(start, end, forecast, plugins)
        filters = {}
        if self.type == 'ceilometer':
            filters = {'type__name__startswith': 'openstack.'}
        elif self.type == 'simple_usage':
            filters = {'type__name__startswith': 'OpenStack '}
        costs = self.get_costs(start, end, forecast, filters)
        usages = self.get_usages_without_cost(start, end, forecast, filters)
        return costs + usages

    def handle(self, type, *args, **options):
        self.type = type
        return super(Command, self).handle(*args, **options)
