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
    Warehouse,
)

class DataForReportValidationError(Exception):
    """`errors` should be a list containing error msgs given by Validator."""

    def __init__(self, message, errors):
        setattr(self, 'errors', errors)
        Exception.__init__(self, message)


class Validator(object):

    def __init__(self, date, forecast):
        self.date = date
        self.forecast = forecast
        self.errors = []

        self.active_teams = Team.objects.filter(active=True)
        self.active_usage_types = UsageType.objects.filter(active=True)

    # XXX And also, maybe check extra costs and dynamic extra costs..?
    def _check_for_required_costs_and_prices(self):
        """There should be no active UsageType without all required
        costs/prices."""
        q = {'start__lte': self.date, 'end__gte': self.date}
        for ut in self.active_usage_types:
            q.update({'type': ut})
            field = 'cost' if not self.forecast else 'forecast_cost'
            sum_cost = UsagePrice.objects.filter(**q).aggregate(
                s=Sum(field)
            )['s']
            field = 'price' if not self.forecast else 'forecast_price'
            sum_price = UsagePrice.objects.filter(**q).aggregate(
                s=Sum(field)
            )['s']

            if not sum_cost or not sum_price:
                self.errors.append(
                    'no {}cost(s) or price(s) defined for usage type "{}"'
                    .format('forecast ' if self.forecast else '', ut.name)
                )

    def _check_for_usage_prices_by_warehouse(self):
        """There should be no base UsageType with by_warehouse field set to
        True, where UsagePrices for a given day are defined only for some (i.e.
        not all) active Warehouses.
        """
        num_active_warehouses = Warehouse.objects.filter(
            show_in_report=True
        ).count()
        for ut in self.active_usage_types.filter(
                usage_type='BU', by_warehouse=True
        ):
            warehouses = UsagePrice.objects.filter(
                type=ut,
                warehouse__show_in_report=True,
                start__lte=self.date,
                end__gte=self.date,
            ).values_list('warehouse', flat=True)
            num_warehouses = len(set(warehouses))
            if num_warehouses != num_active_warehouses:
                self.errors.append(
                    'no usage price(s) for {} of {} active warehouse(s) '
                    'defined for usage type "{}"'.format(
                        num_active_warehouses - num_warehouses,
                        num_active_warehouses,
                        ut.name,
                    )
                )

    def _check_team_costs(self):
        """There should be no active team with undefined/zero costs on given
        day.
        """
        if self.forecast:
            q = 'forecast_cost'
        else:
            q = 'cost'
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
        """There should be no active team with time allocated that doesn't sum
        up to 100%.
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
        """There should be no active usage type without usage(s) saved for
        a given day.
        """
        # XXX(mkurek): only active or maybe active *and* linked to some
        # pricing service..?
        for ut in self.active_usage_types:
            if not DailyUsage.objects.filter(date=self.date, type=ut).exists():
                self.errors.append(
                    'no usage(s) uploaded for usage type "{}"'.format(ut.name)
                )

    def _check_usage_types_percent(self):
        """There should be no usage type where percents do not sum up to 100%.
        """
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
        """There should be no costs that are already accepted."""
        q = {'date': self.date}
        if self.forecast:
            q.update({'forecast_accepted': True})
        else:
            q.update({'accepted': True})
        if CostDateStatus.objects.filter(**q).exists():
            self.errors.append('costs already accepted')

    def _check_for_cycles(self):
        """There should be no cycles between pricing services operating on
        flexible prices.
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
        self._check_for_usage_prices_by_warehouse()
        self._check_team_costs()
        self._check_team_time_allocations()
        self._check_usage_types()
        self._check_usage_types_percent()
        self._check_for_accepted_costs()
        self._check_for_cycles()
        if self.errors:
            raise DataForReportValidationError(
                'Errors detected for day {:%Y-%m-%d}'.format(self.date),
                errors=self.errors
            )
