# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.test import TestCase, Client
from ralph.account.models import Perm

from ralph_scrooge.app import Scrooge
from ralph_scrooge.models import ServiceOwnership, TeamManager
from ralph_scrooge.tests.utils.factory import (
    OwnerFactory,
    ServiceEnvironmentFactory,
    TeamFactory,
)


class TestSecurity(TestCase):
    def setUp(self):
        self.client = Client()

        # users
        self.accountant = User.objects.create_user(
            username='accountant',
            password='12345'
        )
        self.accountant.profile.boundperm_set.create(
            perm=Perm.has_scrooge_access
        )

        self.owner = User.objects.create_user(
            username='owner',
            password='12345'
        )
        self.team_manager = User.objects.create_user(
            username='team_manager',
            password='12345'
        )
        self.superuser = User.objects.create_user(
            username='superuser',
            password='12345',
        )
        self.superuser.is_superuser = True
        self.superuser.save()

        # create services (and assign one of them to owner)
        self.se1 = ServiceEnvironmentFactory()
        self.service1 = self.se1.service
        scrooge_owner = OwnerFactory(profile=self.owner.profile)
        ServiceOwnership.objects.create(
            service=self.service1,
            owner=scrooge_owner
        )

        self.se2 = ServiceEnvironmentFactory()
        self.service2 = self.se2.service

        # create teams
        self.team1 = TeamFactory()
        team_manager = OwnerFactory(profile=self.team_manager.profile)
        TeamManager.objects.create(team=self.team1, manager=team_manager)
        self.team2 = TeamFactory()

    def _login_as(self, user):
        self.client.login(username=user, password='12345')

    def _get_components(self, se):
        return self.client.get('/{}/rest/components/{}/{}/2014/10/1/'.format(
            Scrooge.url_prefix,
            se.service.id,
            se.environment.id,
        ))

    def _get_report(self):
        return self.client.get('/{}/services-costs-report/'.format(
            Scrooge.url_prefix,
        ))

    def _get_team_allocation(self, team):
        return self.client.get('/{}/rest/allocationclient/{}/2014/10/'.format(
            Scrooge.url_prefix,
            team.id,
        ))

    def test_components_superuser_access(self):
        self._login_as('superuser')
        response = self._get_components(self.se1)
        self.assertEquals(response.status_code, 200)
        response = self._get_components(self.se2)
        self.assertEquals(response.status_code, 200)

    def test_components_accountant_access(self):
        self._login_as('accountant')
        response = self._get_components(self.se1)
        self.assertEquals(response.status_code, 200)

    def test_components_owner_access(self):
        self._login_as('owner')
        response = self._get_components(self.se1)
        self.assertEquals(response.status_code, 200)

    def test_components_owner_access_permission_denied(self):
        self._login_as('owner')
        response = self._get_components(self.se2)
        self.assertEquals(response.status_code, 403)

    def test_report_superuser_access(self):
        self._login_as('superuser')
        response = self._get_report()
        self.assertEquals(response.status_code, 200)

    def test_report_accountant_access(self):
        self._login_as('accountant')
        response = self._get_report()
        self.assertEquals(response.status_code, 200)

    def test_report_owner_access(self):
        self._login_as('owner')
        response = self._get_report()
        self.assertEquals(response.status_code, 403)

    def test_allocation_team_manager_access(self):
        self._login_as('team_manager')
        response = self._get_team_allocation(self.team1)
        self.assertEquals(response.status_code, 200)

    def test_allocation_team_manager_access_permission_denied(self):
        self._login_as('team_manager')
        response = self._get_team_allocation(self.team2)
        self.assertEquals(response.status_code, 403)
