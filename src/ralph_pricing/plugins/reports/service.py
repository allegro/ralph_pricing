# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict, OrderedDict
from decimal import Decimal as D

from django.utils.translation import ugettext_lazy as _

from ralph.util import plugin as plugin_runner

from ralph_pricing.plugins.base import register
from ralph_pricing.plugins.reports.base import BaseReportPlugin


logger = logging.getLogger(__name__)


class ServiceBasePlugin(BaseReportPlugin):
    """
    Base plugin for all services in report. Provides 3 main methods:
    * usages - service resources usages count and cost per venture
    * schema - schema (output format) of usages method
    * total_cost - returns total cost of service
    """
    distribute_count_key_tmpl = 'sut_{0}_count'
    distribute_cost_key_tmpl = 'sut_{0}_cost'

    def _get_usage_type_cost(self, start, end, usage_type, forecast, ventures):
        """
        Calculates total cost of usage of given type for specified ventures in
        period of time (between start and end), using real or forecast
        price/cost.
        """
        try:
            return plugin_runner.run(
                'reports',
                usage_type.get_plugin_name(),
                type='total_cost',
                start=start,
                end=end,
                usage_type=usage_type,
                forecast=forecast,
                ventures=ventures,
            )
        except (KeyError, AttributeError):
            logger.warning(
                'Invalid call for {0} total cost'.format(usage_type.name)
            )
            return D(0)

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
        real or forecast prices/costs. Total cost is calculated for period of
        time (between start and end) and for specified ventures.
        """
        total_cost = D(0)
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

    def _get_dependent_services_cost(
        self,
        start,
        end,
        service,
        forecast,
        ventures
    ):
        """
        Calculates cost of dependent services used by service.
        """
        dependent_costs = 0
        for dependent in service.dependency.exclude(id=service.id):
            try:
                dependent_schema = plugin_runner.run(
                    'reports',
                    dependent.get_plugin_name(),
                    service=dependent,
                    type='schema'
                )
                # find total cost column in schema
                total_cost_key = None
                for column_key, column_description in dependent_schema.items():
                    if column_description.get('total_cost'):
                        total_cost_key = column_key
                        break

                if total_cost_key:
                    # do report of usages for service (and it's ventures)
                    dependent_usages = plugin_runner.run(
                        'reports',
                        dependent.get_plugin_name(),
                        service=dependent,
                        ventures=ventures,
                        start=start,
                        end=end,
                        forecast=forecast,
                        type='costs',
                    )

                    for venture, venture_data in dependent_usages.items():
                        dependent_costs += venture_data[total_cost_key]
                else:
                    logger.warning(
                        'No total cost column for {0} dependency'.format(
                            dependent.name
                        )
                    )
            except (KeyError, AttributeError):
                logger.warning('Invalid plugin for {0} dependency'.format(
                    dependent.name
                ))
        return dependent_costs

    def _get_service_extra_cost(
        self,
        start,
        end,
        ventures,
    ):
        """
        Calculates total cost of extra costs for given service.

        :param datatime start: Begin of time interval
        :param datatime end: End of time interval
        :param list ventures: List of ventures
        :returns decimal: price
        :rtype decimal:
        """
        try:
            return plugin_runner.run(
                'reports',
                'extra_cost_plugin',
                type='total_cost',
                start=start,
                end=end,
                ventures=ventures,
            )
        except (KeyError, AttributeError):
            logger.warning('Invalid call for total extra cost')
            return D(0)

    def _get_date_ranges_percentage(self, start, end, service):
        """
        Returns list of minimum date ranges that have different percentage
        division in given service.

        :returns: dict of date ranges and it's percentage division. Key in dict
            is tuple: (start, end), value is dict (key: usage type id, value:
            percent)
        :rtype dict:
        """
        usage_types = service.serviceusagetypes_set.filter(
            start__lte=end,
            end__gte=start,
        )
        dates = defaultdict(lambda: defaultdict(list))
        for usage_type in usage_types:
            dates[max(usage_type.start, start)]['start'].append(usage_type)
            dates[min(usage_type.end, end)]['end'].append(usage_type)

        result = {}
        current_percentage = {}
        current_start = None

        # iterate through dict items sorted by key (date)
        for date, usage_types in sorted(dates.items(), key=lambda k: k[0]):
            if usage_types['start']:
                current_start = date
            for sut in usage_types['start']:
                current_percentage[sut.usage_type.id] = sut.percent

            if usage_types['end']:
                result[(current_start, date)] = current_percentage.copy()
            for usage_type in usage_types['end']:
                del current_percentage[usage_type.usage_type.id]
        return result

    def total_cost(self, start, end, service, forecast, ventures):
        """
        Calculates total cost of service (in period of time), assuming, that
        ventures are service ventures.

        Total cost is sum of cost of base usage types usages, all dependent
        and extra costs.
        services costs (for specified ventures).

        :param datatime start: Begin of time interval
        :param datatime end: End of time interval
        :param list ventures: List of service ventures
        :returns decimal: total cost of service
        :rtype decimal:
        """
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
        total_cost += self._get_service_extra_cost(
            start,
            end,
            ventures,
        )
        return total_cost

    def costs(self, service, start, end, ventures, forecast=False, **kwargs):
        """
        Calculates usages and costs of service usages per venture.

        Main steps:
        1) calculation of percentage division in date ranges
        2) for each daterange with different percentage division:
            2.1) calculation of service total cost in daterange
            2.2) distribution of that cost to ventures, basing on venture usage
                 of service and using percentage division
            2.3) sum ventures costs of service usage types (eventually total
                 cost)
        """
        logger.debug("Calculating report for service {0}".format(service))
        date_ranges_percentage = self._get_date_ranges_percentage(
            start,
            end,
            service,
        )
        service_symbol = "{0}_service_cost".format(service.id)
        schema_usage_types = [
            a.usage_type for a in service.serviceusagetypes_set.all()
        ]
        usage_types = sorted(set(schema_usage_types), key=lambda a: a.name)
        total_cost_column = len(usage_types) > 1

        result = defaultdict(lambda: defaultdict(int))
        for date_range, percentage in date_ranges_percentage.items():
            dstart, dend = date_range[0], date_range[1]
            service_cost = self.total_cost(
                dstart,
                dend,
                service,
                forecast,
                ventures=service.venture_set.all(),
            )
            # distribute total cost between every venture proportionally to
            # service usages
            service_report_in_daterange = self._distribute_costs(
                start,
                end,
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
        """
        Returns service usages schema depending on schema usage types.
        """
        schema_usage_types = [
            a.usage_type for a in service.serviceusagetypes_set.all()
        ]
        usage_types = sorted(set(schema_usage_types), key=lambda a: a.name)
        schema = OrderedDict()
        for usage_type in usage_types:
            symbol = usage_type.id
            usage_type_count_symbol = 'sut_{0}_count'.format(symbol)
            usage_type_cost_symbol = 'sut_{0}_cost'.format(symbol)

            schema[usage_type_count_symbol] = {
                'name': _("{0} count".format(usage_type.name)),
            }
            schema[usage_type_cost_symbol] = {
                'name': _("{0} cost".format(usage_type.name)),
                'currency': True,
                'total_cost': len(usage_types) == 1,
            }
        # if there is more than one schema usage type -> add total service
        # usage column
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
    """
    Base Service Plugin as ralph plugin. Splitting it into two classes gives
    ability to inherit from ServiceBasePlugin.
    """
    pass
