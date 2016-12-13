# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json

from django.core.urlresolvers import reverse
from rest_framework.test import APIClient

from ralph_scrooge.models import (
    BaseUsage,
    DailyCost,
    Environment,
    OwnershipType,
    ScroogeUser,
    Service,
    ServiceOwnership,
    ServiceEnvironment,
    ServiceUsageTypes,
    UsageType,
)
from ralph_scrooge.rest_api.public.v0_10.service_environment_costs import (
    USAGE_COST_NUM_DIGITS,
    USAGE_VALUE_NUM_DIGITS,
    date_range,
)
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import (
    PricingObjectFactory,
    PricingServiceFactory,
    UsageTypeFactory,
    DailyCostFactory,
)

# Let's abbreviate this name for convenience.
strptime = datetime.datetime.strptime


class TestServiceEnvironmentCosts(ScroogeTestCase):

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
        superuser = ScroogeUser.objects.create_superuser(
            'username0', 'username0@test.test', 'pass0'
        )
        self.client = APIClient()
        self.client.force_authenticate(superuser)

    # TODO(xor-xor): Consider using named tuples for `daily_costs`.
    def create_daily_costs(
            self, daily_costs, service_env=None, parent=None, forecast=False
    ):
        """A helper method for creating DailyCost objects with given params.

        `daily_costs` arg should be an iterable holding tuples of the following
        form: (usage type, date, value, cost).

        `service_env` designates service environment that created costs should
        be associated with (if None given, then `self.service_environment1`
        will be used).

        `parent` arg should be a tuple (pricing service, date as string) - this
        pricing service will be used as a parent for created DailyCosts.

        Subcosts are linked to parent costs via `path` field, e.g. a cost with
        `path` "0/1" is a subcost of a cost with `path` "0". And also, parent
        costs can be distinguished from subcosts by `depth` field, which will
        be 0 in the former case, and 1 in the latter.

        `forecast` designates if costs should be created as "forecasted" (in
        in contrast to "normal" ones).
        """
        pricing_object = self.pricing_object1
        if not service_env:
            service_env = self.service_environment1
        if parent is not None:
            parent_value = parent_cost = 0
            children = set([dc[0] for dc in daily_costs])
            child_id_lookup = {}
            for n, c in enumerate(children):
                child_id_lookup[c] = n

        for n, dc in enumerate(daily_costs, 1):
            if parent is not None:
                parent_value += dc[2]
                parent_cost += dc[3]
                id_ = child_id_lookup[dc[0]]
            DailyCostFactory(
                type=dc[0],
                pricing_object=pricing_object,
                service_environment=service_env,
                date=dc[1],
                value=dc[2],
                cost=dc[3],
                depth=(1 if parent is not None else 0),
                path=("0/{}".format(id_) if parent is not None else str(n)),
                forecast=forecast,
            )
        if parent is not None:
            parent_cost = DailyCostFactory(
                type=parent[0],
                pricing_object=pricing_object,
                service_environment=service_env,
                date=parent[1],
                value=parent_value,
                cost=parent_cost,
                depth=0,
                path="0",
                forecast=forecast,
            )

    def send_post_request(self):
        return self.client.post(
            reverse('service_environment_costs'),
            json.dumps(self.payload),
            content_type='application/json',
        )

    def test_for_error_when_date_from_is_greater_than_date_to(self):
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": '2016-10-01',
            "date_to": '2016-08-01',
            "group_by": "day",
            "types": [self.pricing_service.symbol]
        }
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 400)
        self.assertIn('should be less or equal', resp.content)

    def test_for_error_when_unknown_usage_type_given(self):
        unknown_type = 'unknown type'
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": self.date1_as_str,
            "date_to": self.date2_as_str,
            "group_by": "day",
            "types": [self.pricing_service.symbol, unknown_type]
        }
        self.assertFalse(
            BaseUsage.objects.filter(name=unknown_type).exists()
        )
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 400)
        self.assertIn(unknown_type, resp.content)

    def test_if_all_base_usages_with_depth_zero_are_used_by_default(self):
        costs = (
            (self.usage_type1, self.date1, 10, 20),
            (self.usage_type2, self.date1, 11, 21),
        )
        self.create_daily_costs(
            costs, parent=(self.pricing_service, self.date1_as_str)
        )
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": self.date1_as_str,
            "date_to": self.date1_as_str,
            "group_by": "day"
        }

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        types_used = set(
            costs['service_environment_costs'][0]['costs'].keys()
        )
        parent_base_usages = BaseUsage.objects.exclude(
            pk__in=UsageType.objects.filter(usage_type='SU')
        )
        types_from_fixtures = {'other', 'support'}
        parent_base_usages_ = set([p.symbol for p in parent_base_usages])
        types_expected = parent_base_usages_ - types_from_fixtures
        self.assertEquals(types_used, types_expected)

    def test_for_error_when_unknown_group_by_given(self):
        unknown_group_by = "week"
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": self.date1_as_str,
            "date_to": self.date2_as_str,
            "group_by": unknown_group_by,
            "types": [self.pricing_service.symbol]
        }

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 400)
        self.assertIn(unknown_group_by, resp.content)

    def test_for_error_when_unknown_service_uid_given(self):
        unknown_service_uid = 'xx-111'
        self.payload = {
            "service_uid": unknown_service_uid,
            "environment": self.environment1,
            "date_from": self.date1_as_str,
            "date_to": self.date2_as_str,
            "group_by": "day",
            "types": [self.pricing_service.symbol]
        }
        self.assertFalse(
            Service.objects.filter(ci_uid=unknown_service_uid).exists()
        )
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 400)
        self.assertIn(unknown_service_uid, resp.content)

    def test_for_error_when_unknown_environment_given(self):
        unknown_environment = 'fake env name'
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": unknown_environment,
            "date_from": self.date1_as_str,
            "date_to": self.date2_as_str,
            "group_by": "day",
            "types": [self.pricing_service.symbol]
        }
        self.assertFalse(
            Environment.objects.filter(name=unknown_environment).exists()
        )
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 400)
        self.assertIn(unknown_environment, resp.content)

    def test_for_error_when_service_environment_does_not_exist(self):
        self.payload = {
            "service_uid": self.service_uid2,
            "environment": self.environment1,
            "date_from": self.date1_as_str,
            "date_to": self.date2_as_str,
            "group_by": "day",
            "types": [self.pricing_service.symbol]
        }
        self.assertFalse(
            ServiceEnvironment.objects.filter(
                service__ci_uid=self.service_uid2,
                environment__name=self.environment1,
            ).exists()
        )
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 400)
        self.assertIn(self.service_uid2, resp.content)
        self.assertIn(self.environment1, resp.content)

    def test_if_grouped_date_has_correct_format_when_group_by_month_given(self):  # noqa: E501
        costs = (
            (self.usage_type1, self.date1, 10, 20),
            (self.usage_type2, self.date1, 11, 21),
        )
        self.create_daily_costs(
            costs, parent=(self.pricing_service, self.date1_as_str)
        )
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": self.date1_as_str,
            "date_to": self.date1_as_str,
            "group_by": "month",
            "types": [self.pricing_service.symbol]
        }
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        date_expected = self.date1.strftime('%Y-%m')
        date_received = json.loads(resp.content)['service_environment_costs'][0]['grouped_date']  # noqa: E501
        self.assertEquals(date_received, date_expected)

    def test_for_forecast_costs(self):
        costs = (
            (self.usage_type1, self.date1, 10, 20),
            (self.usage_type2, self.date1, 11, 21),
        )
        self.create_daily_costs(
            costs, parent=(self.pricing_service, self.date1_as_str),
            forecast=True,
        )
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": self.date1_as_str,
            "date_to": self.date1_as_str,
            "group_by": "month",
            "types": [self.pricing_service.symbol]
        }
        # first, try non-forecast and check if response is empty
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        self.assertEqual(
            len(json.loads(resp.content)['service_environment_costs'][0]['costs']), 0  # noqa: E501
        )
        # try forecast - it should have some costs
        self.payload['forecast'] = True
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        self.assertGreater(
            len(json.loads(resp.content)['service_environment_costs'][0]['costs']), 0  # noqa: E501
        )

    def test_if_grouped_date_has_correct_format_when_group_by_day_given(self):
        costs = (
            (self.usage_type1, self.date1, 10, 20),
            (self.usage_type2, self.date1, 11, 21),
        )
        self.create_daily_costs(
            costs, parent=(self.pricing_service, self.date1_as_str)
        )
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": self.date1_as_str,
            "date_to": self.date1_as_str,
            "group_by": "day",
            "types": [self.pricing_service.symbol]
        }
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        date_expected = self.date1_as_str
        date_received = json.loads(resp.content)['service_environment_costs'][0]['grouped_date']  # noqa: E501
        self.assertEquals(date_received, date_expected)

    def test_if_only_superuser_and_service_owner_can_fetch_costs_and_usage_values(self):  # noqa: E501
        costs = (
            (self.usage_type1, self.date1, 10, 20),
            (self.usage_type2, self.date1, 11, 21),
        )
        self.create_daily_costs(
            costs, parent=(self.pricing_service, self.date1_as_str)
        )
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": self.date1_as_str,
            "date_to": self.date1_as_str,
            "group_by": "day",
            "types": [self.pricing_service.symbol]
        }

        # Unauthenticated user.
        self.client = APIClient()
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 401)

        # Regular user (i.e. not superuser or owner).
        regular_user = ScroogeUser.objects.create_user(
            'username2', 'username2@test.test', 'pass2'
        )
        self.client = APIClient()
        self.client.force_authenticate(regular_user)
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 403)

        # Superuser.
        superuser = ScroogeUser.objects.create_superuser(
            'username1', 'username1@test.test', 'pass1'
        )
        self.client = APIClient()
        self.client.force_authenticate(superuser)
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)

        # Owner.
        ServiceOwnership.objects.create(
            service=self.service_environment1.service,
            type=OwnershipType.business,
            owner=regular_user
        )  # At this point, regular_user is "promoted" to owner.
        self.client = APIClient()
        self.client.force_authenticate(regular_user)
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)

    def test_if_costs_and_usage_values_are_rounded_to_given_precision(self):
        cost = value = 1.123456789
        costs = (
            (self.usage_type1, self.date1, value, cost),
            (self.usage_type2, self.date1, cost, cost),
        )
        self.create_daily_costs(
            costs, parent=(self.pricing_service, self.date1_as_str)
        )
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": self.date1_as_str,
            "date_to": self.date1_as_str,
            "group_by": "day",
            "types": [self.pricing_service.symbol]
        }

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)

        # Let's abbreviate these for convenience.
        costs_ = costs['service_environment_costs'][0]['costs']
        pricing_service_ = costs_[self.pricing_service.symbol]
        type1_ = pricing_service_['subcosts'][self.usage_type1.symbol]
        type2_ = pricing_service_['subcosts'][self.usage_type2.symbol]

        self.assertEquals(
            pricing_service_['cost'],
            round(cost * 2, USAGE_COST_NUM_DIGITS)
        )
        self.assertEquals(
            pricing_service_['usage_value'],
            round(value * 2, USAGE_VALUE_NUM_DIGITS)
        )
        self.assertEquals(
            type1_['cost'],
            round(cost, USAGE_COST_NUM_DIGITS)
        )
        self.assertEquals(
            type1_['usage_value'],
            round(value, USAGE_VALUE_NUM_DIGITS)
        )
        self.assertEquals(
            type2_['cost'],
            round(cost, USAGE_COST_NUM_DIGITS)
        )
        self.assertEquals(
            type2_['usage_value'],
            round(value, USAGE_VALUE_NUM_DIGITS)
        )

    def test_if_costs_and_usage_values_are_properly_aggregated_when_group_by_day(self):  # noqa: E501
        dates = ('2016-10-07', '2016-10-08')
        daily_costs1 = (
            (self.usage_type1, strptime(dates[0], '%Y-%m-%d').date(), 1, 10),
            (self.usage_type1, strptime(dates[0], '%Y-%m-%d').date(), 2, 20),
            (self.usage_type2, strptime(dates[0], '%Y-%m-%d').date(), 3, 30),
            (self.usage_type2, strptime(dates[0], '%Y-%m-%d').date(), 4, 40),
        )
        daily_costs2 = (
            (self.usage_type1, strptime(dates[1], '%Y-%m-%d').date(), 5, 50),
            (self.usage_type1, strptime(dates[1], '%Y-%m-%d').date(), 6, 60),
            (self.usage_type2, strptime(dates[1], '%Y-%m-%d').date(), 7, 70),
            (self.usage_type2, strptime(dates[1], '%Y-%m-%d').date(), 8, 80),
        )
        self.create_daily_costs(
            daily_costs1,
            parent=(self.pricing_service, dates[0]),
        )
        self.create_daily_costs(
            daily_costs2,
            parent=(self.pricing_service, dates[1]),
        )
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": dates[0],
            "date_to": dates[1],
            "group_by": "day",
            "types": [self.pricing_service.symbol]
        }

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        self.assertEquals(len(costs['service_environment_costs']), 2)

        for c in costs['service_environment_costs']:
            pricing_service_ = c['costs'][self.pricing_service.symbol]
            subcost1_ = pricing_service_['subcosts'][self.usage_type1.symbol]
            subcost2_ = pricing_service_['subcosts'][self.usage_type2.symbol]
            if c['grouped_date'] == dates[0]:
                self.assertEquals(pricing_service_['cost'], 100.0)
                self.assertEquals(pricing_service_['usage_value'], 10.0)
                self.assertEquals(subcost1_['cost'], 30.0)
                self.assertEquals(subcost1_['usage_value'], 3.0)
                self.assertEquals(subcost2_['cost'], 70.0)
                self.assertEquals(subcost2_['usage_value'], 7.0)
                self.assertEquals(c['total_cost'], 100.0)
            elif c['grouped_date'] == dates[1]:
                self.assertEquals(pricing_service_['cost'], 260.0)
                self.assertEquals(pricing_service_['usage_value'], 26.0)
                self.assertEquals(subcost1_['cost'], 110.0)
                self.assertEquals(subcost1_['usage_value'], 11.0)
                self.assertEquals(subcost2_['cost'], 150.0)
                self.assertEquals(subcost2_['usage_value'], 15.0)
                self.assertEquals(c['total_cost'], 260.0)
            else:
                assert False  # this shouldn't happen!

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
        for dc in daily_costs:
            self.create_daily_costs(
                (dc,),
                parent=(self.pricing_service, dc[1].strftime('%Y-%m-%d'))
            )
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": date_from,
            "date_to": date_to,
            "group_by": "month",
            "types": [self.pricing_service.symbol]
        }

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        self.assertEquals(len(costs['service_environment_costs']), 1)
        expected_usage_value = usage_value * 31
        expected_cost = cost * 31
        self.assertEquals(
            costs['service_environment_costs'][0]['costs'][self.pricing_service.symbol]['usage_value'],  # noqa: E501
            expected_usage_value
        )
        self.assertEquals(
            costs['service_environment_costs'][0]['costs'][self.pricing_service.symbol]['cost'],  # noqa: E501
            expected_cost
        )

    def test_if_total_cost_includes_other_costs_if_present(self):
        date = '2016-10-07'
        cost1 = 20
        cost2 = 40
        cost3 = 100
        costs = (
            (self.usage_type1, strptime(date, '%Y-%m-%d').date(), 1, cost1),
            (self.usage_type2, strptime(date, '%Y-%m-%d').date(), 1, cost2),
        )
        self.create_daily_costs(
            costs, parent=(self.pricing_service, date)
        )
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": date,
            "date_to": date,
            "group_by": "day",
            "types": [self.pricing_service.symbol]
        }

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        expected_total_cost = cost1 + cost2
        self.assertEquals(
            costs['service_environment_costs'][0]['total_cost'],
            expected_total_cost
        )

        # Create some "other" cost.
        self.create_daily_costs(((self.usage_type2, date, 1, cost3),))

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        expected_total_cost = cost1 + cost2 + cost3
        self.assertEquals(
            costs['service_environment_costs'][0]['total_cost'],
            expected_total_cost
        )
        requested_types = costs['service_environment_costs'][0]['costs'].keys()  # noqa: E501
        self.assertNotIn(self.usage_type2, requested_types)

    def test_if_costs_and_values_are_not_rounded_to_month_boundaries(self):
        date1_as_str = '2016-10-01'
        date2_as_str = '2016-10-07'
        date3_as_str = '2016-10-31'
        date1 = strptime(date1_as_str, '%Y-%m-%d').date()
        date2 = strptime(date2_as_str, '%Y-%m-%d').date()
        date3 = strptime(date3_as_str, '%Y-%m-%d').date()
        cost1 = 10
        cost2 = 20
        cost3 = 30
        cost4 = 40  # some "other" cost
        self.create_daily_costs(
            ((self.usage_type1, date1, 1, cost1),),
            parent=(self.pricing_service, date1),
        )
        self.create_daily_costs(
            ((self.usage_type1, date2, 1, cost2),),
            parent=(self.pricing_service, date2),
        )
        self.create_daily_costs(
            ((self.usage_type1, date3, 1, cost3),),
            parent=(self.pricing_service, date3),
        )
        self.create_daily_costs(((self.usage_type2, date3, 1, cost4),))

        # Group by month and also whole month given as date range.
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": date1_as_str,
            "date_to": date3_as_str,
            "group_by": "month",
            "types": [self.pricing_service.symbol]
        }
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        self.assertEquals(
            costs['service_environment_costs'][0]['total_cost'],
            cost1 + cost2 + cost3 + cost4
        )
        self.assertEquals(
            costs['service_environment_costs'][0]['costs'][self.pricing_service.symbol]['cost'],  # noqa: E501
            cost1 + cost2 + cost3
        )

        # Group by month, but only single day given as date range - we expect
        # different results than those from "group by month + whole month given
        # as range" case. In other words, when date range is smaller than the
        # selected group by unit, we expect that only costs from this date
        # range will be taken into account.
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": date2_as_str,
            "date_to": date2_as_str,
            "group_by": "month",
            "types": [self.pricing_service.symbol]
        }
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        self.assertEquals(
            costs['service_environment_costs'][0]['total_cost'],
            cost2
        )
        self.assertEquals(
            costs['service_environment_costs'][0]['costs'][self.pricing_service.symbol]['cost'],  # noqa: E501
            cost2
        )

    def test_if_subcosts_show_up_in_resulting_json(self):
        cost1 = 10
        cost2 = 11
        usage_value1 = 1
        usage_value2 = 2
        costs = (
            (self.usage_type1, self.date1, usage_value1, cost1),
            (self.usage_type2, self.date1, usage_value2, cost2),
        )
        self.create_daily_costs(
            costs, parent=(self.pricing_service, self.date1_as_str)
        )
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": self.date1_as_str,
            "date_to": self.date1_as_str,
            "group_by": "day",
            "types": [self.pricing_service.symbol]
        }

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)

        subcosts = costs['service_environment_costs'][0]['costs'][self.pricing_service.symbol]['subcosts']  # noqa: E501
        self.assertEquals(len(subcosts.keys()), 2)
        self.assertEquals(subcosts[self.usage_type1.symbol]['cost'], cost1)
        self.assertEquals(
            subcosts[self.usage_type1.symbol]['usage_value'], usage_value1
        )
        self.assertEquals(subcosts[self.usage_type2.symbol]['cost'], cost2)
        self.assertEquals(
            subcosts[self.usage_type2.symbol]['usage_value'], usage_value2
        )

    def test_if_top_level_costs_do_not_overwrite_each_other(self):
        date = '2016-10-07'
        daily_costs1 = (
            (self.usage_type1, strptime(date, '%Y-%m-%d').date(), 1, 10),
        )
        daily_costs2 = (
            (self.usage_type2, strptime(date, '%Y-%m-%d').date(), 11, 11),
        )
        pricing_service1 = self.pricing_service
        pricing_service2 = PricingServiceFactory()
        ServiceUsageTypes.objects.create(
            usage_type=self.usage_type2,
            pricing_service=pricing_service2,
            start=datetime.date.min,
            end=datetime.date.max,
        )
        self.create_daily_costs(
            daily_costs1,
            parent=(pricing_service1, date),
        )
        self.create_daily_costs(
            daily_costs2,
            parent=(pricing_service2, date),
        )
        for type_symbol, path in (
            (pricing_service1.symbol, '0'),
            (pricing_service2.symbol, '1'),
            (self.usage_type1.symbol, '0/2'),
            (self.usage_type2.symbol, '1/3'),
        ):
            dc = DailyCost.objects_tree.get(type__symbol=type_symbol)
            dc.path = path
            dc.save()

        # At this point we should have the following structure:
        #
        # costs
        #   |--- ps1 (cost)
        #   |     |
        #   |    ut1 (subcost)
        #   |
        #   |___ ps1 (cost)
        #         |
        #        ut2 (subcost)

        types = [pricing_service1.symbol, pricing_service2.symbol]
        self.payload = {
            "service_uid": self.service_uid1,
            "environment": self.environment1,
            "date_from": date,
            "date_to": date,
            "group_by": "day",
            "types": types
        }

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)
        self.assertEquals(
            set(costs['service_environment_costs'][0]['costs'].keys()),
            set(types)
        )

    def test_if_all_envs_are_taken_into_account_when_no_env_given(self):
        cost1 = 10
        cost2 = 20
        usage_value1 = 1
        usage_value2 = 2

        # We need two service environments that share the same service, but
        # have different environments.
        service_env1 = self.service_environment1
        env2_name = "other"
        self.assertFalse(
            Environment.objects.filter(name=env2_name).exists()
        )
        env2 = Environment.objects.create(name=env2_name)
        service_env2 = ServiceEnvironment.objects.create(
            service=service_env1.service,
            environment=env2,
        )
        self.assertIs(service_env1.service, service_env2.service)
        self.assertIsNot(service_env1.environment, service_env2.environment)

        self.create_daily_costs(
            ((self.usage_type1, self.date1, usage_value1, cost1),),
            service_env=service_env1,
            parent=(self.pricing_service, self.date1),
        )
        self.create_daily_costs(
            ((self.usage_type1, self.date1, usage_value2, cost2),),
            service_env=service_env2,
            parent=(self.pricing_service, self.date1),
        )
        self.payload = {
            "service_uid": self.service_uid1,
            "date_from": self.date1_as_str,
            "date_to": self.date1_as_str,
            "group_by": "day",
            "types": [self.pricing_service.symbol]
        }

        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)
        costs = json.loads(resp.content)

        costs_ = costs['service_environment_costs'][0]['costs'][self.pricing_service.symbol]['cost']  # noqa: E501
        subcosts = costs['service_environment_costs'][0]['costs'][self.pricing_service.symbol]['subcosts']  # noqa: E501
        total_cost = costs['service_environment_costs'][0]['total_cost']

        self.assertEquals(costs_, cost1 + cost2)
        self.assertEquals(total_cost, cost1 + cost2)
        self.assertEquals(len(subcosts.values()), 1)
        self.assertEquals(
            subcosts.values()[0]['cost'],
            cost1 + cost2
        )
        self.assertEquals(
            subcosts.values()[0]['usage_value'],
            usage_value1 + usage_value2
        )
