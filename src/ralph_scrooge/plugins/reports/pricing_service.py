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

from ralph_scrooge.models import Team, UsageType
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.reports.base import BaseReportPlugin


logger = logging.getLogger(__name__)


class PricingServiceBasePlugin(BaseReportPlugin):
    """
    Base plugin for all pricing services in report. Provides 3 main methods:
    * usages - service resources usages count and cost per service_environment
    * schema - schema (output format) of usages method
    * total_cost - returns total cost of service
    """
    distribute_count_key_base_tmpl = 'service_{}_sut_{{}}_count'
    distribute_cost_key_base_tmpl = 'service_{}_sut_{{}}_cost'

    def _get_usage_type_cost(self, start, end, usage_type, forecast, service_environments):
        """
        Calculates total cost of usage of given type for specified service_environments in
        period of time (between start and end), using real or forecast
        price/cost.
        """
        try:
            return plugin_runner.run(
                'scrooge_reports',
                usage_type.get_plugin_name(),
                type='total_cost',
                start=start,
                end=end,
                usage_type=usage_type,
                forecast=forecast,
                service_environments=service_environments,
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
        pricing_service,
        forecast,
        service_environments,
    ):
        """
        Calculates total cost of base types usages for given pricing_service, using
        real or forecast prices/costs. Total cost is calculated for period of
        time (between start and end) and for specified service_environments.
        """
        total_cost = D(0)
        for usage_type in UsageType.objects.filter(type='BU').exclude(
                id__in=pricing_service.excluded_base_usage_types.values_list(
                    'id',
                    flat=True
                )):
            usage_type_total_cost = self._get_usage_type_cost(
                start,
                end,
                usage_type,
                forecast,
                service_environments,
            )
            total_cost += usage_type_total_cost
        return total_cost

    def _get_service_regular_usage_types_cost(
        self,
        start,
        end,
        pricing_service,
        forecast,
        service_environments,
    ):
        """
        Calculates total cost of regular types usages for given pricing_service, using
        real or forecast prices/costs. Total cost is calculated for period of
        time (between start and end) and for specified service_environments.
        """
        total_cost = D(0)
        for usage_type in pricing_service.regular_usage_types.all():
            usage_type_total_cost = self._get_usage_type_cost(
                start,
                end,
                usage_type,
                forecast,
                service_environments,
            )
            total_cost += usage_type_total_cost
        return total_cost

    def _get_service_teams_cost(
        self,
        start,
        end,
        pricing_service,
        forecast,
        service_environments,
    ):
        """
        Calculates total cost of teams for given pricing service, using
        real or forecast prices/costs. Total cost is calculated for period of
        time (between start and end) and for specified service environments.
        """
        total_cost = D(0)
        for team in Team.objects.all():
            try:
                total_cost += plugin_runner.run(
                    'scrooge_reports',
                    'team',
                    type='total_cost',
                    start=start,
                    end=end,
                    team=team,
                    forecast=forecast,
                    service_environments=service_environments,
                )
            except (KeyError, AttributeError):
                logger.warning(
                    'Invalid call for {0} total cost'.format(team.name)
                )
        return total_cost

    def _get_dependent_services_cost(
        self,
        start,
        end,
        pricing_service,
        forecast,
        service_environments
    ):
        """
        Calculates cost of dependent services used by pricing_service.
        """
        total_cost = 0
        dependent_services = pricing_service.get_dependent_services(start, end)
        for dependent in dependent_services:
            try:
                total_cost += plugin_runner.run(
                    'scrooge_reports',
                    dependent.get_plugin_name(),
                    pricing_service=dependent,
                    type='total_cost',
                    start=start,
                    end=end,
                    forecast=forecast,
                    service_environments=service_environments,
                )
            except (KeyError, AttributeError):
                logger.warning(
                    'Invalid call for {0} total cost'.format(dependent.name)
                )
        return total_cost

    def _get_service_extra_cost(
        self,
        start,
        end,
        service_environments,
    ):
        """
        Calculates total cost of extra costs for given pricing_service.

        :param datatime start: Begin of time interval
        :param datatime end: End of time interval
        :param list service_environments: List of service_environments
        :returns decimal: price
        :rtype decimal:
        """
        try:
            return plugin_runner.run(
                'scrooge_reports',
                'extra_cost_plugin',
                type='total_cost',
                start=start,
                end=end,
                service_environments=service_environments,
            )
        except (KeyError, AttributeError):
            logger.warning('Invalid call for total extra cost')
            return D(0)

    def _get_date_ranges_percentage(self, start, end, pricing_service):
        """
        Returns list of minimum date ranges that have different percentage
        division in given pricing_service.

        :returns: dict of date ranges and it's percentage division. Key in dict
            is tuple: (start, end), value is dict (key: usage type id, value:
            percent)
        :rtype dict:
        """
        usage_types = pricing_service.serviceusagetypes_set.filter(
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

    def total_cost(self, start, end, pricing_service, forecast, service_environments):
        """
        Calculates total cost of pricing service (in period of time).

        Total cost will be calculated only for service environments that are in
        service_environment list (these service_environments could be totally
        different than service environments of pricing service services).

        Total cost is sum of cost of base usage types usages, all dependent
        and extra costs.
        services costs (for specified service_environments).

        :param datatime start: Begin of time interval
        :param datatime end: End of time interval
        :param PricingService: Pricing Service for which total cost will be
            calculated
        :param iterable service_environments: List of service_environments for
            which total cost should be calculated
        :returns decimal: total cost of pricing_service
        :rtype decimal:
        """
        # total cost of base usage types for service_environments providing this pricing_service
        total_cost = self._get_service_base_usage_types_cost(
            start,
            end,
            pricing_service,
            forecast,
            service_environments=service_environments,
        )
        total_cost += self._get_service_regular_usage_types_cost(
            start,
            end,
            pricing_service,
            forecast,
            service_environments=service_environments,
        )
        total_cost += self._get_dependent_services_cost(
            start,
            end,
            pricing_service,
            forecast,
            service_environments=service_environments,
        )
        # total_cost += self._get_service_extra_cost(
        #     start,
        #     end,
        #     service_environments,
        # )
        total_cost += self._get_service_teams_cost(
            start,
            end,
            pricing_service,
            forecast,
            service_environments=service_environments,
        )
        return total_cost

    def _fill_distribute_tmpl(self, pricing_service):
        self.distribute_cost_key_tmpl = (
            self.distribute_cost_key_base_tmpl.format(pricing_service.id)
        )
        self.distribute_count_key_tmpl = (
            self.distribute_count_key_base_tmpl.format(pricing_service.id)
        )

    def costs(self, pricing_service, start, end, service_environments, forecast=False, **kwargs):
        """
        Calculates usages and costs of pricing_service usages per service_environment.

        Main steps:
        1) calculation of percentage division in date ranges
        2) for each daterange with different percentage division:
            2.1) calculation of pricing_service total cost in daterange
            2.2) distribution of that cost to service_environments, basing on service_environment usage
                 of pricing_service and using percentage division
            2.3) sum service_environments costs of pricing_service usage types (eventually total
                 cost)
        """
        logger.debug("Calculating report for pricing_service {0}".format(pricing_service))
        self._fill_distribute_tmpl(pricing_service)
        date_ranges_percentage = self._get_date_ranges_percentage(
            start,
            end,
            pricing_service,
        )
        service_symbol = "{0}_service_cost".format(pricing_service.id)
        schema_usage_types = pricing_service.usage_types.all()
        usage_types = sorted(set(schema_usage_types), key=lambda a: a.name)
        total_cost_column = len(usage_types) > 1

        result = defaultdict(lambda: defaultdict(int))
        for date_range, percentage in date_ranges_percentage.items():
            dstart, dend = date_range[0], date_range[1]
            service_cost = self.total_cost(
                dstart,
                dend,
                pricing_service,
                forecast,
                service_environments=pricing_service.service_environments,
            )
            # distribute total cost between every service_environment proportionally to
            # pricing_service usages
            service_report_in_daterange = self._distribute_costs(
                start,
                end,
                service_environments,
                service_cost,
                percentage
            )
            for service_environment, service_environment_data in service_report_in_daterange.items():
                for key, value in service_environment_data.items():
                    result[service_environment][key] += value
                    if total_cost_column and key.endswith('cost'):
                        result[service_environment][service_symbol] += value
        return result

    def schema(self, pricing_service):
        """
        Returns pricing_service usages schema depending on schema usage types.
        """
        self._fill_distribute_tmpl(pricing_service)
        schema_usage_types = pricing_service.usage_types.distinct()
        usage_types = sorted(set(schema_usage_types), key=lambda a: a.name)
        schema = OrderedDict()
        for usage_type in usage_types:
            symbol = usage_type.id
            usage_type_count_symbol = self.distribute_count_key_tmpl.format(
                symbol
            )
            usage_type_cost_symbol = self.distribute_cost_key_tmpl.format(
                symbol
            )

            schema[usage_type_count_symbol] = {
                'name': _("{0} count".format(usage_type.name)),
                'rounding': usage_type.rounding,
                'divide_by': usage_type.divide_by,
            }
            schema[usage_type_cost_symbol] = {
                'name': _("{0} cost".format(usage_type.name)),
                'currency': True,
                'total_cost': len(usage_types) == 1,
            }
        # if there is more than one schema usage type -> add total pricing_service
        # usage column
        if len(usage_types) > 1:
            service_symbol = "{0}_service_cost".format(pricing_service.id)
            schema[service_symbol] = {
                'name': _("{0} cost".format(pricing_service.name)),
                'currency': True,
                'total_cost': True,
            }

        return schema


@register(chain='reports')
class PricingServicePlugin(PricingServiceBasePlugin):
    """
    Base Service Plugin as ralph plugin. Splitting it into two classes gives
    ability to inherit from ServiceBasePlugin.
    """
    pass
