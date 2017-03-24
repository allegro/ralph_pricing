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
    PricingServicePlugin,
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

    # XXX And also, maybe check extra costs and dynamic extra costs.
    def _check_for_required_costs_and_prices(self):
        """Are all required costs/prices (for *active* usages, teams etc.)
        present?
        """
        if self.forecast:
            q = 'forecast_cost'
        else:
            q = 'cost'
        # TODO(xor-xor): Handle costs *and* prices here.
        # XXX(mkurek) I gues that we need to differentiate UsagePrices here by
        # DC/Warehouse, right?

        for ut in self.active_usage_types:
            sum_ = UsagePrice.objects.filter(
                type=ut,
                start__lte=self.date,
                end__gte=self.date,
            ).aggregate(s=Sum(q))['s']
            if not sum_:
                self.errors.append(
                    'no {}(s) defined for usage type "{}"'
                    .format(' '.join(q.split('_')), ut.name)
                )

        for team in self.active_teams:
            sum_ = TeamCost.objects.filter(
                team=team,
                start__lte=self.date,
                end__gte=self.date,
            ).aggregate(s=Sum(q))['s']
            if not sum_:
                self.errors.append(
                    'no {}(s) defined for team "{}"'
                    .format(' '.join(q.split('_')), team.name)
                )

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
        for ps in PricingService.objects.filter(active=True).exclude(
            plugin_type=PricingServicePlugin.pricing_service_fixed_price_plugin
        ):
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
        self._check_for_required_costs_and_prices()
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
