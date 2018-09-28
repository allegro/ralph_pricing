# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals

import json

import responses
from django.test import override_settings
from ralph_scrooge.sync.publisher import publish_accepted_costs_dump
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import (
    DailyCostFactory,
    EnvironmentFactory,
    ServiceEnvironmentFactory,
    ServiceFactory,
    UsageTypeFactory
)

ANOTHER_SCROOGE_URL = 'http://another-scrooge/scrooge/rest/import-accepted-costs/'  # noqa
ANOTHER_SCROOGE_TOKEN = 'some-token'


class TestPublisher(ScroogeTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestPublisher, cls).setUpClass()

        cls.env_prod = EnvironmentFactory(name='prod')
        cls.env_test = EnvironmentFactory(name='test')
        cls.service_env_1 = ServiceEnvironmentFactory(
            service__ci_uid='uid-1', environment=cls.env_prod
        )
        cls.service_2 = ServiceFactory(ci_uid='uid-2')
        cls.service_env_2 = ServiceEnvironmentFactory(
            service=cls.service_2, environment=cls.env_prod
        )
        cls.service_env_3 = ServiceEnvironmentFactory(
            service=cls.service_2, environment=cls.env_test
        )
        ServiceEnvironmentFactory(
            service__ci_uid='uid-unused', environment=cls.env_test
        )

        usage_type = UsageTypeFactory()
        for day in range(1, 11):
            for i, se in enumerate([
                cls.service_env_1,
                cls.service_env_2,
                cls.service_env_3
            ], start=1):
                for forecast in [True, False]:
                    DailyCostFactory(
                        service_environment=se,
                        cost=i*10,
                        date='2018-09-{}'.format(day),
                        forecast=forecast,
                        type=usage_type
                    )

    @override_settings(
        ACCEPTED_COSTS_SYNC_RECIPIENTS=[
            (ANOTHER_SCROOGE_URL, ANOTHER_SCROOGE_TOKEN)
        ],
        ACCEPTED_COSTS_SYNC_TYPE='infrastructure',
    )
    @responses.activate
    def test_should_send_dump_of_costs_to_recipient(self):
        responses.add(responses.POST, ANOTHER_SCROOGE_URL, status=202)
        publish_accepted_costs_dump('2018-09-02', '2018-09-08')

        self.assertEqual(len(responses.calls), 1)
        request = responses.calls[0].request
        json_body = json.loads(request.body)
        self.assertEqual(json_body.pop('costs'), [
                {"environment": "prod", "service_uid": "uid-1", "total_cost": 70.00},  # noqa
                {"environment": "prod", "service_uid": "uid-2", "total_cost": 140.00},  # noqa
                {"environment": "test", "service_uid": "uid-2", "total_cost": 210.00}  # noqa
        ])
        self.assertEqual(json_body, {
            "date_from": "2018-09-02",
            "date_to": "2018-09-08",
            "type": "infrastructure",
        })
        self.assertEqual(
            request.headers['Authorization'],
            'Token {}'.format(ANOTHER_SCROOGE_TOKEN)
        )
