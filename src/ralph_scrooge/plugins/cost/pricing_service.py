# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import itertools
from collections import defaultdict
from decimal import Decimal as D

from django.db.models import Sum

from ralph.util import plugin as plugin_runner

from ralph_scrooge.models import ExtraCostType, Team, UsageType
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.cost.base import BaseCostPlugin


logger = logging.getLogger(__name__)


class PricingServiceBaseCostPlugin(BaseCostPlugin):
    """
    Base plugin for all pricing services in report. Provides 3 main methods:
    * usages - service resources usages count and cost per service_environment
    * schema - schema (output format) of usages method
    * total_cost - returns total cost of service
    """
    def total_costs(self, collapse=True, *args, **kwargs):
        service_costs = self._get_service_costs()
        if collapse:
            return sum([v[0] for v in service_costs.values()])
        return service_costs

    def costs(
        self,
        pricing_service,
        date,
        service_environments,
        forecast=False,
        **kwargs
    ):
        """
        Calculates usages and costs of pricing service usages per service
        environment.

        Main steps:
        1) calculation of percentage division in date ranges
        2) for each daterange with different percentage division:
            2.1) calculation of pricing_service total cost in daterange
            2.2) distribution of that cost to service_environments, basing on
                 service_environment usage of pricing_service and using
                 percentage division
            2.3) sum service_environments costs of pricing_service usage types
                 (eventually total cost)
        """
        logger.debug("Calculating report for pricing_service {0}".format(
            pricing_service
        ))
        percentage = self._get_percentage(date, pricing_service)
        costs = self._get_service_costs(
            date,
            pricing_service,
            forecast,
            service_environments=pricing_service.service_environments,
        )
        # distribute total cost between every service_environment
        # proportionally to pricing_service usages
        return self._distribute_costs(
            date,
            pricing_service,
            service_environments,
            costs,
            percentage
        )

    # HELPERS
    def _get_service_costs(
        self,
        date,
        pricing_service,
        forecast,
        service_environments,
    ):
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
        # total cost of base usage types for service_environments providing
        # this pricing_service
        base_usage_types_costs = self._get_service_base_usage_types_cost(
            date,
            pricing_service,
            forecast,
            service_environments=service_environments,
        )
        regular_usage_types_costs = self._get_service_regular_usage_types_cost(
            date,
            pricing_service,
            forecast,
            service_environments=service_environments,
        )
        dependent_services_costs = self._get_dependent_services_cost(
            date,
            pricing_service,
            forecast,
            service_environments=service_environments,
        )
        teams_costs = self._get_service_teams_cost(
            date,
            forecast,
            service_environments=service_environments,
        )
        extra_costs = self._get_service_extra_cost(
            date,
            forecast,
            service_environments=service_environments,
        )

        costs = dict(itertools.chain(
            base_usage_types_costs.items(),
            regular_usage_types_costs.items(),
            dependent_services_costs.items(),
            teams_costs.items(),
            extra_costs.items(),
        ))
        total_cost = sum([v[0] for v in costs.values()])

        return {
            pricing_service.id: (total_cost, costs)
        }

    def _distribute_costs(
        self,
        date,
        pricing_service,
        service_environments,
        costs_hierarchy,
        service_usage_types,
    ):
        usages = defaultdict(list)
        total_usages = []
        percentage = []
        result = defaultdict(list)
        for service_usage_type in service_usage_types:
            usages_per_po = self._get_usages_per_pricing_object(
                usage_type=service_usage_type.usage_type,
                date=date,
                service_environments=service_environments,
                excluded_services=pricing_service.services.all(),
            ).values_list(
                'daily_pricing_object__pricing_object',
                'service_environment',
            ).annotate(usage=Sum('value'))
            for pricing_object, se, usage in usages_per_po:
                usages[(pricing_object, se)].append(usage)

            total_usages.append(self._get_total_usage(
                usage_type=service_usage_type.usage_type,
                date=date,
                service_environments=service_environments,
                excluded_services=pricing_service.services.all(),
            ))
            percentage.append(service_usage_type.percent)

        def add_costs(po, po_usages, hierarchy):
            subresult = []
            for base_usage, (cost, children) in hierarchy.items():
                base_usage_result = {
                    'type_id': base_usage,
                    'pricing_object_id': po,
                    'cost': D(0),
                }
                for usage, total, percent in po_usages:
                    base_usage_result['cost'] += (
                        D(cost) * (D(usage) / D(total)) * (D(percent) / 100)
                    )
                if children:
                    base_usage_result['_children'] = add_costs(
                        po,
                        po_usages,
                        children,
                    )
                subresult.append(base_usage_result)
            return subresult

        for (po, se), po_usages in usages.items():
            po_usages_info = zip(po_usages, total_usages, percentage)
            result[se].extend(add_costs(po, po_usages_info, costs_hierarchy))
        return result

    def _get_usage_type_costs(
        self,
        date,
        usage_type,
        forecast,
        service_environments
    ):
        """
        Calculates total cost of usage of given type for specified
        service environments in period of time (between start and end), using
        real or forecast price/cost.
        """
        try:
            return plugin_runner.run(
                'scrooge_costs',
                usage_type.get_plugin_name(),
                type='total_cost',
                date=date,
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
        date,
        pricing_service,
        forecast,
        service_environments,
    ):
        """
        Calculates total cost of base types usages for given pricing service,
        using real or forecast prices/costs. Total cost is calculated for
        period of time (between start and end) and for specified
        service environments.
        """
        result = {}
        for usage_type in UsageType.objects.filter(usage_type='BU').exclude(
                id__in=pricing_service.excluded_base_usage_types.values_list(
                    'id',
                    flat=True
                )):
            usage_type_costs = self._get_usage_type_costs(
                date,
                usage_type,
                forecast,
                service_environments,
            )
            if usage_type_costs != 0:
                result[usage_type.id] = usage_type_costs, {}
        return result

    def _get_service_regular_usage_types_cost(
        self,
        date,
        pricing_service,
        forecast,
        service_environments,
    ):
        """
        Calculates total cost of regular types usages for given pricing
        service, using real or forecast prices/costs. Total cost is calculated
        for period of time (between start and end) and for specified service
        environments.
        """
        result = {}
        for usage_type in pricing_service.regular_usage_types.all():
            usage_type_costs = self._get_usage_type_costs(
                date,
                usage_type,
                forecast,
                service_environments,
            )
            if usage_type_costs != 0:
                result[usage_type.id] = usage_type_costs, {}
        return result

    def _get_service_teams_cost(
        self,
        date,
        forecast,
        service_environments,
    ):
        """
        Calculates total cost of teams for given pricing service, using
        real or forecast prices/costs. Total cost is calculated for period of
        time (between start and end) and for specified service environments.
        """
        result = {}
        for team in Team.objects.all():
            try:
                team_cost = plugin_runner.run(
                    'scrooge_costs',
                    'team',
                    type='total_cost',
                    date=date,
                    team=team,
                    forecast=forecast,
                    service_environments=service_environments,
                )
                if team_cost != 0:
                    result[team.id] = team_cost, {}
            except (KeyError, AttributeError):
                logger.warning(
                    'Invalid call for {0} total cost'.format(team.name)
                )
        return result

    def _get_dependent_services_cost(
        self,
        date,
        pricing_service,
        forecast,
        service_environments
    ):
        """
        Calculates cost of dependent services used by pricing_service.
        """
        result = {}
        dependent_services = pricing_service.get_dependent_services(date)
        for dependent in dependent_services:
            try:
                dependent_cost = plugin_runner.run(
                    'scrooge_costs',
                    dependent.get_plugin_name(),
                    pricing_service=dependent,
                    type='total_cost',
                    collapse=False,
                    date=date,
                    forecast=forecast,
                    service_environments=service_environments,
                )
                dependent_total_cost = sum(
                    [v[0] for v in dependent_cost.values()]
                )
                if dependent_total_cost != 0:
                    result[dependent.id] = dependent_total_cost, dependent_cost
            except (KeyError, AttributeError):
                logger.warning(
                    'Invalid call for {0} total cost'.format(dependent.name)
                )
        return result

    def _get_service_extra_cost(
        self,
        date,
        forecast,
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
        result = {}
        for extra_cost_type in ExtraCostType.objects.all():
            try:
                extra_cost = plugin_runner.run(
                    'scrooge_costs',
                    'extra_cost_plugin',
                    type='total_cost',
                    date=date,
                    forecast=forecast,
                    extra_cost_type=extra_cost_type,
                    service_environments=service_environments,
                )
                if extra_cost != 0:
                    result[extra_cost_type.id] = extra_cost, {}
            except (KeyError, AttributeError):
                logger.warning(
                    'Invalid call for {0} total cost'.format(
                        extra_cost_type.name
                    )
                )
        return result

    def _get_percentage(self, date, pricing_service):
        """
        Returns list of minimum date ranges that have different percentage
        division in given pricing_service.

        :returns: dict of date ranges and it's percentage division. Key in dict
            is tuple: (start, end), value is dict (key: usage type id, value:
            percent)
        :rtype dict:
        """
        usage_types = pricing_service.serviceusagetypes_set.filter(
            start__lte=date,
            end__gte=date,
        )
        assert abs(sum([s.percent for s in usage_types]) - 100) < 0.01
        return usage_types


@register(chain='scrooge_costs')
class PricingServiceCostPlugin(PricingServiceBaseCostPlugin):
    """
    Base Service Plugin as ralph plugin. Splitting it into two classes gives
    ability to inherit from ServiceBasePlugin.
    """
    pass