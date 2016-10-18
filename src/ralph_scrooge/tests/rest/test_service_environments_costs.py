# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework.test import APIClient

from ralph_scrooge.models import (
    DailyCost,
    Environment,
    Owner,
    OwnershipType,
    Service,
    ServiceOwnership,
    ServiceEnvironment,
    ServiceUsageTypes,
    UsageType,
    UserProfile,
)
from ralph_scrooge.rest.service_environments_costs import (
    USAGE_COST_NUM_DIGITS,
    USAGE_VALUE_NUM_DIGITS,
    date_range,
)
from ralph_scrooge.tests.utils.factory import (
    PricingObjectFactory,
    PricingServiceFactory,
    UsageTypeFactory,
    DailyCostFactory,
)


strptime = datetime.datetime.strptime


class TestPricingServiceUsages(TestCase):

    def setUp(self):
        self.date1 = datetime.date(2016, 8, 1)
        self.date1_as_str = self.date1.strftime("%Y-%m-%d")
        self.date2 = datetime.date(2016, 10, 1)
        self.date2_as_str = self.date2.strftime("%Y-%m-%d")
        self.pricing_object1 = PricingObjectFactory()
        self.pricing_object2 = PricingObjectFactory()
        self.service_environment1 = self.pricing_object1.service_environment
        self.service_environment2 = self.pricing_object2.service_environment
        self.service_uid1 = self.service_environment1.service.ci_uid
        self.service_uid2 = self.service_environment2.service.ci_uid
        self.environment1 = self.service_environment1.environment.name
        self.environment2 = self.service_environment2.environment.name
        self.pricing_service = PricingServiceFactory()
        self.usage_type1 = UsageTypeFactory()
        ServiceUsageTypes.objects.create(
            usage_type=self.usage_type1,
            pricing_service=self.pricing_service,
            start=datetime.date.min,
            end=datetime.date.max,
        )
        self.usage_type2 = UsageTypeFactory()
        ServiceUsageTypes.objects.create(
            usage_type=self.usage_type2,
            pricing_service=self.pricing_service,
            start=datetime.date.min,
            end=datetime.date.max,
        )

        superuser = User.objects.create_superuser(
            'username0', 'username0@test.test', 'pass0'
        )
        self.client = APIClient()
        self.client.force_authenticate(superuser)

        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": self.date1_as_str,
            "date_to": self.date2_as_str,
            "group_by": "day",
            "usage_types": [self.usage_type1.symbol, self.usage_type2.symbol]
        }

    def create_daily_costs(
            self, daily_costs, pricing_object=None, service_environment=None
    ):
        """A helper method for creating DailyCost objects with given params.

        `daily_costs` argument should be an iterable holding tuples of
        the following form: (usage type, date, value, cost).

        Apart from creating DailyCost instances, this method assigns them to
        dynamically created attributes of `self`, which will be named
        `daily_cost1`, `daily_cost2`, ..., `daily_costN`, where N is the number
        of elements in `daily_costs` iterable.
        """
        if pricing_object is None:
            pricing_object = self.pricing_object1
        if service_environment is None:
            service_environment = self.service_environment1
        for n, dc in enumerate(daily_costs, 1):
            setattr(self, 'daily_cost{}'.format(n), DailyCostFactory(
                type=dc[0],
                pricing_object=pricing_object,
                service_environment=service_environment,
                date=dc[1],
                value=dc[2],
                cost=dc[3],
            ))

    def send_post_request(self):
        return self.client.post(
            reverse('service_environments_costs'),
            json.dumps(self.payload),
            content_type='application/json',
        )

    def test_for_error_when_date_from_is_greater_than_date_to(self):
        self.payload['date_from'] = '2016-10-01'
        self.payload['date_to'] = '2016-08-01'
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 400)
        self.assertIn('should be less or equal', resp.content)

    def test_for_error_when_unknown_usage_type_given(self):
        unknown_usage_type = 'unknown usage type'
        self.assertFalse(
            UsageType.objects.filter(name=unknown_usage_type).exists()
        )
        self.payload['usage_types'].append(unknown_usage_type)
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 400)
        self.assertIn(unknown_usage_type, resp.content)

    def test_if_all_usage_types_are_used_by_default(self):
        self.payload['date_from'] = '2016-10-01'
        self.payload['date_to'] = '2016-10-01'
        self.payload.pop('usage_types')
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        usage_types_used = set(costs['costs'][0]['usages'].keys())
        usage_types_expected = set([ut.symbol for ut in UsageType.objects.all()])  # noqa: E501
        self.assertEquals(usage_types_used, usage_types_expected)

    def test_for_error_when_unknown_group_by_given(self):
        unknown_group_by = "week"
        self.payload['group_by'] = unknown_group_by
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 400)
        self.assertIn(unknown_group_by, resp.content)

    def test_list_field_validation_does_not_break_when_null_given(self):
        # This test can be removed once we switch to DjRF 3.x and get rid of
        # drf_compound_fields package.
        self.payload['usage_types'] = None
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)

    def test_for_error_when_unknown_service_uid_given(self):
        unknown_service_uid = 'xx-111'
        self.payload['service_uid'] = unknown_service_uid
        self.assertFalse(
            Service.objects.filter(ci_uid=unknown_service_uid).exists()
        )
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 400)
        self.assertIn(unknown_service_uid, resp.content)

    def test_for_error_when_unknown_environment_given(self):
        unknown_environment = 'fake env name'
        self.payload['environment'] = unknown_environment
        self.assertFalse(
            Environment.objects.filter(name=unknown_environment).exists()
        )
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 400)
        self.assertIn(unknown_environment, resp.content)

    def test_for_error_when_service_environment_does_not_exist(self):
        self.assertFalse(
            ServiceEnvironment.objects.filter(
                service__ci_uid=self.service_uid2,
                environment__name=self.environment1,
            ).exists()
        )
        self.payload['service_uid'] = self.service_uid2
        self.payload['environment'] = self.environment1
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 400)
        self.assertIn(self.service_uid2, resp.content)
        self.assertIn(self.environment1, resp.content)

    def test_if_grouped_date_has_correct_format_when_group_by_month_given(self):  # noqa: E501
        self.payload['date_from'] = "2016-10-01"
        self.payload['date_to'] = "2016-10-01"
        self.payload['group_by'] = "month"
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        date_expected = "2016-10"
        date_received = json.loads(resp.content)['costs'][0]['grouped_date']
        self.assertEquals(date_received, date_expected)

    def test_if_grouped_date_has_correct_format_when_group_by_day_given(self):
        self.payload['date_from'] = "2016-10-01"
        self.payload['date_to'] = "2016-10-01"
        self.payload['group_by'] = "day"
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        date_expected = "2016-10-01"
        date_received = json.loads(resp.content)['costs'][0]['grouped_date']
        self.assertEquals(date_received, date_expected)

    def test_if_only_superuser_and_service_owner_can_fetch_costs_and_usage_values(self):  # noqa: E501
        # Unauthenticated user.
        self.client = APIClient()
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 401)

        # Regular user (i.e. not superuser or owner).
        regular_user = User.objects.create_user(
            'username2', 'username2@test.test', 'pass2'
        )
        self.client = APIClient()
        self.client.force_authenticate(regular_user)
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 403)

        # Superuser.
        superuser = User.objects.create_superuser(
            'username1', 'username1@test.test', 'pass1'
        )
        self.client = APIClient()
        self.client.force_authenticate(superuser)
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)

        # Owner.
        user_profile = UserProfile.objects.create(user=regular_user)
        owner = Owner.objects.create(profile=user_profile)
        ServiceOwnership.objects.create(
            service=self.service_environment1.service,
            type=OwnershipType.business,
            owner=owner
        )
        self.client = APIClient()
        # At this point, regular_user is "promoted" to owner.
        self.client.force_authenticate(regular_user)
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)

    def test_if_costs_and_usage_values_are_returned_for_all_selected_usage_types(self):  # noqa: E501
        self.payload['date_from'] = self.date1_as_str
        self.payload['date_to'] = self.date1_as_str
        self.create_daily_costs((
            (self.usage_type1, self.date1, 10, 20),
            (self.usage_type2, self.date1, 11, 21),
        ))

        for usage_types in [
            [self.usage_type1.symbol, self.usage_type2.symbol],
            [self.usage_type1.symbol],
        ]:
            self.payload['usage_types'] = usage_types
            resp = self.send_post_request()
            self.assertEquals(resp.status_code, 200)
            costs = json.loads(resp.content)
            for ut in UsageType.objects.filter(
                    name__in=self.payload['usage_types']
            ):
                daily_cost = DailyCost.objects.get(type=ut)
                self.assertEquals(
                    costs['costs'][0]['usages'][ut.name]['usage_value'],
                    daily_cost.value
                )
                self.assertEquals(
                    costs['costs'][0]['usages'][ut.name]['cost'],
                    daily_cost.cost
                )

    def test_if_costs_and_usage_values_are_rounded_to_given_precision(self):
        usage_type_symbol = self.usage_type1.symbol
        self.payload['date_from'] = self.date1_as_str
        self.payload['date_to'] = self.date1_as_str
        self.payload['usage_types'] = [usage_type_symbol]
        self.create_daily_costs((
            (self.usage_type1, self.date1, 1.123456789, 1.123456789),
        ))

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        self.assertEquals(
            costs['costs'][0]['usages'][usage_type_symbol]['usage_value'],
            round(self.daily_cost1.value, USAGE_VALUE_NUM_DIGITS)
        )
        self.assertEquals(
            costs['costs'][0]['usages'][usage_type_symbol]['cost'],
            round(self.daily_cost1.cost, USAGE_COST_NUM_DIGITS)
        )

    def test_if_expected_total_cost_is_returned_when_group_by_day(self):
        pass

    def test_if_expected_total_cost_is_returned_when_group_by_month(self):
        pass

    def test_if_costs_and_usage_values_are_properly_aggregated_when_group_by_day(self):  # noqa: E501
        dates = ('2016-10-07', '2016-10-08')
        daily_costs = (
            (self.usage_type1, strptime(dates[0], '%Y-%m-%d').date(), 10, 20),
            (self.usage_type1, strptime(dates[0], '%Y-%m-%d').date(), 20, 40),
            (self.usage_type2, strptime(dates[0], '%Y-%m-%d').date(), 11, 22),
            (self.usage_type2, strptime(dates[0], '%Y-%m-%d').date(), 22, 44),

            (self.usage_type1, strptime(dates[1], '%Y-%m-%d').date(), 10, 20),
            (self.usage_type1, strptime(dates[1], '%Y-%m-%d').date(), 20, 40),
            (self.usage_type2, strptime(dates[1], '%Y-%m-%d').date(), 11, 22),
            (self.usage_type2, strptime(dates[1], '%Y-%m-%d').date(), 22, 44),
        )
        self.create_daily_costs(daily_costs)
        self.payload['date_from'] = dates[0]
        self.payload['date_to'] = dates[1]
        self.payload['group_by'] = 'day'

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        self.assertEquals(len(costs['costs']), 2)
        for c in costs['costs']:
            self.assertEquals(
                c['usages'][self.usage_type1.symbol]['usage_value'], 30.0
            )
            self.assertEquals(
                c['usages'][self.usage_type1.symbol]['cost'], 60.0
            )
            self.assertEquals(
                c['usages'][self.usage_type2.symbol]['usage_value'], 33.0
            )
            self.assertEquals(
                c['usages'][self.usage_type2.symbol]['cost'], 66.0
            )

    def test_if_costs_and_usage_values_are_properly_aggregated_when_group_by_month(self):  # noqa: E501
        date_from = '2016-10-01'
        date_to = '2016-10-31'
        usage_value = 10
        cost = 20
        daily_costs = [
            (self.usage_type1, d.date(), usage_value, cost)
            for d in date_range(
                strptime(date_from, '%Y-%m-%d'),
                strptime(date_to, '%Y-%m-%d') + datetime.timedelta(days=1),
            )
        ]
        self.create_daily_costs(daily_costs)
        self.payload['date_from'] = date_from
        self.payload['date_to'] = date_to
        self.payload['group_by'] = 'month'
        self.payload['usage_types'] = [self.usage_type1.symbol]

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        self.assertEquals(len(costs['costs']), 1)
        expected_usage_value = usage_value * 31
        expected_cost = cost * 31
        self.assertEquals(
            costs['costs'][0]['usages'][self.usage_type1.symbol]['usage_value'],  # noqa: E501
            expected_usage_value
        )
        self.assertEquals(
            costs['costs'][0]['usages'][self.usage_type1.symbol]['cost'],
            expected_cost
        )

    def test_if_total_cost_includes_other_costs_if_present(self):
        date = '2016-10-07'
        cost1 = 20
        cost2 = 40
        daily_costs = (
            (self.usage_type1, strptime(date, '%Y-%m-%d').date(), 1, cost1),
            (self.usage_type2, strptime(date, '%Y-%m-%d').date(), 1, cost2),
        )
        self.create_daily_costs(daily_costs)
        self.payload['date_from'] = date
        self.payload['date_to'] = date
        self.payload['group_by'] = 'day'

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        expected_total_cost = cost1 + cost2
        self.assertEquals(costs['costs'][0]['total_cost'], expected_total_cost)

        self.assertEquals(UsageType.objects.count(), 2)
        # Create new cost, not associated with usage types being the subject
        # of the previous query.
        other_usage_type = UsageTypeFactory()
        ServiceUsageTypes.objects.create(
            usage_type=other_usage_type,
            pricing_service=self.pricing_service,
            start=datetime.date.min,
            end=datetime.date.max,
        )
        other_cost = 100
        DailyCostFactory(
            type=other_usage_type,
            pricing_object=self.pricing_object1,
            service_environment=self.service_environment1,
            date=strptime(date, '%Y-%m-%d').date(),
            value=1,
            cost=other_cost,
        )
        self.assertEquals(UsageType.objects.count(), 3)

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        expected_total_cost = cost1 + cost2 + other_cost
        self.assertEquals(costs['costs'][0]['total_cost'], expected_total_cost)
        requested_usage_types = costs['costs'][0]['usages'].keys()
        self.assertNotIn(other_usage_type.name, requested_usage_types)
