# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals

import datetime

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from ralph_scrooge.models import ExtraCost
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import (
    BusinessLineFactory,
    EnvironmentFactory,
    ExtraCostFactory,
    ExtraCostTypeFactory,
    ServiceEnvironmentFactory,
    ServiceFactory
)
from rest_framework.test import APIClient

ANOTHER_SCROOGE_URL = 'http://another-scrooge/scrooge/rest/import-accepted-costs/'  # noqa
ANOTHER_SCROOGE_TOKEN = 'some-token'


class TestSyncRecipient(ScroogeTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestSyncRecipient, cls).setUpClass()

        cls.business_line = BusinessLineFactory(name='bl', id=100)
        cls.env_prod = EnvironmentFactory(name='prod')
        cls.env_test = EnvironmentFactory(name='test')
        cls.service_env_1 = ServiceEnvironmentFactory(
            service__ci_uid='uid-1',
            service__business_line=cls.business_line,
            environment=cls.env_prod
        )
        cls.service_2 = ServiceFactory(
            ci_uid='uid-2', business_line=cls.business_line
        )
        cls.service_env_2 = ServiceEnvironmentFactory(
            service=cls.service_2, environment=cls.env_prod
        )
        cls.service_env_3 = ServiceEnvironmentFactory(
            service=cls.service_2, environment=cls.env_test
        )
        ServiceEnvironmentFactory(
            service__ci_uid='uid-other-business-line',
            service__business_line__name='another-business-line',
            environment=cls.env_test
        )

    def test_should_return_403_when_user_is_not_admin(self):
        user = get_user_model().objects.create_user(
            'test', 'test@test.test', 'test', is_staff=False
        )
        client = APIClient()
        client.force_authenticate(user)
        resp = client.post(
            reverse(
                'import_accepted_costs',
            ),
            {
                'date_from': '2018-09-01',
                'date_to': '2018-09-30',
                'type': 'infrastructure',
                'costs': []
            },
            format='json'
        )
        self.assertEqual(resp.status_code, 403)

    @override_settings(
        ACCEPTED_COSTS_SYNC_HANDLER_BUSINESS_LINE_ID=100,
    )
    def test_should_save_received_costs_as_extra_cost(self):
        user = get_user_model().objects.create_user(
            'test', 'test@test.test', 'test', is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user)

        self.assertEqual(ExtraCost.objects.count(), 0)

        resp = client.post(
            reverse(
                'import_accepted_costs',
            ),
            {
                'date_from': '2018-09-01',
                'date_to': '2018-09-30',
                'type': 'infrastructure',
                'costs': [
                    {"environment": "prod", "service_uid": "uid-1", "total_cost": 70.00},  # noqa
                    {"environment": "prod", "service_uid": "uid-2", "total_cost": 140.00},  # noqa
                    {"environment": "test", "service_uid": "uid-2", "total_cost": 210.00},  # noqa
                    {"environment": "test", "service_uid": "uid-other-business-line", "total_cost": 500.00}  # noqa; should be skipped
                ]
            },
            format='json'
        )
        self.assertEqual(resp.status_code, 202)

        # validate saved data
        self.assertEqual(ExtraCost.objects.count(), 3)
        date_from = datetime.date(2018, 9, 1)
        date_to = datetime.date(2018, 9, 30)
        self.assertItemsEqual(list(ExtraCost.objects.values_list(
            'service_environment__service__ci_uid',
            'service_environment__environment__name',
            'start',
            'end',
            'cost',
            'extra_cost_type__name',
        )), [
            ('uid-1', 'prod', date_from, date_to, 70.0, 'infrastructure'),
            ('uid-2', 'prod', date_from, date_to, 140.0, 'infrastructure'),
            ('uid-2', 'test', date_from, date_to, 210.0, 'infrastructure'),
        ])

    @override_settings(
        ACCEPTED_COSTS_SYNC_HANDLER_BUSINESS_LINE_ID=100,
    )
    def test_should_save_received_costs_as_extra_cost_and_delete_previously_saved_costs(self):  # noqa
        user = get_user_model().objects.create_user(
            'test', 'test@test.test', 'test', is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user)

        extra_cost_type = ExtraCostTypeFactory(name='infrastructure')
        ExtraCostFactory(
            extra_cost_type=extra_cost_type,
            cost=1000.0,
            start='2018-09-01',
            end='2018-09-30'
        )
        self.assertEqual(ExtraCost.objects.count(), 1)

        resp = client.post(
            reverse(
                'import_accepted_costs',
            ),
            {
                'date_from': '2018-09-01',
                'date_to': '2018-09-30',
                'type': 'infrastructure',
                'costs': [
                    {"environment": "prod", "service_uid": "uid-1", "total_cost": 70.00},  # noqa
                    {"environment": "prod", "service_uid": "uid-2", "total_cost": 140.00},  # noqa
                    {"environment": "test", "service_uid": "uid-2", "total_cost": 210.00},  # noqa
                    {"environment": "test", "service_uid": "uid-other-business-line", "total_cost": 500.00}  # noqa; should be skipped
                ]
            },
            format='json'
        )
        self.assertEqual(resp.status_code, 202)

        # validate saved data
        self.assertEqual(ExtraCost.objects.count(), 3)
        date_from = datetime.date(2018, 9, 1)
        date_to = datetime.date(2018, 9, 30)
        self.assertItemsEqual(list(ExtraCost.objects.values_list(
            'service_environment__service__ci_uid',
            'service_environment__environment__name',
            'start',
            'end',
            'cost',
            'extra_cost_type__name'
        )), [
            ('uid-1', 'prod', date_from, date_to, 70.0, 'infrastructure'),
            ('uid-2', 'prod', date_from, date_to, 140.0, 'infrastructure'),
            ('uid-2', 'test', date_from, date_to, 210.0, 'infrastructure'),
        ])
