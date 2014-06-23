# -*- coding: utf-8 -*-
"""
Plugin for billing teams on pricing report.

There are 5 possible models of team billing:
- time
- devices-cores
- devices
- distribution
- average

* Time
For each team, that should be billed based on time model, should be provided
information about percentage division of time, that team spent for each
venture (in some period of time - generally this periods don't have to be the
same as team cost period). It's assumed, that team cost, that is defined for
some period of time, is split between all days in period as some daily cost
and then distributed between teams based on their value of time spent.

* Devices-cores
In this billing model, each venture is billed for total number of owned devices
and cores, proportionally to total number of devices and cores for all
ventures (in period of team cost definition). Having such proportions, half of
team cost in period of time is designed for devices and other half for cores.
Devices and cores "budget" is distributed for each venture, proportionally to
the number of owned devices and cores.

* Devices
This billing model is similar to devices-cores model, but whole team cost is
distributed to ventures proprotionally to the number of devices each own.

* Distribution
This model is using other teams (not-distributed) and information about team
members count (more specifically: proportion of team members number to total
members number of all teams). Cost of distributed team is split between all
other teams based on members number proportion. Then, based on other team
model (time, devices-cores or devices), team cost (which is part of total
distributed cost) is spliited between all ventures and summed with parts of
cost for other teams.

* Average
This model is using other teams and use average of percent of other teams costs
distribution between ventures.
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

from ralph_pricing.models import (
    DailyDevice,
    DailyUsage,
    Team as TeamModel,
    TeamVenturePercent,
    UsagePrice,
    UsageType
)
from ralph_pricing.plugins.base import register
from ralph_pricing.plugins.reports.usage import UsageBasePlugin


logger = logging.getLogger(__name__)
PERCENT_PRECISION = 4


@register(chain='reports')
class Team(UsageBasePlugin):
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
            billing_type__in=('DISTRIBUTE', 'AVERAGE'),
        )

    @memoize(skip_first=True)
    def _get_teams_not_average(self):
        """
        Returns all teams that have billing type different than AVERAGE
        """
        return TeamModel.objects.filter(show_in_report=True).exclude(
            billing_type='AVERAGE'
        )

    def _get_team_dateranges_percentage(self, start, end, team):
        """
        Returns percentage division (of team time) between ventures in period
        of time (between start and end). Returned periods are not overlapping.

        :rtype: dict (key: (start, end) tuple; value: dict venture-percent )
        """
        result = {}
        for daterange in team.dateranges.filter(
            start__lte=end,
            end__gte=start
        ):
            dstart = max(daterange.start, start)
            dend = min(daterange.end, end)

            subresult = {}
            for vp in daterange.percentage.all():
                subresult[vp.venture.id] = vp.percent
            result[(dstart, dend)] = subresult
        return result

    def _get_teams_dateranges_members_count(self, start, end, teams):
        """
        Returns not overlaping members count of each time in periods of time
        between start and end.

        :rtype: dict (key: (start, end) tuple; value: dict team-members count )
        """
        members_count = UsagePrice.objects.filter(
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
                current_members_count[tm.team.id] = tm.team_members_count

            if mc['end']:
                result[(current_start, date)] = current_members_count.copy()
            for tm in mc['end']:
                del current_members_count[tm.team.id]
        return result

    @memoize(skip_first=True)
    def _get_devices_count_by_venture(self, start, end, ventures):
        """
        Returns (total) devices count per venture between start and end.
        Notice that total devices count is sum of all DailyDevices for every
        venture - not average devices count.

        :rtype: dict (key: venture, value: devices count)
        """
        devices_query = DailyDevice.objects.filter(
            pricing_device__is_virtual=False,
            date__gte=start,
            date__lte=end,
            pricing_venture__in=ventures,
        )
        count = devices_query.values('pricing_venture').annotate(
            count=Count('id')
        )
        result = dict([(dc['pricing_venture'], dc['count']) for dc in count])
        return result

    @memoize(skip_first=True)
    def _get_total_devices_count(self, start, end, excluded_ventures):
        """
        Returns total count of devices in period of time (sum of DailyDevices).

        :rtype: int
        """
        devices_query = DailyDevice.objects.filter(
            pricing_device__is_virtual=False,
            date__gte=start,
            date__lte=end,
        ).exclude(
            pricing_venture__isnull=True
        ).exclude(
            pricing_venture__in=excluded_ventures,
        )
        return devices_query.aggregate(count=Count('id')).get('count', 0)

    def _get_cores_usage_type(self):
        """
        Physical CPU cores usage type definition
        """
        return UsageType.objects.get_or_create(
            name="Physical CPU cores",
        )[0]

    @memoize(skip_first=True)
    def _get_cores_count_by_venture(self, start, end, ventures):
        """
        Returns (total) cores count per venture between start and end.
        Notice that total cores count is sum of all DailyUsage for every
        venture - not average cores count.

        :rtype: dict (key: venture, value: cores count)
        """
        cores_query = DailyUsage.objects.filter(
            type=self._get_cores_usage_type(),
            date__gte=start,
            date__lte=end,
            pricing_venture__in=ventures
        )
        count = cores_query.values('pricing_venture').annotate(
            count=Sum('value')
        )
        result = dict([(cc['pricing_venture'], cc['count']) for cc in count])
        return result

    @memoize(skip_first=True)
    def _get_total_cores_count(self, start, end, excluded_ventures):
        """
        Returns total count of cores in period of time (sum of DailyUsage).

        :rtype: int
        """
        cores_query = DailyUsage.objects.filter(
            type=self._get_cores_usage_type(),
            date__gte=start,
            date__lte=end,
        ).exclude(
            pricing_venture__isnull=True
        ).exclude(
            pricing_venture__in=excluded_ventures,
        )
        return cores_query.aggregate(
            cores_count=Sum('value')
        ).get('cores_count', 0)

    def _get_percent_from_costs(
        self,
        ventures_costs,
        total_cost,
        percent_key,
        cost_key
    ):
        """
        Calculates venture percent of total cost, according to it's cost
        """
        for v in ventures_costs.values():
            if isinstance(v[cost_key], (D, int, float)) and total_cost:
                v[percent_key] = v[cost_key] / total_cost
            else:
                v[percent_key] = 0

    def _get_team_time_cost_per_venture(
        self,
        team,
        usage_type,
        start,
        end,
        ventures,
        forecast=False,
        no_price_msg=False,
        daily_cost=None,
        **kwargs
    ):
        """
        Calculates cost of teams, that are billed by spent time for each
        venture. If daily_cost is passed, it's used instead of calculated
        daily cost from total cost.

        Main idea:
        for every period in which cost is defined for team
            for every not-overlaping daterange of percent per team
                calculate cost of team time per venture in this period of time

        Notice that:
        * total cost is treated as sum of equal daily cost (assumed, that in
            period of time daily cost is the same)
        * assumed, that in period of time percent of time spent to venture is
            equal for each day
        """

        result = defaultdict(lambda: defaultdict(int))
        ventures_ids = set([v.id for v in ventures])
        cost_key = 'ut_{0}_team_{1}_cost'.format(usage_type.id, team.id)
        percent_key = 'ut_{0}_team_{1}_percent'.format(usage_type.id, team.id)
        # check if price is undefined for any time between start and end
        price_undefined = no_price_msg and self._incomplete_price(
            usage_type,
            start,
            end,
            team=team,
        )
        total_cost = 0

        def add_subcosts(sstart, send, cost, percentage):
            """
            Helper to add subcost for every venture for single, integral period
            of time.
            """
            # for every venture-percentage division defined for period of time
            for venture, percent in percentage.items():
                if venture in ventures_ids:
                    # store daily percent to calculate average percent
                    if price_undefined:
                        result[venture][cost_key] = price_undefined
                    else:
                        result[venture][cost_key] += cost * D(percent) / 100

        usageprices = team.usageprice_set.filter(
            start__lte=end,
            end__gte=start,
            type=usage_type
        )
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
                total_cost += period_daily_cost * ((tcend - tcstart).days + 1)
                dateranges_percentage = self._get_team_dateranges_percentage(
                    tcstart,
                    tcend,
                    team
                )
                for (dpstart, dpend), percent in dateranges_percentage.items():
                    subcost = period_daily_cost * ((dpend - dpstart).days + 1)
                    add_subcosts(dpstart, dpend, subcost, percent)
        else:
            # if price was not provided at all
            percentage = TeamVenturePercent.objects.filter(
                team_daterange__team=team,
                team_daterange__start__lte=end,
                team_daterange__end__gte=start,
                venture__in=ventures,
            )
            percentage = dict([(p.venture.id, p.percent) for p in percentage])
            add_subcosts(start, end, 0, percentage)

        self._get_percent_from_costs(result, total_cost, percent_key, cost_key)

        return result

    def _exclude_ventures(self, team, ventures):
        if team.excluded_ventures.count():
            ventures = list(set(ventures) - set(team.excluded_ventures.all()))
        return ventures

    def _get_team_func_cost_per_venture(
        self,
        team,
        usage_type,
        start,
        end,
        ventures,
        forecast=False,
        no_price_msg=False,
        daily_cost=None,
        funcs=None,
        **kwargs
    ):
        """
        Calculates cost of used resources (i.e. devices, cores) for each
        venture in period of time. If daily_cost is passed, it's used instead
        of calculated daily cost from total cost.

        Main idea:
        for every period in which cost is defined for team:
            calculate daily cost
            for every resource:
                get total count of resource usage per venture
                calculate venture cost based od cost in period of time and
                    resource usage

        Passed functions (funcs) should be 3-elements tuple:
        (resource_usage_per_venture_function, resource_total_usage_function,
        result_dict_key (to store usages of venture)).

        Notice that:
        * if there is more than one funcs (resources), that total cost is
            distributed in equal parts to all resources (1/n)
        """

        result = defaultdict(lambda: defaultdict(int))
        cost_key = 'ut_{0}_team_{1}_cost'.format(usage_type.id, team.id)
        percent_key = 'ut_{0}_team_{1}_percent'.format(usage_type.id, team.id)
        price_undefined = no_price_msg and self._incomplete_price(
            usage_type,
            start,
            end,
            team=team,
        )
        funcs = funcs or []
        total_cost = 0
        ventures = self._exclude_ventures(team, ventures)

        def add_subcosts(sstart, send, cost):
            for count_func, total_count_func in funcs:
                count_per_venture = count_func(sstart, send, ventures)
                total = total_count_func(
                    sstart,
                    send,
                    team.excluded_ventures.all(),
                )
                # if there is more than one resource, calculate 1/n of total
                # cost
                cost_part = cost / D(len(funcs))
                for venture, count in count_per_venture.items():
                    if price_undefined:
                        result[venture][cost_key] = price_undefined
                    elif not total:
                        result[venture][cost_key] = D(0)
                    else:
                        result[venture][cost_key] += (
                            cost_part * D(count) / D(total)
                        )

        usageprices = team.usageprice_set.filter(
            start__lte=end,
            end__gte=start,
            type=usage_type
        )
        if usageprices:
            for team_cost in usageprices:
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

    def _get_team_devices_cores_cost_per_venture(
        self,
        team,
        usage_type,
        *args,
        **kwargs
    ):
        """
        Calculates costs of devices and cores usage per venture.
        """
        return self._get_team_func_cost_per_venture(
            team=team,
            usage_type=usage_type,
            funcs=(
                (
                    self._get_devices_count_by_venture,
                    self._get_total_devices_count,
                ),
                (
                    self._get_cores_count_by_venture,
                    self._get_total_cores_count,
                ),
            ),
            *args,
            **kwargs
        )

    def _get_team_devices_cost_per_venture(
        self,
        team,
        usage_type,
        *args,
        **kwargs
    ):
        """
        Calculates costs of devices usage per venture.
        """
        return self._get_team_func_cost_per_venture(
            team=team,
            usage_type=usage_type,
            funcs=(
                (
                    self._get_devices_count_by_venture,
                    self._get_total_devices_count,
                ),
            ),
            *args,
            **kwargs
        )

    def _get_team_distributed_cost_per_venture(
        self,
        team,
        usage_type,
        start,
        end,
        ventures,
        forecast=False,
        no_price_msg=False,
        **kwargs
    ):
        """
        Calculates cost of team, which cost is based on venture cost for other
        teams (proprotionally to members count of other teams).

        Main idea:
        for every period on which cost is defined for team
            for every period of not-distributed teams members count in main
            period
                for every not-distributed team
                    get team members count in period and it's % among all teams
                    calculate % of distributed team total cost (daily)
                    calculate cost for this team for all ventures,
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
        cost_key = 'ut_{0}_team_{1}_cost'.format(usage_type.id, team.id)
        percent_key = 'ut_{0}_team_{1}_percent'.format(usage_type.id, team.id)
        price_undefined = no_price_msg and self._incomplete_price(
            usage_type,
            start,
            end,
            team=team,
        )

        usageprices = team.usageprice_set.filter(
            start__lte=end,
            end__gte=start,
            type=usage_type
        )
        total_cost = 0

        if usageprices:
            for team_cost in usageprices:
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
                        team_cost_key = 'ut_{0}_team_{1}_cost'.format(
                            usage_type.id,
                            dependent_team.id,
                        )
                        daily_team_cost = daily_cost * members / total_members
                        for venture_info in self._get_team_cost_per_venture(
                            team=dependent_team,
                            start=mcstart,
                            end=mcend,
                            ventures=ventures,
                            usage_type=usage_type,
                            daily_cost=daily_team_cost,
                            forecast=forecast,
                        ).items():
                            venture = venture_info[0]
                            venture_cost = venture_info[1][team_cost_key]
                            if price_undefined:
                                result[venture][cost_key] = price_undefined
                            elif isinstance(venture_cost, (int, D)):
                                result[venture][cost_key] += venture_cost
        else:
            for venture in ventures:
                result[venture.id][cost_key] = price_undefined

        self._get_percent_from_costs(result, total_cost, percent_key, cost_key)

        return result

    def _get_team_average_cost_per_venture(
        self,
        team,
        usage_type,
        start,
        end,
        ventures,
        forecast=False,
        no_price_msg=False,
        **kwargs
    ):
        """
        Calculates team cost according to average of percents of other teams
        costs per ventures.

        For every dependent team (every other, that has billing type different
        than AVERAGE), in period of time for which cost is defined for current
        team, there are costs and percentage division calculated for such a
        dependent team. Calculated percentage division is then added to venture
        'counter' and at the end, total cost of current team is distributed
        according to ventures 'counters' (of percent).
        """
        result = defaultdict(lambda: defaultdict(D))
        teams = self._get_teams_not_average()
        cost_key = 'ut_{0}_team_{1}_cost'.format(usage_type.id, team.id)
        percent_key = 'ut_{0}_team_{1}_percent'.format(usage_type.id, team.id)
        price_undefined = no_price_msg and self._incomplete_price(
            usage_type,
            start,
            end,
            team=team,
        )
        usageprices = team.usageprice_set.filter(
            start__lte=end,
            end__gte=start,
            type=usage_type
        )
        total_cost = 0

        # if any team cost was defined between start and end
        if usageprices:
            for team_cost in usageprices:
                venture_percent = defaultdict(D)
                total_percent = 0
                tcstart = max(start, team_cost.start)
                tcend = min(end, team_cost.end)
                cost = team_cost.forecast_cost if forecast else team_cost.cost
                daily_cost = cost / (
                    (team_cost.end - team_cost.start).days + 1
                )
                period_cost = daily_cost * ((tcend - tcstart).days + 1)
                total_cost += period_cost
                # calculate costs and percent of other teams per venture
                for dependent_team in teams:
                    team_percent_key = 'ut_{0}_team_{1}_percent'.format(
                        usage_type.id,
                        dependent_team.id,
                    )
                    for venture_info in self._get_team_cost_per_venture(
                        team=dependent_team,
                        start=tcstart,
                        end=tcend,
                        ventures=ventures,
                        usage_type=usage_type,
                        forecast=forecast,
                    ).items():
                        venture = venture_info[0]
                        percent = venture_info[1][team_percent_key]
                        venture_percent[venture] += percent
                        total_percent += percent

                # distribute cost of current team according to calculated
                # percent between tcstart and tcend
                for venture, percent in venture_percent.iteritems():
                    if price_undefined:
                        result[venture][cost_key] = price_undefined
                    else:
                        result[venture][cost_key] += (
                            period_cost * percent / total_percent
                        )
        else:
            for venture in ventures:
                result[venture.id][cost_key] = price_undefined

        # calculate percent of total cost per venture
        # sum of percent should be equal to 1
        self._get_percent_from_costs(result, total_cost, percent_key, cost_key)

        return result

    def _get_team_cost_per_venture(self, team, *args, **kwargs):
        """
        Call proper function to calculate team cost, based on team billing type
        """
        functions = {
            'TIME': self._get_team_time_cost_per_venture,
            'DISTRIBUTE': self._get_team_distributed_cost_per_venture,
            'DEVICES_CORES': self._get_team_devices_cores_cost_per_venture,
            'DEVICES': self._get_team_devices_cost_per_venture,
            'AVERAGE': self._get_team_average_cost_per_venture,
        }
        func = functions.get(team.billing_type)
        if func:
            logger.debug("Get team {0} costs".format(team))
            return func(team, *args, **kwargs)
        logger.warning('No handle method for billing type {0}'.format(
            team.billing_type
        ))
        return {}

    def total_cost(self, *args, **kwargs):
        costs = self.costs(*args, **kwargs)
        total_cost_key = 'ut_{0}_total_cost'.format(kwargs['usage_type'].id)
        return sum([u[total_cost_key] for u in costs.values()])

    def costs(self, **kwargs):
        """
        Calculates teams costs.
        """
        logger.debug("Get teams usages")
        teams = self._get_teams()
        total_cost_column = len(teams) > 1
        total_cost_key = 'ut_{0}_total_cost'.format(kwargs['usage_type'].id)
        result = defaultdict(lambda: defaultdict(int))
        for team in teams:
            team_report = self._get_team_cost_per_venture(team, **kwargs)
            for venture, venture_data in team_report.items():
                for key, value in venture_data.items():
                    result[venture][key] = value
                    if (total_cost_column and key.endswith('cost')
                       and isinstance(value, (int, D))):
                        result[venture][total_cost_key] += value
        return result

    def schema(self, usage_type, **kwargs):
        """
        Build schema for this usage.

        :returns dict: schema for usage
        """
        logger.debug("Get teams schema")
        schema = OrderedDict()
        teams = self._get_teams()
        usage_type_id = usage_type.id
        for team in teams:
            if team.show_percent_column:
                schema['ut_{0}_team_{1}_percent'.format(
                    usage_type_id,
                    team.id,
                )] = {
                    'name': _("{0} - {1} %".format(
                        usage_type.name,
                        team.name,
                    )),
                    'rounding': PERCENT_PRECISION,
                }
            schema['ut_{0}_team_{1}_cost'.format(usage_type_id, team.id)] = {
                'name': _("{0} - {1} cost".format(
                    usage_type.name,
                    team.name,
                )),
                'currency': True,
                'total_cost': len(teams) == 1,
            }
        if len(teams) > 1:
            schema['ut_{0}_total_cost'.format(usage_type_id)] = {
                'name': _("{0} total cost".format(usage_type.name)),
                'currency': True,
                'total_cost': True,
            }
        return schema
