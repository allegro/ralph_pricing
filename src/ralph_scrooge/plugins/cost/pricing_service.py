# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import itertools
from collections import defaultdict
from decimal import Decimal as D

from django.conf import settings
from django.db.models import Sum

from ralph.util import plugin as plugin_runner
from ralph_scrooge.models import (
    DynamicExtraCostType,
    ExtraCostType,
    Team,
    UsageType,
)
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.cost.base import BaseCostPlugin
from ralph_scrooge.utils.common import memoize


logger = logging.getLogger(__name__)


class PricingServiceBasePlugin(BaseCostPlugin):
    """
    Base plugin for all pricing services in report. Provides 2 main methods:
    * costs - tree of costs for pricing service
    * total_cost - returns total cost of service
    """
    def total_cost(self, for_all_service_environments=False, *args, **kwargs):
        """
        Returns total cost of pricing service

        If for_all_service_environments is True, then cost will be calculated
        for all possible service_environments, which is in general "real" total
        cost of this pricing service (equivalent of pricing service row in
        costs report). It's usefull to calculate difference between real costs
        of pricing service (equivalent of row in costs report) and costs
        calculated by specific plugin for pricing service (column in costs
        report).

        If for_all_service_environments is False, then total costs is
        calculated only for service_environments specified in
        service_environments param. It's usefull to calculate dependent pricing
        service costs only for some subset of all service_environments (in
        other words, how dependent pricing service is charging "me" (my service
        environments)).

        In both cases dict with costs hierarchy is returned. On top-level of
        a dict there is only one key-value pair, which is this pricing service
        id and tuple, containing total cost of this pricing service, and dict
        with total cost details (hirearchy). (See `_get_pricing_service_costs`
        for sample).

        :rtype: dict
        :returns: pricing service total costs hierarchy.
        """
        if for_all_service_environments:
            return self._get_pricing_service_costs(*args, **kwargs)
        else:
            service_costs = self.costs(*args, **kwargs)
            return self._get_total_costs_from_costs(service_costs)

    @memoize(skip_first=True)
    def _costs(
        self,
        pricing_service,
        date,
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
        logger.info("Calculating pricing service costs: {0}".format(
            pricing_service.name,
        ))
        costs = self._get_pricing_service_costs(
            pricing_service=pricing_service,
            date=date,
            forecast=forecast,
        )
        percentage = self._get_percentage(date, pricing_service)
        excluded_services = self._get_excluded_services(pricing_service)
        # distribute total cost between every service_environment
        # proportionally to pricing_service usages
        return self._distribute_costs(
            date,
            pricing_service,
            costs,
            percentage,
            excluded_services=excluded_services,
        )

    # HELPERS
    def _get_excluded_services(self, pricing_service):
        """
        Return all excluded services for pricing services (services, on which
        costs shouldn't be allocated) - is union of manually chosen services
        and services from which costs are calculated (they shouldn't charge
        themselves)

        :returns: set of services excluded from chargin by this pricig service
        :rtype: set
        """
        excluded_services = set(pricing_service.excluded_services.all())
        # extend exluded services by pricing services services -
        # pricing service could not charge it's own services (CYCLE!)
        excluded_services.update(set(pricing_service.services.all()))
        return excluded_services

    def _get_total_costs_from_costs(self, costs):
        """
        Transforms costs result structure (costs per service environment
        with _children hierarchy) to format accepted by _get_service_costs
        (dict with type_id as key and tuple (cost, children dict) as value)
        """
        result = {}

        def add_costs(hierarchy, root):
            for cost in hierarchy:
                type_id = cost['type_id']
                if type_id not in root:
                    root[type_id] = [D(0), {}]
                root[type_id][0] += cost['cost']
                if '_children' in cost:
                    add_costs(cost['_children'], root[type_id][1])

        for se, se_costs in costs.items():
            add_costs(se_costs, result)
        return result

    def _add_hierarchy_costs(self, po, po_usages, hierarchy, depth=0):
        """
        For every record in hierarchy, add record to result with cost
        proportional to pricing object usage of pricing service resource.
        """
        subresult = []
        for base_usage, (cost, children) in hierarchy.items():
            base_usage_result = {
                'type_id': base_usage,
                'pricing_object_id': po,
                'cost': D(0),
            }
            for usage, total, percent in po_usages:
                if total != 0:
                    base_usage_result['cost'] += (
                        D(cost) * (D(usage) / D(total)) * (D(percent) / 100)
                    )
                else:
                    base_usage_result['cost'] = D(0)
            # add value if there is only one usage type defined for pricing
            # service and depth is 0 (whole pricing service level)
            if len(po_usages) == 1 and depth == 0:
                base_usage_result['value'] = po_usages[0][0]

            if children and not settings.SAVE_ONLY_FIRST_DEPTH_COSTS:
                base_usage_result['_children'] = self._add_hierarchy_costs(
                    po,
                    po_usages,
                    children,
                    depth+1,
                )
            subresult.append(base_usage_result)
        return subresult

    def _distribute_costs(
        self,
        date,
        pricing_service,
        costs_hierarchy,
        service_usage_types,
        excluded_services,
    ):
        """
        Distribute pricing service costs (in general: hierarchy of pricing
        service costs) between services (pricing objects) according to daily
        usages of pricing service resources (and its percentage division).

        :rtype: dict
        :returns: dict with costs per service environment (and pricing object
            at next level). Sample:
            {
                11: [  # service environment id
                    {  # costs grouped by pricing object and service usage type
                        'cost': Decimal(111),
                        'pricing_object_id': 123,
                        'type_id': 11,
                        '_children': [
                            {
                                'cost': Decimal(100),
                                'pricing_object_id': 123,
                                'type_id': 12,
                                '_children': [
                                    {
                                        'cost': Decimal(50),
                                        'pricing_object_id': 123,
                                        'type_id': 13,
                                    },
                                    {
                                        'cost': Decimal(50),
                                        'pricing_object_id': 123,
                                        'type_id': 14,
                                    },
                                ]
                            },
                            {
                                'cost': Decimal(11),
                                'pricing_object_id': 123,
                                'type_id': 13,
                            },
                        ]
                    },
                    {'cost': D(222), 'pricing_object_id': 321, 'type_id': 11}
                ],
                22: [  # another service environment
                    ...
                ],
                ...
            }
        """
        usages = defaultdict(list)
        total_usages = []
        percentage = []
        result = defaultdict(list)
        self.pricing_service = pricing_service

        for service_usage_type in service_usage_types:
            service_excluded = excluded_services.union(
                service_usage_type.usage_type.excluded_services.all()
            )
            usages_per_po = self._get_usages_per_pricing_object(
                usage_type=service_usage_type.usage_type,
                date=date,
                excluded_services=service_excluded,
            ).values_list(
                'daily_pricing_object__pricing_object',
                'service_environment',
            ).annotate(usage=Sum('value'))
            for pricing_object, se, usage in usages_per_po:
                usages[(pricing_object, se)].append(usage)

            total_usages.append(self._get_total_usage(
                usage_type=service_usage_type.usage_type,
                date=date,
                excluded_services=service_excluded,
            ))
            percentage.append(service_usage_type.percent)
        # create hierarchy basing on usages
        for (po, se), po_usages in usages.items():
            po_usages_info = zip(po_usages, total_usages, percentage)
            result[se].extend(
                self._add_hierarchy_costs(po, po_usages_info, costs_hierarchy)
            )
        return result

    @memoize(skip_first=True)
    def _get_pricing_service_costs(
        self,
        date,
        pricing_service,
        forecast,
    ):
        """
        Calculates total cost of pricing service (for one day).

        Total cost will be calculated only for service environments that are in
        service_environment list (which is in general list of pricing service
        services).

        Total cost is sum of cost of base usage types usages, all dependent
        services costs, (dynamic) extra costs and teams.

        :param date: Day for which calculate pricing service cost
        :type date: datetime.date
        :param pricing_service: Pricing Service for which total cost will be
            calculated
        :type pricing_service: ralph_scrooge.models.PricingService
        :param service_environments: List of service_environments for
            which total cost should be calculated

        :rtype dict:
        :returns: hierarchy of pricing service costs (grouped by base usage
            type) Notice that this dict has only one top-level key-value pair.
            Sample:
            {
                pricing_service_id: (
                    Decimal(1000), # sum of pricing service costs
                    {
                        usage_type1_id: (Decimal(200), {}),
                        usage_type2_id: (Decimal(100), {}),
                        team1_id: (Decimal(100), {}),
                        extra_cost1_id: (Decimal(100), {}),
                        dependent_pricing_service1_id: (Decimal(500), {
                            usage_type1_id: (Decimal(100), {}),
                            usage_type3_id: (Decimal(200), {}),
                            dependent_pricing_service2_id: (Decimal(200), {
                                usage_type3_id: (Decimal(100), {}),
                                team2_id: (Decimal(100), {}),
                            }),
                        }),
                    }
                )
            }
        """
        service_environments = pricing_service.service_environments
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
        dynamic_extra_costs = self._get_service_dynamic_extra_cost(
            date,
            forecast,
            service_environments=service_environments,
        )
        dependent_services_costs = self._get_dependent_services_cost(
            date,
            pricing_service,
            forecast,
            service_environments=service_environments,
        )
        diffs_costs = self._get_service_charging_by_diffs(
            pricing_service=pricing_service,
            date=date,
            forecast=forecast,
        )
        costs = dict(itertools.chain(
            base_usage_types_costs.items(),
            regular_usage_types_costs.items(),
            teams_costs.items(),
            extra_costs.items(),
            dynamic_extra_costs.items(),
            dependent_services_costs.items(),
        ))
        # apply diff costs (costs with equal key could been already calculated)
        for but_id, (value, children) in diffs_costs.iteritems():
            if but_id in costs:
                costs[but_id] = (costs[but_id][0] + value, {})
            else:
                costs[but_id] = (value, children)
        total_cost = sum([v[0] for v in costs.values()])
        return {
            pricing_service.id: (total_cost, costs)
        }

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
                    'team_plugin',
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
        service_environments,
    ):
        """
        Calculates cost of dependent services used by pricing_service.
        """
        result = {}
        exclude = [pricing_service]
        dependent_services = pricing_service.get_dependent_services(
            date,
            exclude,
        )
        for dependent in dependent_services:
            try:
                dependent_cost = plugin_runner.run(
                    'scrooge_costs',
                    dependent.get_plugin_name(),
                    pricing_service=dependent,
                    type='total_cost',
                    date=date,
                    forecast=forecast,
                    service_environments=service_environments,
                )
                result.update(dependent_cost)
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

        :param datatime date: day for which calculate extra costs
        :param list service_environments: List of service_environments
        :returns decimal: price
        :rtype decimal:
        """
        result = {}
        for extra_cost_type in ExtraCostType.objects.all():
            try:
                extra_cost = plugin_runner.run(
                    'scrooge_costs',
                    extra_cost_type.get_plugin_name(),
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

    def _get_service_dynamic_extra_cost(
        self,
        date,
        forecast,
        service_environments,
    ):
        """
        Calculates total cost of dynamic extra costs for given pricing_service.

        :param datatime date: day for which calculate extra costs
        :param list service_environments: List of service_environments
        :returns decimal: price
        :rtype decimal:
        """
        result = {}
        for dynamic_extra_cost_type in DynamicExtraCostType.objects.all():
            try:
                dynamic_extra_cost = plugin_runner.run(
                    'scrooge_costs',
                    'dynamic_extra_cost_plugin',
                    type='total_cost',
                    date=date,
                    forecast=forecast,
                    dynamic_extra_cost_type=dynamic_extra_cost_type,
                    service_environments=service_environments,
                )
                if dynamic_extra_cost != 0:
                    result.update(dynamic_extra_cost)
            except (KeyError, AttributeError):
                logger.warning(
                    'Invalid call for {0} total cost'.format(
                        dynamic_extra_cost_type.name
                    )
                )
        return result

    def _get_service_charging_by_diffs(
        self,
        pricing_service,
        **kwargs
    ):
        """
        Calculates total cost of diffs (between real and calculated costs) of
        selected pricing services.

        :param pricing_service: day for which calculate extra costss
        :returns: dict with difference between real and calculated by specific
            pricing service plugin, grouped by pricing service id (key is
            another pricing service id, value is costs difference)
        :rtype dict:
        """
        result = {}
        for ps in pricing_service.charged_by_diffs.all():
            args = dict(
                type='total_cost',
                pricing_service=ps,
                for_all_service_environments=True,
                **kwargs
            )
            try:
                # first run valid pricing service plugin to get "offical" costs
                ps_cost = plugin_runner.run(
                    'scrooge_costs',
                    ps.get_plugin_name(),
                    **args
                )

                # then call universal plugin to get real cost
                ps_real_cost = plugin_runner.run(
                    'scrooge_costs',
                    'pricing_service_plugin',
                    **args
                )
            except (KeyError, AttributeError):
                logger.warning(
                    'Invalid call for {0} total cost diff'.format(
                        ps.name
                    )
                )
            else:
                # calculate difference between real cost and calculated cost
                diff = ps_real_cost.values()[0][0] - ps_cost.values()[0][0]
                result[ps.id] = diff, {}
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
class PricingServicePlugin(PricingServiceBasePlugin):
    """
    Base Service Plugin as ralph plugin. Splitting it into two classes gives
    ability to inherit from ServiceBasePlugin.
    """
    pass
