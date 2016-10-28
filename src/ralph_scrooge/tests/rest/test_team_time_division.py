# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from rest_framework.test import APIClient

from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.models import (
    Environment,
    Service,
    ServiceEnvironment,
)
from ralph_scrooge.models import (
    Team,
    TeamManager,
    TeamServiceEnvironmentPercent,
)
from ralph_scrooge.tests.utils.factory import (
    ServiceEnvironmentFactory,
    TeamFactory,
)


class TestTeamTimeDivision(ScroogeTestCase):

    def setUp(self):
        superuser = get_user_model().objects.create_superuser(
            'test', 'test@test.test', 'test'
        )
        self.client = APIClient()
        self.client.force_authenticate(superuser)
        self.date = datetime.date(2016, 9, 8)
        self.service_environment1 = ServiceEnvironmentFactory()
        self.service_environment2 = ServiceEnvironmentFactory()
        self.service_environment3 = ServiceEnvironmentFactory()
        self.service1_uid = self.service_environment1.service.ci_uid
        self.service2_uid = self.service_environment2.service.ci_uid
        self.service3_uid = self.service_environment3.service.ci_uid
        self.service1_env_name = self.service_environment1.environment.name
        self.service2_env_name = self.service_environment2.environment.name
        self.service3_env_name = self.service_environment3.environment.name
        self.team = TeamFactory()

    def test_if_uploaded_division_is_the_same_when_fetched_with_get(self):
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
        self.assertEquals(resp.status_code, 201)
        resp = self.client.get(
            reverse(
                'team_time_division',
                kwargs={
                    'year': self.date.year,
                    'month': self.date.month,
                    'team_id': self.team.id,
                },
            )
        )
        self.assertEquals(resp.status_code, 200)
        received_response = json.loads(resp.content)
        expected_response = division
        # The order of returned objects depends on DB backend, so we have to
        # manually sort them here before we compare them.
        received_response['division'].sort(key=lambda d: d['service_uid'])
        for i in range(len(expected_response['division'])):
            self.assertEquals(
                received_response['division'][i]['service_uid'],
                expected_response['division'][i]['service_uid']
            )
            self.assertEquals(
                received_response['division'][i]['environment'],
                expected_response['division'][i]['environment']
            )
            self.assertEquals(
                received_response['division'][i]['percent'],
                expected_response['division'][i]['percent']
            )

    def test_for_error_when_service_env_does_not_exist(self):
        self.assertEquals(
            ServiceEnvironment.objects.filter(
                service__ci_uid=self.service2_uid,
                environment__name=self.service1_env_name,
            ).count(),
            0
        )
        division = {
            "division": [
                {
                    "service_uid": self.service1_uid,
                    "environment": self.service1_env_name,
                    "percent": 60.0,
                },
                {
                    # Non-existing service environment (although such service
                    # and env exist).
                    "service_uid": self.service2_uid,
                    "environment": self.service1_env_name,
                    "percent": 40.0,
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
        self.assertIn('Service environment', resp.content)
        self.assertIn('does not exist', resp.content)
        self.assertIn(self.service2_uid, resp.content)
        self.assertIn(self.service1_env_name, resp.content)

    def test_for_error_when_percents_doesnt_sum_up_to_100(self):
        # We are testing here *both* validation of `percent` field, and the
        # correctness of saved values.
        division_over_100 = {
            "division": [
                {
                    "service_uid": self.service1_uid,
                    "environment": self.service1_env_name,
                    "percent": 60.0,
                },
                {
                    "service_uid": self.service2_uid,
                    "environment": self.service2_env_name,
                    "percent": 30.0,
                },
                {
                    "service_uid": self.service3_uid,
                    "environment": self.service3_env_name,
                    "percent": 20.0,
                }
            ]
        }
        self.assertEquals(TeamServiceEnvironmentPercent.objects.count(), 0)
        resp = self.client.post(
            reverse(
                'team_time_division',
                kwargs={
                    'year': self.date.year,
                    'month': self.date.month,
                    'team_id': self.team.id,
                },
            ),
            json.dumps(division_over_100),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(TeamServiceEnvironmentPercent.objects.count(), 0)
        self.assertIn("Percents should sum to 100", resp.content)
        self.assertIn(str(110.0), resp.content)

        division_less_than_100 = {
            "division": [
                {
                    "service_uid": self.service1_uid,
                    "environment": self.service1_env_name,
                    "percent": 30.0,
                },
                {
                    "service_uid": self.service2_uid,
                    "environment": self.service2_env_name,
                    "percent": 30.0,
                },
                {
                    "service_uid": self.service3_uid,
                    "environment": self.service3_env_name,
                    "percent": 20.0,
                }
            ]
        }
        self.assertEquals(TeamServiceEnvironmentPercent.objects.count(), 0)
        resp = self.client.post(
            reverse(
                'team_time_division',
                kwargs={
                    'year': self.date.year,
                    'month': self.date.month,
                    'team_id': self.team.id,
                },
            ),
            json.dumps(division_less_than_100),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(TeamServiceEnvironmentPercent.objects.count(), 0)
        self.assertIn("Percents should sum to 100", resp.content)
        self.assertIn(str(80.0), resp.content)

    def test_for_success_when_percents_sum_up_to_100(self):
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
        self.assertEquals(TeamServiceEnvironmentPercent.objects.count(), 0)
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
        self.assertEquals(resp.status_code, 201)
        self.assertEquals(TeamServiceEnvironmentPercent.objects.count(), 3)
        percent_total = 0
        for tsep in TeamServiceEnvironmentPercent.objects.all():
            percent_total += tsep.percent
        self.assertEquals(percent_total, 100)

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
        self.assertEquals(resp.status_code, 404)
        self.assertIn(str(non_existing_team_id), resp.content)
        self.assertIn("does not exist", resp.content)

    def test_if_only_team_manager_can_upload_divisions(self):
        regular_user = get_user_model().objects.create_user(
            'test2', 'test2@test.test', 'test2'
        )
        self.client.force_authenticate(regular_user)
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
        url = reverse(
            'team_time_division',
            kwargs={
                'year': self.date.year,
                'month': self.date.month,
                'team_id': self.team.id,
            },
        )
        payload = json.dumps(division)

        resp = self.client.post(url, payload, content_type='application/json')
        self.assertEquals(resp.status_code, 403)
        self.assertEquals(TeamServiceEnvironmentPercent.objects.count(), 0)

        # Let's promote regular_user to Owner and then to TeamManager (we
        # silently assume that all team managers are also owners - but not
        # the other way around).
        TeamManager.objects.create(team=self.team, manager=regular_user)

        resp = self.client.post(url, payload, content_type='application/json')
        self.assertEquals(resp.status_code, 201)
        self.assertEquals(TeamServiceEnvironmentPercent.objects.count(), 3)

    def test_if_only_team_manager_can_fetch_divisions(self):
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
        url = reverse(
            'team_time_division',
            kwargs={
                'year': self.date.year,
                'month': self.date.month,
                'team_id': self.team.id,
            },
        )

        # Let's upload initial data as a superuser.
        resp = self.client.post(
            url, json.dumps(division), content_type='application/json'
        )
        self.assertEquals(resp.status_code, 201)
        self.assertEquals(TeamServiceEnvironmentPercent.objects.count(), 3)

        # Then try to fetch this data as a regular user.
        regular_user = get_user_model().objects.create_user(
            'test2', 'test2@test.test', 'test2'
        )
        self.client.force_authenticate(regular_user)
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 403)

        # Try again with regular_user promoted to TeamManager.
        TeamManager.objects.create(team=self.team, manager=regular_user)
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_if_uploaded_division_overwrites_previous_one_for_same_team_and_date(self):  # noqa
        self.assertEquals(TeamServiceEnvironmentPercent.objects.count(), 0)
        division1 = {
            "division": [
                {
                    "service_uid": self.service1_uid,
                    "environment": self.service1_env_name,
                    "percent": 60.0,
                },
                {
                    "service_uid": self.service2_uid,
                    "environment": self.service2_env_name,
                    "percent": 40.0,
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
            json.dumps(division1),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        self.assertEquals(TeamServiceEnvironmentPercent.objects.count(), 2)
        service_uids = set()
        env_names = set()
        percents = set()
        for tsep in TeamServiceEnvironmentPercent.objects.all():
            service_uids.add(tsep.service_environment.service.ci_uid)
            env_names.add(tsep.service_environment.environment.name)
            percents.add(tsep.percent)
        self.assertEquals(service_uids, {self.service1_uid, self.service2_uid})
        self.assertEquals(
            env_names, {self.service1_env_name, self.service2_env_name}
        )
        self.assertEquals(percents, {60, 40})

        division2 = {
            "division": [
                {
                    "service_uid": self.service1_uid,
                    "environment": self.service1_env_name,
                    "percent": 70.0,
                },
                {
                    "service_uid": self.service3_uid,
                    "environment": self.service3_env_name,
                    "percent": 30.0,
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
            json.dumps(division2),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        self.assertEquals(TeamServiceEnvironmentPercent.objects.count(), 2)
        service_uids = set()
        env_names = set()
        percents = set()
        for tsep in TeamServiceEnvironmentPercent.objects.all():
            service_uids.add(tsep.service_environment.service.ci_uid)
            env_names.add(tsep.service_environment.environment.name)
            percents.add(tsep.percent)
        self.assertEquals(service_uids, {self.service1_uid, self.service3_uid})
        self.assertEquals(
            env_names, {self.service1_env_name, self.service3_env_name}
        )
        self.assertEquals(percents, {70, 30})

    def test_for_error_when_service_does_not_exist(self):
        non_existing_service_uid = 'fake_uid'
        self.assertEquals(
            Service.objects.filter(ci_uid=non_existing_service_uid).count(),
            0
        )
        division = {
            "division": [
                {
                    "service_uid": self.service1_uid,
                    "environment": self.service1_env_name,
                    "percent": 60.0,
                },
                {
                    "service_uid": non_existing_service_uid,
                    "environment": self.service2_env_name,
                    "percent": 40.0,
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
        # Scrooge checks for the existence of a given service
        # indirectly, i.e. by checking if service env exists - hence
        # assertion below.
        self.assertIn("Service environment", resp.content)
        self.assertIn("does not exist", resp.content)
        self.assertIn(non_existing_service_uid, resp.content)

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

    def test_for_error_when_environment_does_not_exist(self):
        non_existing_env_name = 'fake_uid'
        self.assertEquals(
            Environment.objects.filter(name=non_existing_env_name).count(),
            0
        )
        division = {
            "division": [
                {
                    "service_uid": self.service1_uid,
                    "environment": self.service1_env_name,
                    "percent": 60.0,
                },
                {
                    "service_uid": self.service2_uid,
                    "environment": non_existing_env_name,
                    "percent": 40.0,
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
        # Scrooge checks for the existence of a given environment
        # indirectly, i.e. by checking if service env exists - hence
        # assertion below.
        self.assertIn("Service environment", resp.content)
        self.assertIn("does not exist", resp.content)
        self.assertIn(non_existing_env_name, resp.content)

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
        self.assertIn("may not be null", resp.content)

    def test_for_error_when_service_uid_and_env_pairs_are_repeated(self):
        division = {
            "division": [
                {
                    "service_uid": self.service1_uid,
                    "environment": self.service1_env_name,
                    "percent": 70.0,
                },
                {
                    "service_uid": self.service2_uid,
                    "environment": self.service2_env_name,
                    "percent": 20.0,
                },
                {
                    "service_uid": self.service2_uid,
                    "environment": self.service2_env_name,
                    "percent": 10.0,
                }
            ]
        }
        offending_pair = "{}/{}".format(
            self.service2_uid, self.service2_env_name
        )
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
        self.assertIn("Repeated service_uid/environment", resp.content)
        self.assertIn(offending_pair, resp.content)
