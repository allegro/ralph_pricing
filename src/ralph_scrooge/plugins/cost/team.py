# -*- coding: utf-8 -*-
"""
Plugin for billing teams on pricing report.

There are 5 possible models of team billing:
- time
- assets-cores
- assets
- distribution
- average

* Time
For each team, that should be billed based on time model, should be provided
information about percentage division of time, that team spent for each
service environment (in some period of time - generally this periods don't have
to be the same as team cost period). It's assumed, that team cost, that is
defined for some period of time, is split between all days in period as some
daily cost and then distributed between teams based on their value of time
spent.

* assets-cores
In this billing model, each service_environment is billed for total number of
owned assets and cores, proportionally to total number of assets and cores for
all service_environments (in period of team cost definition). Having such
proportions, half of team cost in period of time is designed for assets and
other half for cores. Assets and cores "budget" is distributed for each
service environment, proportionally to the number of owned assets and cores.

* assets
This billing model is similar to assets-cores model, but whole team cost is
distributed to service environments proprotionally to the number of assets
each own.

* Distribution
This model is using other teams (not-distributed) and information about team
members count (more specifically: proportion of team members number to total
members number of all teams). Cost of distributed team is split between all
other teams based on members number proportion. Then, based on other team
model (time, assets-cores or assets), team cost (which is part of total
distributed cost) is spliited between all service environments and summed with
parts of cost for other teams.

* Average
This model is using other teams and use average of percent of other teams costs
distribution between service environments.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict
from decimal import Decimal as D

from django.db.models import Sum, Count
from ralph_scrooge.utils.common import memoize

from ralph_scrooge.models import (
    DailyUsage,
    DailyPricingObject,
    PRICING_OBJECT_TYPES,
    ServiceEnvironment,
    Team as TeamModel,
    TeamBillingType,
    TeamCost,
    UsageType,
)
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.cost.base import (
    BaseCostPlugin,
    NoPriceCostError
)

logger = logging.getLogger(__name__)
PERCENT_PRECISION = 4


@register(chain='scrooge_costs')
class TeamPlugin(BaseCostPlugin):
    @memoize(skip_first=True)
    def _costs(self, team, **kwargs):
        """
        Calculates teams costs.
        """
        logger.info("Calculating team costs: {0}".format(team.name))
        return self._get_team_cost_per_service_environment(team, **kwargs)

    def _get_team_cost_per_service_environment(self, team, *args, **kwargs):
        """
        Call proper function to calculate team cost, based on team billing type
        """
        functions = {
            TeamBillingType.time: (
                self._get_team_time_cost_per_service_environment
            ),
            TeamBillingType.distribute: (
                self._get_team_distributed_cost_per_service_environment
            ),
            TeamBillingType.assets_cores: (
                self._get_team_assets_cores_cost_per_service_environment
            ),
            TeamBillingType.assets: (
                self._get_team_assets_cost_per_service_environment
            ),
            TeamBillingType.average: (
                self._get_team_average_cost_per_service_environment
            ),
        }
        func = functions.get(team.billing_type)
        if func:
            return func(team=team, *args, **kwargs)
        logger.warning('No handle method for billing type {0}'.format(
            team.billing_type
        ))
        return {}

    @memoize(skip_first=True)
    def _get_teams(self):
        """
        Returns all available teams, that should be visible on report
        """
        return TeamModel.objects.all()

    @memoize(skip_first=True)
    def _get_teams_not_distributes_to_others(self):
        """
        Returns all teams that have billing type different than DISTRIBUTE and
        AVERAGE
        """
        return TeamModel.objects.exclude(
            billing_type__in=(
                TeamBillingType.distribute,
                TeamBillingType.average,
            ),
        )

    @memoize(skip_first=True)
    def _get_teams_not_average(self):
        """
        Returns all teams that have billing type different than AVERAGE
        """
        return TeamModel.objects.exclude(
            billing_type=TeamBillingType.average,
        )

    def _get_teams_members_count(self, date, teams):
        """
        Returns members count for given date and teams.

        :rtype: dict (key: team id, value: members count)
        """
        team_costs = TeamCost.objects.filter(
            start__lte=date,
            end__gte=date,
            team__in=teams,
        )
        result = {}
        for team_cost in team_costs:
            result[team_cost.team.id] = team_cost.members_count
        return result

    @memoize(skip_first=True)
    def _get_assets_count_by_service_environment(
        self,
        date,
        excluded_service_environments,
    ):
        """
        Returns (total) assets count per service_environment between start and
        end. Notice that total assets count is sum of all Dailyassets for every
        service_environment - not average assets count.

        :rtype: dict (key: service_environment, value: assets count)
        """
        assets_query = DailyPricingObject.objects.filter(
            date=date,
            pricing_object__type=PRICING_OBJECT_TYPES.ASSET,
        ).exclude(
            service_environment__isnull=True
        ).exclude(
            service_environment__in=excluded_service_environments,
        )
        count = assets_query.values('service_environment').annotate(
            count=Count('id')
        )
        result = dict([
            (dc['service_environment'], dc['count']) for dc in count
        ])
        return result

    @memoize(skip_first=True)
    def _get_total_assets_count(
        self,
        date,
        excluded_service_environments
    ):
        """
        Returns total count of assets in period of time (sum of
        DailyPricingObject).

        :rtype: int
        """
        assets_query = DailyPricingObject.objects.filter(
            date=date,
            pricing_object__type=PRICING_OBJECT_TYPES.ASSET,
        ).exclude(
            service_environment__isnull=True
        ).exclude(
            service_environment__in=excluded_service_environments,
        )
        return assets_query.aggregate(count=Count('id')).get('count', 0)

    def _get_cores_usage_type(self):
        """
        Physical CPU cores usage type definition
        """
        return UsageType.objects.get_or_create(
            symbol="physical_cpu_cores",
        )[0]

    @memoize(skip_first=True)
    def _get_cores_count_by_service_environment(
        self,
        date,
        excluded_service_environments,
    ):
        """
        Returns (total) cores count per service_environment between start and
        end. Notice that total cores count is sum of all DailyUsage for every
        service_environment - not average cores count.

        :rtype: dict (key: service_environment, value: cores count)
        """
        cores_query = DailyUsage.objects.filter(
            type=self._get_cores_usage_type(),
            date=date,
        ).exclude(
            service_environment__isnull=True
        ).exclude(
            service_environment__in=excluded_service_environments,
        )
        count = cores_query.values('service_environment').annotate(
            count=Sum('value')
        )
        result = dict([
            (cc['service_environment'], cc['count']) for cc in count
        ])
        return result

    @memoize(skip_first=True)
    def _get_total_cores_count(
        self,
        date,
        excluded_service_environments
    ):
        """
        Returns total count of cores in period of time (sum of
        DailyPricingObject).

        :rtype: int
        """
        cores_query = DailyUsage.objects.filter(
            type=self._get_cores_usage_type(),
            date=date,
        ).exclude(
            service_environment__isnull=True
        ).exclude(
            service_environment__in=excluded_service_environments,
        )
        return cores_query.aggregate(
            cores_count=Sum('value')
        ).get('cores_count', 0)

    def _get_team_daily_cost(self, team, date, forecast, daily_cost=None):
        try:
            team_cost = team.teamcost_set.get(start__lte=date, end__gte=date)
        except TeamCost.DoesNotExist:
            raise NoPriceCostError()

        # calculate daily cost if not provided
        team_cost_days = (team_cost.end - team_cost.start).days + 1
        if not daily_cost:
            cost = team_cost.forecast_cost if forecast else team_cost.cost
            daily_cost = cost / team_cost_days

        return team_cost_days, daily_cost, team_cost

    def _get_team_time_cost_per_service_environment(
        self,
        team,
        date,
        forecast=False,
        daily_cost=None,
        **kwargs
    ):
        """
        Calculates cost of teams, that are billed by spent time for each
        service environment. If daily_cost is passed, it's used instead of
        calculated daily cost from total cost.

        Main idea:
        for every period in which cost is defined for team
            for every not-overlaping daterange of percent per team
                calculate cost of team time per service environment in this
                period of time

        Notice that:
        * total cost is treated as sum of equal daily cost (assumed, that in
            period of time daily cost is the same)
        * assumed, that in period of time percent of time spent to service
            environment is equal for each day
        """

        result = defaultdict(list)
        team_cost_days, daily_cost, team_cost = self._get_team_daily_cost(
            team,
            date,
            forecast,
            daily_cost,
        )

        percentage = dict(team_cost.percentage.values_list(
            'service_environment__id',
            'percent',
        ))
        for service_environment, percent in percentage.items():
            result[service_environment].append({
                'cost': D(daily_cost) * D(percent) / 100,
                'type': team,
                'percent': D(percent) / 100,
            })

        return result

    def _get_team_func_cost_per_service_environment(
        self,
        team,
        date,
        forecast=False,
        daily_cost=None,
        funcs=None,
        **kwargs
    ):
        """
        Calculates cost of used resources (i.e. assets, cores) for each
        service environment in period of time. If daily_cost is passed, it's
        used instead of calculated daily cost from total cost.

        Main idea:
        for every period in which cost is defined for team:
            calculate daily cost
            for every resource:
                get total count of resource usage per service_environment
                calculate service_environment cost based od cost in period of
                 time andresource usage

        Passed functions (funcs) should be 3-elements tuple:
        (
            resource_usage_per_service_environment_function,
            resource_total_usage_function,
            result_dict_key (to store usages of service_environment)
        ).

        Notice that:
        * if there is more than one funcs (resources), that total cost is
            distributed in equal parts to all resources (1/n)
        """
        result = defaultdict(list)
        funcs = funcs or []
        excluded_service_environments = ServiceEnvironment.objects.filter(
            service__in=team.excluded_services.all(),
        )

        team_cost_days, daily_cost, team_cost = self._get_team_daily_cost(
            team,
            date,
            forecast,
            daily_cost,
        )
        service_environments_costs = defaultdict(D)
        for count_func, total_count_func in funcs:
            count_per_service_environment = count_func(
                date,
                excluded_service_environments=excluded_service_environments,
            )
            total = total_count_func(
                date,
                excluded_service_environments=excluded_service_environments,
            )
            # if there is more than one resource, calculate 1/n of total
            # cost
            cost_part = D(daily_cost) / len(funcs)
            for se, count in count_per_service_environment.items():
                percent = D(count) / D(total) if total else D(0)
                service_environments_costs[se] += D(cost_part * percent)

        for service_environment, cost in service_environments_costs.items():
            result[service_environment].append({
                'cost': cost,
                'type': team,
                'percent': D(cost) / D(daily_cost) if daily_cost else 0,
            })

        return result

    def _get_team_assets_cores_cost_per_service_environment(
        self,
        team,
        *args,
        **kwargs
    ):
        """
        Calculates costs of assets and cores usage per service_environment.
        """
        return self._get_team_func_cost_per_service_environment(
            team=team,
            funcs=(
                (
                    self._get_assets_count_by_service_environment,
                    self._get_total_assets_count,
                ),
                (
                    self._get_cores_count_by_service_environment,
                    self._get_total_cores_count,
                ),
            ),
            *args,
            **kwargs
        )

    def _get_team_assets_cost_per_service_environment(
        self,
        team,
        *args,
        **kwargs
    ):
        """
        Calculates costs of assets usage per service_environment.
        """
        return self._get_team_func_cost_per_service_environment(
            team=team,
            funcs=(
                (
                    self._get_assets_count_by_service_environment,
                    self._get_total_assets_count,
                ),
            ),
            *args,
            **kwargs
        )

    def _get_team_distributed_cost_per_service_environment(
        self,
        team,
        date,
        forecast=False,
        **kwargs
    ):
        """
        Calculates cost of team, which cost is based on service_environment
        cost for other teams (proprotionally to members count of other teams).

        Main idea:
        for every period on which cost is defined for team
            for every period of not-distributed teams members count in main
            period
                for every not-distributed team
                    get team members count in period and it's % among all teams
                    calculate % of distributed team total cost (daily)
                    calculate cost for this team for all service_environments,
                    proportionally to team cost (usage)

        Not distributed team cost is calculated using functions defined for
        such calculations. First of all, daily cost of distributed team is
        calculated. Then, based on not distributed team members count, daily
        cost of that team is calculated (distributed_team_daily_cost *
        not_distributed_team_members_count / total_members). Then such daily
        cost is passed to function for not distributed team and used to
        calculate (part of) cost of distributed team.
        """

        result = defaultdict(list)
        teams = self._get_teams_not_distributes_to_others()
        teams_by_id = dict([(t.id, t) for t in teams])

        team_cost_days, daily_cost, team_cost = self._get_team_daily_cost(
            team,
            date,
            forecast,
        )
        teams_members = self._get_teams_members_count(date, teams)
        total_members = sum(teams_members.values())

        service_environments_costs = defaultdict(D)

        for team_id, members_count in teams_members.items():
            dependent_team = teams_by_id[team_id]
            daily_team_cost = float(daily_cost) * members_count / total_members
            for sei in self._costs(
                team=dependent_team,
                date=date,
                daily_cost=daily_team_cost,
                forecast=forecast,
            ).items():
                service_environments_costs[sei[0]] += sum(
                    s['cost'] for s in sei[1]
                )

        for service_environment, cost in service_environments_costs.items():
            se_info = {
                'type': team,
                'cost': cost,
                'percent': cost / daily_cost
            }
            result[service_environment].append(se_info)

        return result

    def _get_team_average_cost_per_service_environment(
        self,
        team,
        date,
        forecast=False,
        **kwargs
    ):
        """
        Calculates team cost according to average of percents of other teams
        costs per service_environments.

        For every dependent team (every other, that has billing type different
        than AVERAGE), in period of time for which cost is defined for current
        team, there are costs and percentage division calculated for such a
        dependent team. Calculated percentage division is then added to service
        environment 'counter' and at the end, total cost of current team is
        distributed according to service_environments 'counters' (of percent).
        """
        result = defaultdict(list)
        teams = self._get_teams_not_average()
        team_cost_days, daily_cost, team_cost = self._get_team_daily_cost(
            team,
            date,
            forecast,
        )

        # calculate costs and percent of other teams per
        # service_environment
        service_environment_percent = defaultdict(D)
        total_percent = len(teams)

        for dependent_team in teams:
            seis = self._costs(
                team=dependent_team,
                date=date,
                forecast=forecast,
            )
            for sei in seis.items():
                se = sei[0]
                percent = sei[1][0]['percent']
                service_environment_percent[se] += percent
        # distribute cost of current team according to calculated percent
        for se, percent in service_environment_percent.iteritems():
            percent_scaled = percent / total_percent
            result[se].append({
                'cost': daily_cost * percent_scaled,
                'percent': percent_scaled,
                'type': team,
            })

        return result
