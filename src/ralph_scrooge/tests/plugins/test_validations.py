# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test.utils import override_settings

from ralph_scrooge.models import (
    PricingServicePlugin,
    ServiceUsageTypes,
    Warehouse,
)
from ralph_scrooge.plugins.validations import DataForReportValidator
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import (
    CostDateStatusFactory,
    DailyUsageFactory,
    PricingServiceFactory,
    ServiceUsageTypesFactory,
    TeamFactory,
    TeamCostFactory,
    TeamServiceEnvironmentPercentFactory,
    UsagePriceFactory,
    UsageTypeFactory,
    WarehouseFactory,
)

FIXED_PRICE_PLUGIN = PricingServicePlugin.pricing_service_fixed_price_plugin
UNIVERSAL_PLUGIN = PricingServicePlugin.pricing_service_plugin
PERCENT_DIFF_EPSILON = 0.01


class TestDataForReportValidations(ScroogeTestCase):

    def setUpHelper(self):
        self.date_start = datetime.datetime(2017, 3, 1).date()
        self.date_end = datetime.datetime(2017, 3, 31).date()
        self.date_kwargs = {'start': self.date_start, 'end': self.date_end}
        # All validations performed by DataForReportValidator operate on single
        # days.
        self.day = datetime.datetime(2017, 3, 29).date()
        self.validator = DataForReportValidator(
            self.day, forecast=self.forecast
        )

    def setUp(self):
        self.forecast = False
        self.setUpHelper()

    def test_if_active_usage_types_without_all_required_costs_or_prices_are_reported(self):  # noqa: E501
        ps1 = PricingServiceFactory(plugin_type=FIXED_PRICE_PLUGIN)
        ps2 = PricingServiceFactory(plugin_type=FIXED_PRICE_PLUGIN)

        ut1, ut2 = UsageTypeFactory.create_batch(2)
        if self.forecast:
            UsagePriceFactory(type=ut1, forecast_cost=10, **self.date_kwargs)
        else:
            UsagePriceFactory(type=ut1, cost=10, **self.date_kwargs)
        UsagePriceFactory(type=ut2, **self.date_kwargs)

        # ps1(ut1) - OK b/c ut1 has cost defined
        ServiceUsageTypes.objects.create(
            usage_type=ut1,
            pricing_service=ps1,
            **self.date_kwargs
        )

        # ps2 (ut1, ut2) - NOT OK b/c ut2 doesn't have a price or cost
        ServiceUsageTypes.objects.create(
            usage_type=ut1,
            pricing_service=ps2,
            **self.date_kwargs
        )
        ServiceUsageTypes.objects.create(
            usage_type=ut2,
            pricing_service=ps2,
            **self.date_kwargs
        )

        self.validator._check_for_required_costs_and_prices()
        self.assertEqual(len(self.validator.errors), 1)
        self.assertIn(ut2.name, self.validator.errors[0])

    def test_if_base_usage_types_calculated_by_warehouse_are_reported_when_prices_for_some_warehouses_are_missing(self):  # noqa: E501
        Warehouse.objects.all().delete()  # remove objs from fixtures
        w1, w2 = WarehouseFactory.create_batch(2)
        for w in [w1, w2]:
            w.show_in_report = True
            w.save()
        self.assertEqual(Warehouse.objects.count(), 2)

        ut1, ut2 = UsageTypeFactory.create_batch(2)
        for ut in [ut1, ut2]:
            ut.usage_type = 'BU'
            ut.by_warehouse = True
            ut.save()

        # ut1 is OK b/c it has UsagePrices for all warehouses
        # (btw, costs/prices - i.e. their values - doesn't matter here at all)
        UsagePriceFactory(type=ut1, warehouse=w1, **self.date_kwargs)
        UsagePriceFactory(type=ut1, warehouse=w2, **self.date_kwargs)

        # ut2 is NOT OK b/c it has UsagePrice for only one warehouse
        UsagePriceFactory(type=ut2, warehouse=w2, **self.date_kwargs)

        self.validator._check_for_usage_prices_by_warehouse()
        self.assertEqual(len(self.validator.errors), 1)
        self.assertIn('1 of 2 active warehouse(s)', self.validator.errors[0])

    def test_if_active_teams_with_undefined_or_zero_costs_are_reported(self):
        # t1 is OK b/c it has cost defined
        # t2 is NOT OK b/c it has cost == 0 defined
        # t3 is NOT OK b/c it doesn't have any cost defined
        t1, t2, t3 = TeamFactory.create_batch(3)
        if self.forecast:
            TeamCostFactory(team=t1, forecast_cost=10, **self.date_kwargs)
            TeamCostFactory(team=t2, forecast_cost=0, **self.date_kwargs)
        else:
            TeamCostFactory(team=t1, cost=10, **self.date_kwargs)
            TeamCostFactory(team=t2, cost=0, **self.date_kwargs)

        self.validator._check_team_costs()
        self.assertEqual(len(self.validator.errors), 2)
        all_errors_as_str = '; '.join(self.validator.errors)
        self.assertIn(t2.name, all_errors_as_str)
        self.assertIn(t3.name, all_errors_as_str)

    @override_settings(PERCENT_DIFF_EPSILON=PERCENT_DIFF_EPSILON)
    def test_if_active_teams_with_allocated_time_that_do_not_sum_up_to_100_percent_are_reported(self):  # noqa: E501
        t1, t2 = TeamFactory.create_batch(2)

        # TeamCosts have to be unique on team, start and end - hence these
        # different dates below.
        t1c1 = TeamCostFactory(
            team=t1,
            start=datetime.datetime(2017, 3, 1).date(),
            end=datetime.datetime(2017, 3, 31).date(),
        )
        t1c2 = TeamCostFactory(
            team=t1,
            start=datetime.datetime(2017, 3, 15).date(),
            end=datetime.datetime(2017, 3, 31).date(),
        )

        t2c1 = TeamCostFactory(
            team=t2,
            start=datetime.datetime(2017, 3, 1).date(),
            end=datetime.datetime(2017, 3, 31).date(),
        )
        t2c2 = TeamCostFactory(
            team=t2,
            start=datetime.datetime(2017, 3, 15).date(),
            end=datetime.datetime(2017, 3, 31).date(),
        )

        # t1 is OK b/c its costs sum to 100% (+ epsilon)
        TeamServiceEnvironmentPercentFactory(
            team_cost=t1c1, percent=60
        )
        TeamServiceEnvironmentPercentFactory(
            team_cost=t1c2, percent=(40 + PERCENT_DIFF_EPSILON)
        )

        # t2 is NOT OK b/c its costs do not sum to 100% (+ epsilon)
        TeamServiceEnvironmentPercentFactory(
            team_cost=t2c1, percent=60
        )
        TeamServiceEnvironmentPercentFactory(
            team_cost=t2c2, percent=(40 + 2 * PERCENT_DIFF_EPSILON)
        )

        self.validator._check_team_time_allocations()
        self.assertEqual(len(self.validator.errors), 1)
        self.assertIn(t2.name, self.validator.errors[0])

    def test_if_active_usage_types_without_saved_usages_are_reported(self):
        # ut1 is OK b/c it has DailyUsage for self.day
        ut1 = UsageTypeFactory(usage_type='BU')
        DailyUsageFactory(type=ut1, date=self.day)

        # ut2 is NOT OK b/c it doesn't have DailyUsage for self.day
        ut2 = UsageTypeFactory(usage_type='BU')

        # ut3 is OK b/c it is 'SU' type and it has ServiceUsageType and
        # DailyUsage for self.day
        ut3 = UsageTypeFactory(usage_type='SU')
        ServiceUsageTypesFactory(usage_type=ut3)
        DailyUsageFactory(type=ut3, date=self.day)

        # ut4 is OK b/c it doesn't have ServiceUsageType, so there's no need
        # for checking if it has DailyUsage for self.day
        UsageTypeFactory(usage_type='SU')

        # ut5 is NOT OK b/c it has ServiceUsageType, but it doesn't have
        # DailyUsage for self.day
        ut5 = UsageTypeFactory(usage_type='SU')
        ServiceUsageTypesFactory(usage_type=ut5)

        self.validator._check_usage_types()
        self.assertEqual(len(self.validator.errors), 2)
        all_errors_as_str = '; '.join(self.validator.errors)
        self.assertIn(ut2.name, all_errors_as_str)
        self.assertIn(ut5.name, all_errors_as_str)

    @override_settings(PERCENT_DIFF_EPSILON=PERCENT_DIFF_EPSILON)
    def test_if_pricing_services_with_usage_types_that_together_does_not_sum_up_to_100_percent_are_reported(self):  # noqa: E501
        ut1, ut2 = UsageTypeFactory.create_batch(2)

        # ps1 is OK b/c its UsageTypes sum to 100% (+ epsilon)
        ps1 = PricingServiceFactory(plugin_type=UNIVERSAL_PLUGIN)
        ServiceUsageTypes.objects.create(
            usage_type=ut1,
            pricing_service=ps1,
            percent=60,
            **self.date_kwargs
        )
        ServiceUsageTypes.objects.create(
            usage_type=ut2,
            pricing_service=ps1,
            percent=(40 + PERCENT_DIFF_EPSILON),
            **self.date_kwargs
        )

        # ps2 is NOT OK b/c its UsageTypes do not sum to 100% (+ epsilon)
        ps2 = PricingServiceFactory(plugin_type=UNIVERSAL_PLUGIN)
        ServiceUsageTypes.objects.create(
            usage_type=ut1,
            pricing_service=ps2,
            percent=60,
            **self.date_kwargs
        )
        ServiceUsageTypes.objects.create(
            usage_type=ut2,
            pricing_service=ps2,
            percent=(40 + 2 * PERCENT_DIFF_EPSILON),
            **self.date_kwargs
        )

        # ps3 is NOT OK b/c it doesn't have any UsageType(s) defined
        ps3 = PricingServiceFactory(plugin_type=UNIVERSAL_PLUGIN)

        self.validator._check_usage_types_percent()
        self.assertEqual(len(self.validator.errors), 2)
        all_errors_as_str = '; '.join(self.validator.errors)
        self.assertIn(ps2.name, all_errors_as_str)
        self.assertIn(ps3.name, all_errors_as_str)

    def test_if_costs_that_are_already_accepted_are_reported(self):
        if self.forecast:
            CostDateStatusFactory(date=self.day, forecast_accepted=True)
        else:
            CostDateStatusFactory(date=self.day, accepted=True)

        self.validator._check_for_accepted_costs()
        self.assertEqual(len(self.validator.errors), 1)
        self.assertIn('costs already accepted', self.validator.errors)

    # We don't test `_check_for_cycles` method, because it's only a wrapper on
    # `detect_cycles`, which has its own suite of tests.


class TestDataForReportValidationsWithForecastOn(TestDataForReportValidations):

    def setUp(self):
        self.forecast = True
        self.setUpHelper()
