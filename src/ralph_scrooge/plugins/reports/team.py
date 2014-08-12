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
from collections import defaultdict, OrderedDict
from decimal import Decimal as D

from django.db.models import Sum, Count
from django.utils.translation import ugettext_lazy as _
from lck.cache import memoize

from ralph_scrooge.models import (
    DailyUsage,
    DailyPricingObject,
    PricingObjectType,
    ServiceEnvironment,
    Team as TeamModel,
    TeamBillingType,
    TeamCost,
    TeamServiceEnvironmentPercent,
    UsageType,
)
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.reports.base import BaseReportPlugin
from ralph_scrooge import utils

logger = logging.getLogger(__name__)
PERCENT_PRECISION = 4


@register(chain='scrooge_reports')
class Team(BaseReportPlugin):
    @memoize(skip_first=True)
    def _get_teams(self):
        """
        Returns all available teams, that should be visible on report
        """
        return TeamModel.objects.filter(show_in_report=True)

    @memoize(skip_first=True)
    def _get_teams_not_distributes_to_others(self):
        """
        Returns all teams that have billing type different than DISTRIBUTE and
        AVERAGE
        """
        return TeamModel.objects.filter(show_in_report=True).exclude(
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
        return TeamModel.objects.filter(show_in_report=True).exclude(
            billing_type=TeamBillingType.average,
        )

    def _incomplete_price(self, start, end, team):
        """
        Calculate if for every day in report there is price defined for usage
        type

        :param list usage_type: usage type
        :param datetime start: Start date of the report
        :param datetime end: End date of the report
        :returns str: 'No price' or 'Incomplete price' or None (if all is ok)
        """
        total_days = (end - start).days + 1  # total report days
        ut_days = 0
        team_costs = team.teamcost_set.filter(
            end__gte=start,
            start__lte=end,
        )
        team_costs = team_costs.values('start', 'end').distinct()
        intervals = [(v['start'], v['end']) for v in team_costs]
        sum_of_intervals = utils.sum_of_intervals(intervals)
        ut_days = sum(map(
            lambda k: (min(end, k[1]) - max(start, k[0])).days + 1,
            sum_of_intervals
        ))
        if ut_days == 0:
            return _('No price')
        if ut_days != total_days:
            return _('Incomplete price')

    def _get_teams_dateranges_members_count(self, start, end, teams):
        """
        Returns not overlaping members count of each time in periods of time
        between start and end.

        :rtype: dict (key: (start, end) tuple; value: dict team-members count)
        """
        members_count = TeamCost.objects.filter(
            start__lte=end,
            end__gte=start,
            team__in=teams,
        )
        dates = defaultdict(lambda: defaultdict(list))
        for mc in members_count:
            dates[max(mc.start, start)]['start'].append(mc)
            dates[min(mc.end, end)]['end'].append(mc)

        result = {}
        current_members_count = {}
        current_start = None

        # iterate through dict items sorted by key (date)
        for date, mc in sorted(dates.items(), key=lambda k: k[0]):
            if mc['start']:
                current_start = date
            for tm in mc['start']:
                current_members_count[tm.team.id] = tm.members_count

            if mc['end']:
                result[(current_start, date)] = current_members_count.copy()
            for tm in mc['end']:
                del current_members_count[tm.team.id]
        return result

    @memoize(skip_first=True)
    def _get_assets_count_by_service_environment(
        self,
        start,
        end,
        service_environments
    ):
        """
        Returns (total) assets count per service_environment between start and
        end. Notice that total assets count is sum of all Dailyassets for every
        service_environment - not average assets count.

        :rtype: dict (key: service_environment, value: assets count)
        """
        assets_query = DailyPricingObject.objects.filter(
            date__gte=start,
            date__lte=end,
            service_environment__in=service_environments,
            pricing_object__type=PricingObjectType.asset,
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
        start,
        end,
        excluded_service_environments
    ):
        """
        Returns total count of assets in period of time (sum of
        DailyPricingObject).

        :rtype: int
        """
        assets_query = DailyPricingObject.objects.filter(
            date__gte=start,
            date__lte=end,
            pricing_object__type=PricingObjectType.asset,
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
        start,
        end,
        service_environments
    ):
        """
        Returns (total) cores count per service_environment between start and
        end. Notice that total cores count is sum of all DailyUsage for every
        service_environment - not average cores count.

        :rtype: dict (key: service_environment, value: cores count)
        """
        cores_query = DailyUsage.objects.filter(
            type=self._get_cores_usage_type(),
            date__gte=start,
            date__lte=end,
            service_environment__in=service_environments
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
        start,
        end,
        excluded_service_environments
    ):
        """
        Returns total count of cores in period of time (sum of
        DailyPricingObject).

        :rtype: int
        """
        cores_query = DailyUsage.objects.filter(
            type=self._get_cores_usage_type(),
            date__gte=start,
            date__lte=end,
        ).exclude(
            service_environment__isnull=True
        ).exclude(
            service_environment__in=excluded_service_environments,
        )
        return cores_query.aggregate(
            cores_count=Sum('value')
        ).get('cores_count', 0)

    def _get_percent_from_costs(
        self,
        service_environments_costs,
        total_cost,
        percent_key,
        cost_key
    ):
        """
        Calculates service environment percent of total cost, according to
        it's cost
        """
        for v in service_environments_costs.values():
            if isinstance(v[cost_key], (D, int, float)) and total_cost:
                v[percent_key] = v[cost_key] / total_cost
            else:
                v[percent_key] = 0

    def _get_team_time_cost_per_service_environment(
        self,
        team,
        start,
        end,
        service_environments,
        forecast=False,
        no_price_msg=False,
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

        result = defaultdict(lambda: defaultdict(int))
        service_environments_ids = set([v.id for v in service_environments])
        cost_key = 'team_{}_cost'.format(team.id)
        percent_key = 'team_{}_percent'.format(team.id)
        # check if price is undefined for any time between start and end
        price_undefined = no_price_msg and self._incomplete_price(
            start,
            end,
            team,
        )
        total_cost = 0

        def add_subcosts(sstart, send, cost, percentage):
            """
            Helper to add subcost for every service_environment for single,
            integral period of time.
            """
            # for every service_environment-percentage division defined for
            # period of time
            for service_environment, percent in percentage.items():
                if service_environment in service_environments_ids:
                    # store daily percent to calculate average percent
                    if price_undefined:
                        result[service_environment][cost_key] = price_undefined
                    else:
                        result[service_environment][cost_key] += (
                            cost * D(percent) / 100
                        )

        usageprices = team.teamcost_set.filter(start__lte=end, end__gte=start)
        if usageprices:
            for team_cost in usageprices:
                cost = team_cost.forecast_cost if forecast else team_cost.cost
                # calculate daily cost if not provided
                if not daily_cost:
                    period_daily_cost = cost / (
                        (team_cost.end - team_cost.start).days + 1
                    )
                else:
                    period_daily_cost = daily_cost
                tcstart = max(start, team_cost.start)
                tcend = min(end, team_cost.end)
                period_cost = period_daily_cost * ((tcend - tcstart).days + 1)
                percentage = dict(team_cost.percentage.values_list(
                    'service_environment__id',
                    'percent',
                ))
                add_subcosts(tcstart, tcend, period_cost, percentage)
                total_cost += period_cost
                # dateranges_percentage = self._get_team_dateranges_percentage(
                #     tcstart,
                #     tcend,
                #     team
                # )
                # for (dpstart, dpend), percent in dateranges_percentage.items():
                #     subcost = period_daily_cost * ((dpend - dpstart).days + 1)
                #     add_subcosts(dpstart, dpend, subcost, percent)

        else:
            # if price was not provided at all
            percentage = TeamServiceEnvironmentPercent.objects.filter(
                team_daterange__team=team,
                team_daterange__start__lte=end,
                team_daterange__end__gte=start,
                service_environment__in=service_environments,
            )
            percentage = dict([
                (p.service_environment.id, p.percent) for p in percentage
            ])
            add_subcosts(start, end, 0, percentage)

        self._get_percent_from_costs(result, total_cost, percent_key, cost_key)

        return result

    def _exclude_service_environments(self, team, service_environments):
        if team.excluded_services.count():
            service_environments = list(set(service_environments) - set(
                ServiceEnvironment.objects.filter(
                    service__in=team.excluded_services.all())
                )
            )
        return service_environments

    def _get_team_func_cost_per_service_environment(
        self,
        team,
        start,
        end,
        service_environments,
        forecast=False,
        no_price_msg=False,
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

        result = defaultdict(lambda: defaultdict(int))
        cost_key = 'team_{}_cost'.format(team.id)
        percent_key = 'team_{}_percent'.format(team.id)
        price_undefined = no_price_msg and self._incomplete_price(
            start,
            end,
            team,
        )
        funcs = funcs or []
        total_cost = 0
        service_environments = self._exclude_service_environments(
            team,
            service_environments
        )

        def add_subcosts(sstart, send, cost):
            for count_func, total_count_func in funcs:
                count_per_service_environment = count_func(
                    sstart,
                    send,
                    service_environments
                )
                total = total_count_func(
                    sstart,
                    send,
                    ServiceEnvironment.objects.filter(
                        service__in=team.excluded_services.all(),
                    )
                )
                # if there is more than one resource, calculate 1/n of total
                # cost
                cost_part = cost / D(len(funcs))
                for se, count in count_per_service_environment.items():
                    if price_undefined:
                        result[se][cost_key] = price_undefined
                    elif not total:
                        result[se][cost_key] = D(0)
                    else:
                        result[se][cost_key] += (
                            cost_part * D(count) / D(total)
                        )

        team_costs = team.teamcost_set.filter(
            start__lte=end,
            end__gte=start,
        )
        if team_costs:
            for team_cost in team_costs:
                cost = team_cost.forecast_cost if forecast else team_cost.cost
                if not daily_cost:
                    period_daily_cost = cost / (
                        (team_cost.end - team_cost.start).days + 1
                    )
                else:
                    period_daily_cost = daily_cost

                tcstart = max(start, team_cost.start)
                tcend = min(end, team_cost.end)
                total_cost += period_daily_cost * ((tcend - tcstart).days + 1)
                cost = period_daily_cost * ((tcend - tcstart).days + 1)
                add_subcosts(tcstart, tcend, cost)
        else:
            add_subcosts(start, end, 0)

        self._get_percent_from_costs(result, total_cost, percent_key, cost_key)
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
        start,
        end,
        service_environments,
        forecast=False,
        no_price_msg=False,
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

        result = defaultdict(lambda: defaultdict(D))
        teams = self._get_teams_not_distributes_to_others()
        teams_by_id = dict([(t.id, t) for t in teams])
        cost_key = 'team_{}_cost'.format(team.id)
        percent_key = 'team_{}_percent'.format(team.id)
        price_undefined = no_price_msg and self._incomplete_price(
            start,
            end,
            team,
        )

        team_costs = team.teamcost_set.filter(start__lte=end, end__gte=start)
        total_cost = 0

        if team_costs:
            for team_cost in team_costs:
                cost = team_cost.forecast_cost if forecast else team_cost.cost
                tcstart = max(start, team_cost.start)
                tcend = min(end, team_cost.end)
                daily_cost = cost / (
                    (team_cost.end - team_cost.start).days + 1
                )
                total_cost += daily_cost * ((tcend - tcstart).days + 1)
                for members_count in self._get_teams_dateranges_members_count(
                    tcstart, tcend, teams
                ).items():
                    (mcstart, mcend), team_members_count = members_count
                    total_members = sum(team_members_count.values())
                    for team_id, members in team_members_count.items():
                        dependent_team = teams_by_id[team_id]
                        team_cost_key = 'team_{}_cost'.format(
                            dependent_team.id,
                        )
                        daily_team_cost = daily_cost * members / total_members
                        for sei in self._get_team_cost_per_service_environment(
                            team=dependent_team,
                            start=mcstart,
                            end=mcend,
                            service_environments=service_environments,
                            daily_cost=daily_team_cost,
                            forecast=forecast,
                        ).items():
                            se = sei[0]
                            se_cost = sei[1][team_cost_key]
                            if price_undefined:
                                result[se][cost_key] = price_undefined
                            elif isinstance(se_cost, (int, D)):
                                result[se][cost_key] += se_cost
        else:
            for service_environment in service_environments:
                result[service_environment.id][cost_key] = price_undefined

        self._get_percent_from_costs(result, total_cost, percent_key, cost_key)

        return result

    def _get_team_average_cost_per_service_environment(
        self,
        team,
        start,
        end,
        service_environments,
        forecast=False,
        no_price_msg=False,
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
        result = defaultdict(lambda: defaultdict(D))
        teams = self._get_teams_not_average()
        cost_key = 'team_{}_cost'.format(team.id)
        percent_key = 'team_{}_percent'.format(team.id)
        price_undefined = no_price_msg and self._incomplete_price(
            start,
            end,
            team,
        )
        team_costs = team.teamcost_set.filter(start__lte=end, end__gte=start)
        total_cost = 0

        # if any team cost was defined between start and end
        if team_costs:
            for team_cost in team_costs:
                service_environment_percent = defaultdict(D)
                total_percent = len(teams)
                tcstart = max(start, team_cost.start)
                tcend = min(end, team_cost.end)
                cost = team_cost.forecast_cost if forecast else team_cost.cost
                daily_cost = cost / (
                    (team_cost.end - team_cost.start).days + 1
                )
                period_cost = daily_cost * ((tcend - tcstart).days + 1)
                total_cost += period_cost
                # calculate costs and percent of other teams per
                # service_environment
                for dependent_team in teams:
                    team_percent_key = 'team_{}_percent'.format(
                        dependent_team.id,
                    )
                    for sei in self._get_team_cost_per_service_environment(
                        team=dependent_team,
                        start=tcstart,
                        end=tcend,
                        service_environments=service_environments,
                        forecast=forecast,
                    ).items():
                        se = sei[0]
                        percent = sei[1][team_percent_key]
                        service_environment_percent[se] += percent

                # distribute cost of current team according to calculated
                # percent between tcstart and tcend
                for se, percent in service_environment_percent.iteritems():
                    if price_undefined:
                        result[se][cost_key] = price_undefined
                    else:
                        result[se][cost_key] += (
                            period_cost * percent / total_percent
                        )
        else:
            for service_environment in service_environments:
                result[service_environment.id][cost_key] = price_undefined

        # calculate percent of total cost per service_environment
        # sum of percent should be equal to 1
        self._get_percent_from_costs(result, total_cost, percent_key, cost_key)

        return result

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
            logger.debug("Getting team {0} costs".format(team))
            return func(team=team, *args, **kwargs)
        logger.warning('No handle method for billing type {0}'.format(
            team.billing_type
        ))
        return {}

    def total_cost(self, team, *args, **kwargs):
        costs = self.costs(team=team, *args, **kwargs)
        total_cost_key = 'team_{}_cost'.format(team.id)
        return sum([u[total_cost_key] for u in costs.values()])

    def costs(self, team, **kwargs):
        """
        Calculates teams costs.
        """
        logger.debug("Get teams usages")
        return self._get_team_cost_per_service_environment(team, **kwargs)

    def schema(self, team, **kwargs):
        """
        Build schema for this usage.

        :returns dict: schema for usage
        """
        logger.debug("Get teams schema")
        schema = OrderedDict()
        if team.show_percent_column:
            schema['team_{}_percent'.format(team.id)] = {
                'name': _("{} %".format(team.name)),
                'rounding': PERCENT_PRECISION,
            }
        schema['team_{}_cost'.format(team.id)] = {
            'name': _("{0} cost".format(team.name)),
            'currency': True,
            'total_cost': True,
        }
        return schema
