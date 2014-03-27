# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.conf import settings
from django.test import TestCase

from ralph_pricing.models import DailyUsage, Venture
from ralph_pricing.plugins.collects.openstack import (
    openstack as openstack_runner,
)
from ralph_pricing.tests.collect_plugins.samples.openstack import (
    simple_tenant_usage_data,
    tenants,
    tenants_data,
    tenants_usages_data,
)


class MockOpenStack(object):
    """ Simple mock for OpenStack network library """
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self

    def simple_tenant_usage(self, start, end):
        return simple_tenant_usage_data

    def query(self, query, url, **kwargs):
        if query == 'os-simple-tenant-usage':
            result = tenants_usages_data
        elif query == 'simple-tenant-usage':
            result = simple_tenant_usage_data
        elif query == 'tenants':
            result = tenants_data
        return result

    def auth(self, *args, **kwargs):
        pass

    def get_ventures(self):
        return tenants

    def __getattr__(self, name):
        return mock.Mock()


class TestOpenstack(TestCase):
    def setUp(self):
        Venture(
            name='Test Venture1',
            symbol='test_venture1',
            venture_id='1'
        ).save()
        Venture(
            name='Test Venture2',
            symbol='test_venture2',
            venture_id='2'
        ).save()
        Venture(
            name='Test Venture3',
            symbol='test_venture3',
            venture_id='3'
        ).save()

    def test_set_usages(self):
        """ OpenStack usages Test Case """
        # fake setting need to run plugin
        settings.OPENSTACK_URL = '/'
        settings.OPENSTACK_USER = 'test'
        settings.OPENSTACK_PASSWORD = 'test'
        with mock.patch(
            'ralph_pricing.plugins.collects.openstack.OpenStack'
        ) as OpenStack:
            OpenStack.side_effect = MockOpenStack
            status, message, arg = openstack_runner(
                today=datetime.datetime.today()
            )
            self.assertTrue(status)
            # usages venture1
            usage_venture1 = DailyUsage.objects.filter(
                pricing_venture__symbol='test_venture1',
            )
            self.assertEqual(len(usage_venture1), 5)
            memory_usage_venture1 = usage_venture1.get(
                type__name='OpenStack 10000 Memory GiB Hours'
            )
            volume_usage_venutre1 = usage_venture1.get(
                type__name='OpenStack 10000 Volume GiB Hours'
            )
            vcpus_usage_venutre1 = usage_venture1.get(
                type__name='OpenStack 10000 CPU Hours'
            )
            disk_usage_venutre1 = usage_venture1.get(
                type__name='OpenStack 10000 Disk GiB Hours'
            )
            images_usage_venutre1 = usage_venture1.get(
                type__name='OpenStack 10000 Images GiB Hours'
            )
            self.assertEqual(memory_usage_venture1.value, 393216.0 / 1024)
            self.assertEqual(volume_usage_venutre1.value, 480.0)
            self.assertEqual(vcpus_usage_venutre1.value, 192.0)
            self.assertEqual(disk_usage_venutre1.value, 768.0)
            self.assertEqual(images_usage_venutre1.value, 199.3)
            # usages venture2
            usage_venture2 = DailyUsage.objects.filter(
                pricing_venture__symbol='test_venture2',
            )
            self.assertEqual(len(usage_venture2), 5)
            memory_usage_venture2 = usage_venture2.get(
                type__name='OpenStack 10000 Memory GiB Hours'
            )
            volume_usage_venutre2 = usage_venture2.get(
                type__name='OpenStack 10000 Volume GiB Hours'
            )
            vcpus_usage_venutre2 = usage_venture2.get(
                type__name='OpenStack 10000 CPU Hours'
            )
            disk_usage_venutre2 = usage_venture2.get(
                type__name='OpenStack 10000 Disk GiB Hours'
            )
            images_usage_venutre2 = usage_venture2.get(
                type__name='OpenStack 10000 Images GiB Hours'
            )
            self.assertEqual(memory_usage_venture2.value, 786432.0 / 1024)
            self.assertEqual(volume_usage_venutre2.value, 28800.0)
            self.assertEqual(vcpus_usage_venutre2.value, 384.0)
            self.assertEqual(disk_usage_venutre2.value, 1536.0)
            self.assertEqual(images_usage_venutre2.value, 315.0)
            # no data for venture3
            usage_venture3 = DailyUsage.objects.filter(
                pricing_venture__symbol='test_venture3',
            )
            self.assertEqual(len(usage_venture3), 0)

    def test_fail_plugin(self):
        """ Testing not configured plugin """
        with mock.patch(
            'ralph_pricing.plugins.collects.openstack.OpenStack'
        ) as OpenStack:
            OpenStack.side_effect = MockOpenStack
            status, message, arg = openstack_runner(
                today=datetime.datetime.today()
            )
            self.assertFalse(status)
