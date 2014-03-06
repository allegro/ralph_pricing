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

from ralph_pricing.models import Team as TeamModel
from ralph_pricing.plugins.base import register
from ralph_pricing.plugins.reports.usage import UsageBasePlugin


logger = logging.getLogger(__name__)


@register(chain='reports')
class Team(UsageBasePlugin):
    @memoize(skip_first=True)
    def _get_teams(self):
        return TeamModel.objects.filter(show_in_report=True)

    @memoize(skip_first=True)
    def _get_teams_distrubuted_to_others(self):
        return TeamModel.objects.filter(
            show_in_report=True,
            billing_type='DISTRIBUTE',
        )

    @memoize(skip_first=True)
    def _get_teams_not_distributes_to_others(self):
        return TeamModel.objects.filter(show_in_report=True).exclude(
            billing_type='DISTRIBUTE'
        )

    def _get_team_time_cost_per_venture(
        self,
        team,
        usage_type,
        start,
        end,
        ventures,
        **kwargs
    ):
        # for every period in which cost is defined for team
            # for every not-overlaping daterange of percent per team
                # calculate % of daily cost * count of days in period
        return {}

    def _get_team_devices_cores_cost_per_venture(
        self,
        team,
        usage_type,
        start,
        end,
        ventures,
        **kwargs
    ):
        # for every period in which cost is defined for team
            # get total count of devices and cores per venture
            # calculate % of total cost based on devices and cores proportions
        return {}

    def _get_team_devices_cost_per_venture(
        self,
        team,
        usage_type,
        start,
        end,
        ventures,
        **kwargs
    ):
        # for every period in which cost is defined for team
            # get total count of devices per venture
            # calculate % of total cost based on devices proportions
        return {}

    def _get_team_distributed_cost_per_venture(
        self,
        team,
        usage_type,
        start,
        end,
        ventures,
        **kwargs
    ):
        # for every period on which cost is defined for team
            # for every period of not-distributed teams members count
                # for every not-distributed team
                    # get team members count in period and it's % among all teams
                    # calculate % of distributed team total cost (daily)
        return {}

    def _get_team_cost_per_venture(self, team, *args, **kwargs):
        functions = {
            'TIME': self._get_team_time_cost_per_venture,
            'DISTRIBUTE': self._get_team_distributed_cost_per_venture,
            'DEVICES_CORES': self._get_team_devices_cores_cost_per_venture,
            'DEVICES': self._get_team_devices_cost_per_venture,
        }
        func = functions.get(team.billing_type)
        if func:
            return func(team, *args, **kwargs)
        logger.warning('No handle method for billing type {0}'.format(team.billing_type))
        return {}

    def usages(self, *args, **kwargs):
        teams = self._get_teams()
        total_cost_column = len(teams) > 1
        total_cost_key = 'teams_total_cost'
        result = defaultdict(lambda: defaultdict(int))
        for team in teams:
            team_report = self._get_team_cost_per_venture(team, *args, **kwargs)
            for venture, venture_data in team_report.items():
                for key, value in venture_data.items():
                    result[venture][key] += value
                    if total_cost_column and key.endswith('cost'):
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
