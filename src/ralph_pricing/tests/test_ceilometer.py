# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json
import mock

from django.test import TestCase

from ralph_pricing.plugins import ceilometer
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
    @mock.patch.object(ceilometer, "requests")
    def test_get_tenants(self, requests_mock):
        response_token_mock = mock.MagicMock()
        response_token_mock.content = json.dumps(
            {
                'access': {
                    'token': {'id': '12345qwert'},
                }
            }
        )
        requests_mock.post.return_value = response_token_mock
        response_tenant_mock = mock.MagicMock()
        response_tenant_mock.content = json.dumps(
            {'tenants': ['tenant1', 'tenant2']},
        )
        requests_mock.get.return_value = response_tenant_mock
        res = ceilometer.get_tenants(ceilometer.settings.OPENSTACK_SITES[0])
        self.assertEqual(['tenant1', 'tenant2'], res)
        data = json.dumps({
            "auth": {
                "passwordCredentials": {
                    "username": 'testuser',
                    "password": 'supersecretpass',
                }
            }
        })
        requests_mock.post.assert_called_with(
            "http://127.0.0.1:5000/v2.0/tokens",
            data=data,
            headers={'content-type': 'application/json'},
        )
        requests_mock.get.assert_called_with(
            "http://127.0.0.1:5000/v2.0/tenants",
            headers={
                'content-type': 'application/json',
                'X-Auth-Token': '12345qwert',
            }
        )

    def test_get_ceilometer_usages(self):
        tenants = [{
            u'description': u'test;ralph;whatever',
            u'enabled': True,
            u'id': u'abcdef12345',
            u'name': u'ralph-test',
        }]
        client_mock = mock.MagicMock()
        today = datetime.date(2014, 1, 21)

        def statistics_mock(meter_name, q):
            cpu = mock.MagicMock(unit="unit", sum=1234)
            neti = mock.MagicMock(unit="unit", sum=2345)
            neto = mock.MagicMock(unit="unit", sum=3456)
            meters = {
                'cpu': cpu,
                'network.outgoing.bytes': neto,
                'network.incoming.bytes': neti,
            }
            correct_query = [
                {
                    'field': 'project_id',
                    'op': 'eq',
                    'value': 'abcdef12345',
                },
                {
                    "field": "timestamp",
                    "op": "ge",
                    "value": '2014-01-20T00:00:00',
                },
                {
                    "field": "timestamp",
                    "op": "lt",
                    "value": '2014-01-21T00:00:00',
                },
            ]
            self.assertEqual(correct_query, q)
            return [meters[meter_name]]

        client_mock.statistics.list.side_effect = statistics_mock
        res = ceilometer.get_ceilometer_usages(
            client_mock,
            tenants,
            date=today,
        )
        correct_res = {
            u'ralph': {
                u'cpu': 1234,
                u'network.incoming.bytes': 2345,
                u'network.outgoing.bytes': 3456,
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
            }
        }
        date = datetime.date(2014, 1, 21)
        ceilometer.save_ceilometer_usages(usages, date)
        usages = DailyUsage.objects.filter(pricing_venture=v)
        self.assertEqual(3, usages.count())
