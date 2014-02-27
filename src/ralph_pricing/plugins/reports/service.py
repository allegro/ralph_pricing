# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict, OrderedDict
from decimal import Decimal as D

from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from lck.cache import memoize

from ralph.util import plugin as plugin_runner
from ralph_pricing.models import DailyUsage, UsageType
from ralph_pricing.plugins.base import register
from ralph_pricing.plugins.reports.base import BaseReportPlugin

logger = logging.getLogger(__name__)


class ServiceBasePlugin(BaseReportPlugin):
    def _get_service_base_usage_types_cost(
        self,
        start,
        end,
        service,
        forecast,
        ventures,
    ):
        """
        Calculates total cost of base types usages for given service, using
        real or forecast prices/costs.
        """
        total_cost = 0
        for usage_type in service.base_usage_types.all():
            usage_type_total_cost = self._get_usage_type_cost(
                start,
                end,
                usage_type,
                forecast,
                ventures,
            )
            total_cost += usage_type_total_cost
        return total_cost

    def _get_dependent_services_cost(self, start, end, service, forecast, ventures):
        dependent_costs = 0
        for dependent in service.dependency.all():
            try:
                dependent_usages = plugin_runner.run(
                    'reports',
                    dependent.get_plugin_name(),
                    service=dependent,
                    ventures=ventures,
                    start=start,
                    end=end,
                    forecast=forecast,
                    type='usages',
                )
                dependent_schema = plugin_runner.run(
                    'reports',
                    dependent.get_plugin_name(),
                    service=dependent,
                    type='schema'
                )

                total_cost_key = None
                for column_key, column_description in dependent_schema.items():
                    if column_description.get('total_cost'):
                        total_cost_key = column_key
                        break
                if total_cost_key:
                    for venture, venture_data in dependent_usages.items():
                        dependent_costs += venture_data[total_cost_key]
            except (KeyError, AttributeError):
                logger.warning('Invalid plugin for {0} dependency'.format(dependent.name))
        return dependent_costs

    def _get_date_ranges_percentage(self, start, end, service):
        """
        Returns list of minimum date ranges that have different percentage
        division in given service.
        """
        usage_types = service.serviceusagetypes_set.filter(
            start__lte=end,
            end__gte=start,
        )
        dates = set()
        for ut in usage_types:
            dates.add(max(ut.start, start))
            dates.add(min(ut.end, end))

        result = {}
        dates = sorted(list(dates))
        for i in range(0, len(dates)-1, 2):
            dstart, dend = dates[i], dates[i+1]
            usage_types = service.serviceusagetypes_set.filter(
                start__lte=dend,
                end__gte=dstart,
            ).values('usage_type', 'percent').order_by('usage_type')
            result[(dstart, dend)] = list(usage_types)
        return result

    def _distribute_costs(
        self,
        start,
        end,
        service,
        ventures,
        cost,
        percentage,
    ):
        """
        Distributes some cost between all ventures proportionally to usages of
        service resources.
        """
        # first level: venture
        # second level: usage type key (count or cost)
        result = defaultdict(lambda: defaultdict(int))

        for percent in percentage:
            usage_type = UsageType.objects.get(id=percent['usage_type'])
            usages_per_venture = self._get_usages_in_period_per_venture(
                start,
                end,
                usage_type,
                ventures=ventures,
            )
            total_usage = self._get_total_usage_in_period(
                start,
                end,
                usage_type
            )
            cost_part = D(percent['percent']) * cost / D(100)

            usage_type_count_symbol = '{0}_count'.format(percent['usage_type'])
            usage_type_cost_symbol = '{0}_cost'.format(percent['usage_type'])

            for v in usages_per_venture:
                venture = v['pricing_venture']
                result[venture][usage_type_count_symbol] = v['usage']
                result[venture][usage_type_cost_symbol] = D(v['usage']) / D(total_usage) \
                    * cost_part
        return result

    def total_cost(self, start, end, service, forecast, ventures):
        # total cost of base usage types for ventures providing this service
        total_cost = self._get_service_base_usage_types_cost(
            start,
            end,
            service,
            forecast,
            ventures=ventures,
        )
        total_cost += self._get_dependent_services_cost(
            start,
            end,
            service,
            forecast,
            ventures=ventures,
        )
        return total_cost

    def usages(self, service, start, end, ventures, forecast=False, **kwargs):
        logger.debug("Calculating report for service {0}".format(service))
        date_ranges_percentage = self._get_date_ranges_percentage(
            start,
            end,
            service,
        )
        service_symbol = "{0}_service_cost".format(service.id)
        usage_types = sorted(set([a.usage_type for a in service.serviceusagetypes_set.all()]), key=lambda a: a.name)
        total_cost_column = len(usage_types) > 1

        result = defaultdict(lambda: defaultdict(int))
        for date_range, percentage in date_ranges_percentage.items():
            dstart, dend = date_range[0], date_range[1]
            # if service.name == 'Hamster':
            #     import ipdb; ipdb.set_trace()
            service_cost = self.total_cost(
                dstart,
                dend,
                service,
                forecast,
                ventures=service.venture_set.all(),
            )
            # distribute total cost between every venture proportionally to service
            # usages
            service_report_in_daterange = self._distribute_costs(
                start,
                end,
                service,
                ventures,
                service_cost,
                percentage
            )
            for venture, venture_data in service_report_in_daterange.items():
                for key, value in venture_data.items():
                    result[venture][key] += value
                    if total_cost_column and key.endswith('cost'):
                        result[venture][service_symbol] += value
        return result

    def schema(self, service):
        usage_types = sorted(set([a.usage_type for a in service.serviceusagetypes_set.all()]), key=lambda a: a.name)
        schema = OrderedDict()
        for ut in usage_types:
            symbol = ut.id
            usage_type_count_symbol = '{0}_count'.format(symbol)
            usage_type_cost_symbol = '{0}_cost'.format(symbol)

            schema[usage_type_count_symbol] = {
                'name': _("{0} count".format(ut.name)),
            }
            schema[usage_type_cost_symbol] = {
                'name': _("{0} cost".format(ut.name)),
                'currency': True,
                'total_cost': len(usage_types) == 1,
            }
        if len(usage_types) > 1:
            service_symbol = "{0}_service_cost".format(service.id)
            schema[service_symbol] = {
                'name': _("{0} cost".format(service.name)),
                'currency': True,
                'total_cost': True,
            }

        return schema


@register(chain='reports')
class ServicePlugin(ServiceBasePlugin):
    pass
