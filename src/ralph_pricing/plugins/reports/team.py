# -*- coding: utf-8 -*-

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
    TeamMembersCount,
    UsageType
)
from ralph_pricing.plugins.base import register
from ralph_pricing.plugins.reports.usage import UsageBasePlugin


logger = logging.getLogger(__name__)


@register(chain='reports')
class Team(UsageBasePlugin):
    @memoize(skip_first=True)
    def _get_teams(self):
        """
        Returns all available teams, that should be visible on report
        """
        return TeamModel.objects.filter(show_in_report=True)

    @memoize(skip_first=True)
    def _get_teams_distrubuted_to_others(self):
        """
        Returns all teams that have billing type DISTRIBUTE
        """
        return TeamModel.objects.filter(
            show_in_report=True,
            billing_type='DISTRIBUTE',
        )

    @memoize(skip_first=True)
    def _get_teams_not_distributes_to_others(self):
        """
        Returns all teams that have billing type different than DISTRIBUTE
        """
        return TeamModel.objects.filter(show_in_report=True).exclude(
            billing_type='DISTRIBUTE'
        )

    def _get_team_dateranges_percentage(self, start, end, team):
        percentage = team.teamventurepercent_set.filter(
            start__lte=end,
            end__gte=start,
        )
        dates = defaultdict(lambda: defaultdict(list))
        for percent in percentage:
            dates[max(percent.start, start)]['start'].append(percent)
            dates[min(percent.end, end)]['end'].append(percent)

        result = {}
        current_percentage = {}
        current_start = None

        # iterate through dict items sorted by key (date)
        for date, percent in sorted(dates.items(), key=lambda k: k[0]):
            if percent['start']:
                current_start = date
            for tvp in percent['start']:
                current_percentage[tvp.venture.id] = tvp.percent

            if percent['end']:
                result[(current_start, date)] = current_percentage.copy()
            for tvp in percent['end']:
                del current_percentage[tvp.venture.id]
        return result

    def _get_teams_dateranges_members_count(self, start, end, teams):
        members_count = TeamMembersCount.objects.filter(
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
    def _get_devices_count_by_venture(self, start, end, ventures):
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
    def _get_total_devices_count(self, start, end, ventures):
        devices_query = DailyDevice.objects.filter(
            pricing_device__is_virtual=False,
            date__gte=start,
            date__lte=end,
            pricing_venture__in=ventures,
        )
        return devices_query.aggregate(count=Count('id')).get('count', 0)

    def _get_cores_usage_type(self):
        return UsageType.objects.get_or_create(
            name="Physical CPU cores",
        )[0]

    @memoize(skip_first=True)
    def _get_cores_count_by_venture(self, start, end, ventures):
        cores_query = DailyUsage.objects.filter(
            type=self._get_cores_usage_type(),
            date__gte=start,
            date__lte=end,
            pricing_venture__in=ventures
        )
        count = cores_query.values('pricing_venture').aggregate(
            count=Sum('value')
        )
        result = dict([(cc['pricing_venture'], cc['count']) for cc in count])
        return result

    @memoize(skip_first=True)
    def _get_total_cores_count(self, start, end, ventures):
        cores_query = DailyUsage.objects.filter(
            type=self._get_cores_usage_type(),
            date__gte=start,
            date__lte=end,
            pricing_venture__in=ventures
        )
        return cores_query.aggregate(
            cores_count=Sum('value')
        )

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
        # for every period in which cost is defined for team
            # for every not-overlaping daterange of percent per team
                # calculate % of daily cost * count of days in period
        result = defaultdict(lambda: defaultdict(int))
        team_cost_key = 'team_{0}_cost'.format(team.id)
        team_percent_key = 'team_{0}_percent'.format(team.id)
        total_days = (end - start).days + 1
        price_undefined = no_price_msg and self._incomplete_price(
            usage_type,
            start,
            end,
            team=team,
        )

        def add_subcosts(sstart, send, cost):
            percentage = team.teamventurepercent_set.filter(
                start__lte=send,
                end__gte=sstart,
                venture__in=ventures,
            )
            days = (send - sstart).days + 1
            for percent in percentage:
                venture = percent.venture.id
                result[venture][team_percent_key] += percent.percent * days
                if price_undefined:
                    result[venture][team_cost_key] = price_undefined
                else:
                    result[venture][team_cost_key] += cost * D(percent.percent) / 100

        usageprices = team.usageprice_set.filter(
            start__lte=end,
            end__gte=start,
            type=usage_type
        )
        if usageprices:
            for team_cost in usageprices:
                cost = team_cost.forecast_cost if forecast else team_cost.cost
                tcstart = max(start, team_cost.start)
                tcend = min(end, team_cost.end)
                if not daily_cost:
                    daily_cost_in_period = cost / ((team_cost.end - team_cost.start).days + 1)
                else:
                    daily_cost_in_period = daily_cost
                dateranges_percentage = self._get_team_dateranges_percentage(
                    tcstart,
                    tcend,
                    team
                )
                for (dpstart, dpend), percentage in dateranges_percentage.items():
                    subcost = daily_cost_in_period * ((dpend - dpstart).days + 1)
                    add_subcosts(dpstart, dpend, subcost)
        else:
            add_subcosts(start, end, 0)

        for v in result.values():
            v[team_percent_key] = round(v[team_percent_key] / total_days, 2)

        return result

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
        # for every period in which cost is defined for team
            # get total count of devices and cores per venture
            # calculate % of total cost based on devices and cores proportions
        result = defaultdict(lambda: defaultdict(int))
        cost_key = 'team_{0}_cost'.format(team.id)
        total_days = (end - start).days + 1
        price_undefined = no_price_msg and self._incomplete_price(
            usage_type,
            start,
            end,
            team=team,
        )
        funcs = funcs or []

        def add_subcosts(sstart, send, cost):
            for count_func, total_count_func, key in funcs:
                count_per_venture = count_func(sstart, send, ventures)
                total = total_count_func(sstart, send, ventures)
                cost_part = cost / D(len(funcs))
                for venture, count in count_per_venture.items():
                    if price_undefined:
                        result[venture][cost_key] = price_undefined
                    else:
                        result[venture][cost_key] += cost_part * count / total
                    result[venture][key] += count

        usageprices = team.usageprice_set.filter(
            start__lte=end,
            end__gte=start,
            type=usage_type
        )
        if usageprices:
            for team_cost in usageprices:
                cost = team_cost.forecast_cost if forecast else team_cost.cost
                if not daily_cost:
                    daily_cost_in_period = cost / ((team_cost.end - team_cost.start).days + 1)
                else:
                    daily_cost_in_period = daily_cost

                tcstart = max(start, team_cost.start)
                tcend = min(end, team_cost.end)
                cost = daily_cost_in_period * ((tcend - tcstart).days + 1)
                add_subcosts(tcstart, tcend, cost)
        else:
            add_subcosts(start, end, 0)

        for v in result.values():
            for f in funcs:
                v[f[2]] = round(v[f[2]] / total_days, 2)
        return result

    def _get_team_devices_cores_cost_per_venture(self, team, *args, **kwargs):
        return self._get_team_func_cost_per_venture(
            team=team,
            funcs = (
                (
                    self._get_devices_count_by_venture,
                    self._get_total_devices_count,
                    'team_{0}_devices'.format(team.id)
                ),
                (
                    self._get_cores_count_by_venture,
                    self._get_total_cores_count,
                    'team_{0}_cores'.format(team.id)
                ),
            ),
            *args,
            **kwargs
        )

    def _get_team_devices_cost_per_venture(self, team, *args, **kwargs):
        return self._get_team_func_cost_per_venture(
            team=team,
            funcs=(
                (
                    self._get_devices_count_by_venture,
                    self._get_total_devices_count,
                    'team_{0}_devices'.format(team.id)
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
        # for every period on which cost is defined for team
            # for every period of not-distributed teams members count
                # for every not-distributed team
                    # get team members count in period and it's % among all teams
                    # calculate % of distributed team total cost (daily)
        result = defaultdict(lambda: defaultdict(D))
        teams = self._get_teams_not_distributes_to_others()
        teams_by_id = dict([(t.id, t) for t in teams])
        team_cost_key = 'team_{0}_cost'.format(team.id)
        price_undefined = no_price_msg and self._incomplete_price(
            usage_type,
            start,
            end,
            team=team,
        )

        usageprices = team.usageprice_set.filter(start__lte=end, end__gte=start, type=usage_type)

        if usageprices:
            for team_cost in usageprices:
                cost = team_cost.forecast_cost if forecast else team_cost.cost
                tcstart = max(start, team_cost.start)
                tcend = min(end, team_cost.end)
                daily_cost = cost / ((team_cost.end - team_cost.start).days + 1)

                for members_count in self._get_teams_dateranges_members_count(
                    tcstart, tcend, teams
                ).items():
                    mcstart, mcend = members_count[0]
                    team_members_count = members_count[1]
                    total_members = sum(team_members_count.values())
                    for team_id, members in team_members_count.items():
                        dependent_team = teams_by_id[team_id]
                        team_key = 'team_{0}_cost'.format(dependent_team.id)
                        daily_team_cost = daily_cost * members / total_members
                        for venture, venture_cost in self._get_team_cost_per_venture(
                            team=dependent_team,
                            start=mcstart,
                            end=mcend,
                            ventures=ventures,
                            usage_type=usage_type,
                            daily_cost=daily_team_cost,
                            forecast=forecast,
                        ).items():
                            # logger.debug('Venture {0} cost for team {1} ({2}-{3}): {4}'.format(venture, team_key, mcstart, mcend, venture_cost[team_key]))
                            if price_undefined:
                                result[venture][team_cost_key] = price_undefined
                            elif isinstance(venture_cost[team_key], (int, D)):
                                result[venture][team_cost_key] += venture_cost[team_key]
        else:
            for venture in ventures:
                result[venture.id][team_cost_key] = price_undefined

        return result

    def _get_team_cost_per_venture(self, team, *args, **kwargs):
        functions = {
            'TIME': self._get_team_time_cost_per_venture,
            'DISTRIBUTE': self._get_team_distributed_cost_per_venture,
            'DEVICES_CORES': self._get_team_devices_cores_cost_per_venture,
            'DEVICES': self._get_team_devices_cost_per_venture,
        }
        func = functions.get(team.billing_type)
        if func:
            logger.debug("Get team {0} costs".format(team))
            return func(team, *args, **kwargs)
        logger.warning('No handle method for billing type {0}'.format(team.billing_type))
        return {}

    def usages(self, *args, **kwargs):
        logger.debug("Get teams usages")
        teams = self._get_teams()
        total_cost_column = len(teams) > 1
        total_cost_key = 'teams_total_cost'
        result = defaultdict(lambda: defaultdict(int))
        for team in teams:
            team_report = self._get_team_cost_per_venture(team, *args, **kwargs)
            for venture, venture_data in team_report.items():
                for key, value in venture_data.items():
                    result[venture][key] = value
                    if total_cost_column and key.endswith('cost') and isinstance(value, (int, D)):
                        result[venture][total_cost_key] += value
        return result

    def schema(self, usage_type, **kwargs):
        """
        Build schema for this usage. Format of schema looks like:

        :returns dict: schema for usage
        """
        logger.debug("Get teams schema")
        schema = OrderedDict()
        teams = self._get_teams()
        for team in teams:
            if team.billing_type == 'TIME':
                schema['team_{0}_percent'.format(team.id)] = {
                    'name': _("{0} - {1} %".format(
                        usage_type.name,
                        team.name,
                    ))
                }
            if team.billing_type in ('DEVICES_CORES', 'DEVICES'):
                schema['team_{0}_devices'.format(team.id)] = {
                    'name': _("{0} - {1} devices".format(
                        usage_type.name,
                        team.name,
                    ))
                }
            if team.billing_type == 'DEVICES_CORES':
                schema['team_{0}_cores'.format(team.id)] = {
                    'name': _("{0} - {1} cores".format(
                        usage_type.name,
                        team.name,
                    ))
                }

            schema['team_{0}_cost'.format(team.id)] = {
                'name': _("{0} - {1} cost".format(
                    usage_type.name,
                    team.name,
                )),
                'currency': True,
                'total_cost': len(teams) == 1,
            }
        if len(teams) > 1:
            schema['teams_total_cost'] = {
                'name': _("Teams total cost"),
                'currency': True,
                'total_cost': True,
            }
        return schema
