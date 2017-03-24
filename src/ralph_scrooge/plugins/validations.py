# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings
from django.db.models import Sum

from ralph_scrooge.utils.cycle_detector import detect_cycles
from ralph_scrooge.models import (
    CostDateStatus,
    DailyUsage,
    PricingService,
    ServiceUsageTypes,
    Team,
    TeamCost,
    TeamServiceEnvironmentPercent,
    UsagePrice,
    UsageType,
)


class Validator(object):

    def __init__(self, date, forecast):
        self.date = date
        self.forecast = forecast
        self.errors = []

        self.active_teams = Team.objects.filter(active=True)
        self.active_usage_types = UsageType.objects.filter(active=True)

    def _check_for_required_costs(self):  # XXX or rather prices..?
        """Are all required costs (for *active* usages, teams etc.) present?"""

        for ut in self.active_usage_types:
            if not UsagePrice.objects.filter(
                type=ut,
                start__lte=self.date,
                end__gte=self.date,
            ).exists():
                self.errors.append(
                    'no price(s) defined for usage type "{}"'.format(ut.name)
                )
        for team in self.active_teams:
            if not TeamCost.objects.filter(
                team=team,
                start__lte=self.date,
                end__gte=self.date,
            ):
                self.errors.append(
                    'no cost(s) defined for team "{}"'.format(team.name)
                )

        # XXX And also, maybe check extra costs and dynamic extra costs.

        # XXX(mkurek): What about usage prices and team costs which are
        # defined, but are equal to 0..?

        # TODO(xor-xor): Handle forecast_cost here as well when it will
        # become clear what to do with costs == 0.

    def _check_team_time_allocations(self):
        """Does every *active* team have its time allocated and does it sum up
        to 100%?
        """
        for team in self.active_teams:
            perc = TeamServiceEnvironmentPercent.objects.filter(
                team_cost__team=team,
                team_cost__start__lte=self.date,
                team_cost__end__gte=self.date,
            )
            sum_ = sum([p.percent for p in perc])
            if abs(sum_ - 100) > settings.PERCENT_DIFF_EPSILON:
                self.errors.append(
                    'time allocated for team "{}" does not sum up to 100% '
                    '(it\'s {}%)'
                    .format(team.name, sum_)
                )

    def _check_usage_types(self):
        """Does every *active* usage type have any usages saved for a given
        day?
        """
        # XXX(mkurek): only active or maybe active *and* linked to some
        # pricing service..?
        for ut in self.active_usage_types:
            if not DailyUsage.objects.filter(date=self.date, type=ut).exists():
                self.errors.append(
                    'no usage(s) uploaded for usage type "{}"'.format(ut.name)
                )

    def _check_usage_types_percent(self):
        """Does every usage type which operates on percents sums up to 100%?"""
        for ps in PricingService.objects.filter(active=True):
            percent_sum = ServiceUsageTypes.objects.filter(
                usage_type__in=ps.usage_types.filter(active=True),
                start__lte=self.date,
                end__gte=self.date,
            ).aggregate(s=Sum('percent'))['s']
            if abs(percent_sum - 100) > settings.PERCENT_DIFF_EPSILON:
                self.errors.append(
                    'usage types for pricing service "{}" does not sum up to '
                    '100% (it\'s {}%)'.format(ps.name, percent_sum)
                )

    def _check_for_accepted_costs(self):
        """Are there any costs that are accepted already? (if yes, report an
        error)
        """
        q = {'date': self.date}
        if self.forecast:
            q.update({'forecast_accepted': True})
        else:
            q.update({'accepted': True})
        if CostDateStatus.objects.filter(**q).exists():
            self.errors.append('costs already accepted')

    def _check_for_cycles(self):
        """Are there any cycles between pricing services operating on flexible
        prices? (if yes, report an error)
        """
        cycles = detect_cycles(self.date)
        if cycles:
            cycles_ = []
            for c in cycles:
                c_str = '->'.join(map(lambda ps: ps.symbol, c))
                cycles_.append(c_str)
            self.errors.append(
                'cycle(s) detected: {}'.format(', '.join(cycles_))
            )

    def validate(self):
        self._check_for_required_costs()
        self._check_team_time_allocations()
        self._check_usage_types()
        self._check_usage_types_percent()
        self._check_for_accepted_costs()
        self._check_for_cycles()
        if self.errors:
            raise Exception(
                'Errors detected for day {:%Y-%m-%d}: {}.'
                .format(self.date, '; '.join(self.errors))
            )
