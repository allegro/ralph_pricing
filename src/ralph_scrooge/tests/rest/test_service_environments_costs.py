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
    DailyUsage,
    Environment,
    Owner,
    OwnershipType,
    PricingService,
    Service,
    ServiceOwnership,
    ServiceEnvironment,
    ServiceUsageTypes,
    UsageType,
    UserProfile,
)
from ralph_scrooge.tests.utils.factory import (
    PricingObjectFactory,
    PricingServiceFactory,
    UsageTypeFactory,
    DailyCostFactory,
)


class TestPricingServiceUsages(TestCase):

    def setUp(self):
        self.date1 = datetime.date(2016, 8, 1)  # XXX needed?
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
            "usage_types": [self.usage_type1.name, self.usage_type2.name]
        }

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
        usage_types_expected = set([ut.name for ut in UsageType.objects.all()])
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

    def test_if_grouped_date_has_correct_format_when_group_by_month_given(self):  # noqa
        pass

    def test_if_grouped_date_has_correct_format_when_group_by_day_given(self):
        pass

    def test_if_costs_and_usage_values_are_rounded_to_given_precision(self):
        pass

    def test_if_expected_total_cost_is_returned_when_group_by_day(self):
        pass

    def test_if_expected_total_cost_is_returned_when_group_by_month(self):
        pass

    def test_if_costs_and_usage_values_are_returned_for_all_selected_usage_types(self):  # noqa
        pass

    def test_if_multiple_validation_errors_are_aggregated_into_one(self):
        pass

    def test_if_months_range_returns_xxx(self):
        pass

    def test_if_only_superuser_and_service_owner_can_fetch_costs_and_usage_values(self):  # noqa
        self.client = APIClient()
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 401)

        superuser = User.objects.create_superuser(
            'username1', 'username1@test.test', 'pass1'
        )
        self.client = APIClient()
        self.client.force_authenticate(superuser)
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 200)

        regular_user = User.objects.create_user(
            'username2', 'username2@test.test', 'pass2'
        )
        self.client = APIClient()
        self.client.force_authenticate(regular_user)
        resp = self.send_post_request()
        self.assertEquals(resp.status_code, 403)

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
