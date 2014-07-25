# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.test import TestCase

from ralph_pricing.plugins.collects import ceilometer
from ralph_pricing.models import DailyUsage, Venture


ceilometer.settings.OPENSTACK_SITES = [
    {
        'OS_METERING_URL': "http://127.0.0.1:8777",
        'OS_TENANT_NAME': 'testtenant',
        'OS_USERNAME': 'testuser',
        'OS_PASSWORD': 'supersecretpass',
        'OS_AUTH_URL': "http://127.0.0.1:5000/v2.0",
    },
    {
        'OS_METERING_URL': "http://127.0.0.2:8777",
        'OS_TENANT_NAME': 'testtenant2',
        'OS_USERNAME': 'testuser2',
        'OS_PASSWORD': 'supersecretpass2',
        'OS_AUTH_URL': "http://127.0.0.2:5000/v2.0",
    },
]


class TestCeilometer(TestCase):
    def test_get_ceilometer_usages(self):
        tenant_mock = mock.Mock()
        tenant_mock.description = 'test;ralph;whatever'
        tenant_mock.id = 'abcdef12345'
        tenant_mock.name = 'ralph-test'
        tenants = [tenant_mock]
        today = datetime.date(2014, 1, 21)

        def execute_mock(sql):
            assert 'abcdef12345' in sql
            return [{
                'flavor': 'instance.test_flav',
                'count': 780,
            }]

        connection_mock = mock.MagicMock()
        connection_mock.execute.side_effect = execute_mock
        engine_mock = mock.MagicMock()
        with mock.patch.object(ceilometer, "create_engine") as create_mock:
            create_mock.return_value = engine_mock
            engine_mock.connect.return_value = connection_mock
            res = ceilometer.get_ceilometer_usages(
                tenants,
                date=today,
                statistics={},
                connection_string="mysql://foo:bar@example.com:3306"
            )
            correct_res = {
                u'ralph': {
                    u'openstack.instance.test_flav': 130.0,
                }
            }
            self.assertEqual(res, correct_res)

    def test_save_ceilometer_usages(self):
        v = Venture.objects.create(
            venture_id=12345,
            name="ralph-ceilo",
            symbol="ralph-ceilo",
        )
        v.save()
        usages = {
            u'ralph-ceilo': {
                u'cpu': 1234,
                u'network.incoming.bytes': 2345,
                u'network.outgoing.bytes': 3456,
                u'disk.write.requests': 4567,
                u'disk.read.requests': 5678,
            }
        }
        date = datetime.date(2014, 1, 21)
        ceilometer.save_ceilometer_usages(usages, date)
        usages = DailyUsage.objects.filter(pricing_venture=v)
        self.assertEqual(5, usages.count())
