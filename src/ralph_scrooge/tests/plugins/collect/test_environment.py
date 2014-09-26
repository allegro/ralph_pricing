# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
import mock

from django.test import TestCase

from ralph_scrooge.models import Environment
from ralph_scrooge.plugins.collect.environment import (
    environment as environment_plugin,
    update_environment
)
from ralph_scrooge.tests.plugins.collect.samples.environment import (
    SAMPLE_ENVIRONMENTS,
)


class TestEnvironmentCollectPlugin(TestCase):
    def setUp(self):
        self.today = date(2014, 07, 01)

    def _compare_environments(self, environment, sample_data):
        self.assertEquals(environment.name, sample_data['name'])
        self.assertEquals(environment.ci_id, sample_data['ci_id'])

    def test_add_environment(self):
        sample_data = SAMPLE_ENVIRONMENTS[0]
        self.assertTrue(update_environment(sample_data, self.today))
        environment = Environment.objects.get(ci_id=sample_data['ci_id'])
        self._compare_environments(environment, sample_data)

    def test_update_environment(self):
        sample_data = SAMPLE_ENVIRONMENTS[0]
        self.assertTrue(update_environment(sample_data, self.today))
        environment = Environment.objects.get(ci_id=sample_data['ci_id'])
        self._compare_environments(environment, sample_data)

        sample_data2 = SAMPLE_ENVIRONMENTS[1]
        sample_data2['ci_id'] = sample_data['ci_id']
        self.assertFalse(update_environment(sample_data2, self.today))
        environment = Environment.objects.get(
            ci_id=sample_data2['ci_id']
        )
        self._compare_environments(environment, sample_data2)

    @mock.patch('ralph_scrooge.plugins.collect.environment.update_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect.environment.get_environments')  # noqa
    def test_batch_update(
        self, get_environments_mock,
        update_environment_mock
    ):
        def sample_update_environment(data, date):
            return data['ci_id'] % 2 == 0

        def sample_get_environments():
            for environment in SAMPLE_ENVIRONMENTS:
                yield environment

        update_environment_mock.side_effect = sample_update_environment
        get_environments_mock.side_effect = sample_get_environments
        result = environment_plugin(today=self.today)
        self.assertEquals(
            result,
            (True, '1 new environment(s), 1 updated, 2 total')
        )
        update_environment_mock.call_count = 2
        update_environment_mock.assert_any_call(
            SAMPLE_ENVIRONMENTS[0],
            self.today
        )
        update_environment_mock.assert_any_call(
            SAMPLE_ENVIRONMENTS[1],
            self.today
        )
