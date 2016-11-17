# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework.test import APIClient

from ralph_scrooge.models import ServiceOwnership, TeamManager
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import (
    ServiceEnvironmentFactory,
    TeamFactory,
)
from ralph_scrooge.utils.security import _is_usage_owner


class TestSecurity(ScroogeTestCase):
    def setUp(self):
        self.client = APIClient()

        # users
        self.accountant = get_user_model().objects.create_user(
            username='accountant',
            password='12345'
        )
        self.owner = get_user_model().objects.create_user(
            username='owner',
            password='12345'
        )
        self.team_manager = get_user_model().objects.create_user(
            username='team_manager',
            password='12345'
        )
        self.usage_owner = get_user_model().objects.create_user(
            username='usage_owner',
            password='12345'
        )
        self.superuser = get_user_model().objects.create_user(
            username='superuser',
            password='12345',
        )
        self.superuser.is_superuser = True
        self.superuser.save()

        # create services (and assign one of them to owner)
        self.se1 = ServiceEnvironmentFactory()
        self.service1 = self.se1.service
        ServiceOwnership.objects.create(
            service=self.service1,
            owner=self.owner
        )

        self.se2 = ServiceEnvironmentFactory()
        self.service2 = self.se2.service

        # create teams
        self.team1 = TeamFactory()
        TeamManager.objects.create(team=self.team1, manager=self.team_manager)
        self.team2 = TeamFactory()

        # assign usage owner permissions
        self.usage_owner.groups.add(
            Group.objects.get_or_create(
                name=settings.USAGE_OWNERS_GROUP_NAME
            )[0]
        )

    def _login_as(self, user):
        self.client.login(username=user, password='12345')

    def _get_components(self, se):
        return self.client.get(
            '/scrooge/rest/components/{}/{}/2014/10/1/'.format(
                se.service.id,
                se.environment.id,
            )
        )

    def _get_team_allocation(self, team):
        return self.client.get(
            '/scrooge/rest/allocationclient/{}/2014/10/'.format(
                team.id,
            )
        )

    def test_components_superuser_access(self):
        self._login_as('superuser')
        response = self._get_components(self.se1)
        self.assertEquals(response.status_code, 200)
        response = self._get_components(self.se2)
        self.assertEquals(response.status_code, 200)

    def test_components_accountant_permission_denied(self):
        self._login_as('accountant')
        response = self._get_components(self.se1)
        self.assertEquals(response.status_code, 403)

    def test_components_owner_access(self):
        self._login_as('owner')
        response = self._get_components(self.se1)
        self.assertEquals(response.status_code, 200)

    def test_components_owner_access_permission_denied(self):
        self._login_as('owner')
        response = self._get_components(self.se2)
        self.assertEquals(response.status_code, 403)

    def test_allocation_team_manager_access(self):
        self._login_as('team_manager')
        response = self._get_team_allocation(self.team1)
        self.assertEquals(response.status_code, 200)

    def test_allocation_team_manager_access_permission_denied(self):
        self._login_as('team_manager')
        response = self._get_team_allocation(self.team2)
        self.assertEquals(response.status_code, 403)

    def test_is_usage_owner_should_return_true_for_superuser(self):
        self.assertTrue(_is_usage_owner(self.superuser))

    def test_is_usage_owner_should_return_true_for_usage_owner(self):
        self.assertTrue(_is_usage_owner(self.usage_owner))

    def test_is_usage_owner_should_return_false_for_team_manager(self):
        self.assertFalse(_is_usage_owner(self.team_manager))

    def test_usages_report_usage_owner_should_have_access(self):
        self._login_as('usage_owner')
        response = self.client.get(
            reverse('usages_report_rest') +
            '?start=2016-11-11&end=2016-11-12&usage_types=1111'
        )
        self.assertEquals(response.status_code, 200)

    def test_usages_report_team_manager_access_permission_denied(self):
        self._login_as('team_manager')
        response = self.client.get(reverse('usages_report_rest'))
        self.assertEquals(response.status_code, 403)
