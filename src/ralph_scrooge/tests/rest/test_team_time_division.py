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

# from ralph_scrooge.models import (
#     DailyUsage,
#     Environment,
#     Service,
#     ServiceEnvironment,
# )
from ralph_scrooge.models import Team
from ralph_scrooge.tests.utils.factory import (
    # EnvironmentFactory,
    # ServiceFactory,
    ServiceEnvironmentFactory,
    TeamFactory,
)


class TestTeamTimeDivision(TestCase):

    def setUp(self):
        superuser = User.objects.create_superuser(
            'test', 'test@test.test', 'test'
        )
        self.client = APIClient()
        self.client.force_authenticate(superuser)
        self.date = datetime.date(2016, 9, 8)
        self.service_environment1 = ServiceEnvironmentFactory()
        self.service_environment2 = ServiceEnvironmentFactory()
        self.service_environment3 = ServiceEnvironmentFactory()
        self.service1_uid = self.service_environment1.service.ci_uid
        self.service2_uid = self.service_environment1.service.ci_uid
        self.service3_uid = self.service_environment1.service.ci_uid
        self.service1_env_name = self.service_environment1.environment.name,
        self.service2_env_name = self.service_environment2.environment.name,
        self.service3_env_name = self.service_environment3.environment.name,
        self.team = TeamFactory()

    def test_if_uploaded_division_is_the_same_when_fetched_with_get(self):
        pass

    def test_get_division_when_there_are_no_usages_for_given_team_and_date(self):  # noqa
        pass

    def test_get_division_when_there_are_usages_for_given_team_and_date(self):
        pass

    def test_for_error_when_service_env_does_not_exist(self):
        pass

    def test_for_error_when_percents_doesnt_sum_up_to_100(self):
        # Take into accout both cases: < 100 and > 100.
        # And yes, floats as well.
        pass

    def test_for_success_when_percents_sum_up_to_100(self):
        pass

    def test_for_error_when_team_does_not_exist(self):
        division = {
            "division": [
                {
                    "service_uid": self.service1_uid,
                    "environment": self.service1_env_name,
                    "percent": 60.0,
                },
                {
                    "service_uid": self.service2_uid,
                    "environment": self.service2_env_name,
                    "percent": 20.0,
                },
                {
                    "service_uid": self.service3_uid,
                    "environment": self.service3_env_name,
                    "percent": 20.0,
                }
            ]
        }
        non_existing_team_id = 9999
        self.assertFalse(
            Team.objects.filter(id=non_existing_team_id).exists()
        )
        resp = self.client.post(
            reverse(
                'team_time_division',
                kwargs={
                    'year': self.date.year,
                    'month': self.date.month,
                    'team_id': non_existing_team_id,
                },
            ),
            json.dumps(division),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        self.assertIn(str(non_existing_team_id), resp.content)
        self.assertIn("does not exist", resp.content)

    def test_if_only_team_manager_can_upload_divisions(self):
        pass

    def test_if_only_team_manager_can_fetch_divisions(self):
        # XXX to be confirmed with @mkurek: should we restrict only POST,
        # or POST and GET..?
        pass

    def test_if_uploaded_division_overwrites_previous_one_for_same_team_and_date(self):  # noqa
        pass

    def test_for_error_when_service_uid_is_missing(self):
        division = {
            "division": [
                {
                    "service_uid": self.service1_uid,
                    "environment": self.service1_env_name,
                    "percent": 60.0,
                },
                {
                    "service_uid": self.service2_uid,
                    "environment": self.service2_env_name,
                    "percent": 20.0,
                },
                {
                    "environment": self.service3_env_name,
                    "percent": 20.0,
                }
            ]
        }
        resp = self.client.post(
            reverse(
                'team_time_division',
                kwargs={
                    'year': self.date.year,
                    'month': self.date.month,
                    'team_id': self.team.id,
                },
            ),
            json.dumps(division),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        self.assertIn("service_uid", resp.content)
        self.assertIn("field is required", resp.content)

    def test_for_error_when_environment_is_missing(self):
        division = {
            "division": [
                {
                    "service_uid": self.service1_uid,
                    "environment": self.service1_env_name,
                    "percent": 60.0,
                },
                {
                    "service_uid": self.service2_uid,
                    "environment": self.service2_env_name,
                    "percent": 20.0,
                },
                {
                    "service_uid": self.service3_uid,
                    "percent": 20.0,
                }
            ]
        }
        resp = self.client.post(
            reverse(
                'team_time_division',
                kwargs={
                    'year': self.date.year,
                    'month': self.date.month,
                    'team_id': self.team.id,
                },
            ),
            json.dumps(division),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        self.assertIn("environment", resp.content)
        self.assertIn("field is required", resp.content)

    def test_for_error_when_percent_is_missing(self):
        division = {
            "division": [
                {
                    "service_uid": self.service1_uid,
                    "environment": self.service1_env_name,
                    "percent": 60.0,
                },
                {
                    "service_uid": self.service2_uid,
                    "environment": self.service2_env_name,
                    "percent": 20.0,
                },
                {
                    "service_uid": self.service3_uid,
                    "environment": self.service3_env_name,
                }
            ]
        }
        resp = self.client.post(
            reverse(
                'team_time_division',
                kwargs={
                    'year': self.date.year,
                    'month': self.date.month,
                    'team_id': self.team.id,
                },
            ),
            json.dumps(division),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        self.assertIn("percent", resp.content)
        self.assertIn("field is required", resp.content)

    def test_for_error_when_division_is_empty_list_or_none(self):
        for d in [{'division': []}, {'division': None}]:
            resp = self.client.post(
                reverse(
                    'team_time_division',
                    kwargs={
                        'year': self.date.year,
                        'month': self.date.month,
                        'team_id': self.team.id,
                    },
                ),
                json.dumps(d),
                content_type='application/json',
            )
        self.assertEquals(resp.status_code, 400)
        self.assertIn("division", resp.content)
        self.assertIn("cannot be empty", resp.content)
