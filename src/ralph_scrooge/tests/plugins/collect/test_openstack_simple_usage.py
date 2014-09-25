# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.test import TestCase

from ralph_scrooge.plugins.collect.openstack_simple_usage import (
    save_usage,
    clear_openstack_simple_usages,
    USAGE_SYMBOL_TMPL,
)
from ralph_scrooge.models import DailyUsage
from ralph_scrooge.tests.utils.factory import (
    DailyUsageFactory,
    TenantInfoFactory,
    WarehouseFactory,
    UsageTypeFactory,
)


TEST_SETTINGS = dict(
    OPENSTACK_SIMPLE_USAGES=[
        {
            'TENANT_NAME': 'testtenant',
            'USERNAME': 'testuser',
            'PASSWORD': 'supersecretpass',
            'AUTH_URL': "http://127.0.0.1:5000/v2.0",
            'REGIONS': ['R1', 'R2']
        },
        {
            'TENANT_NAME': 'testtenant',
            'USERNAME': 'testuser',
            'PASSWORD': 'supersecretpass',
            'AUTH_URL': "http://127.0.0.2:5000/v2.0",
            'REGIONS': ['R3']
        },
    ],
)


class TestOpenStackSimpleUsage(TestCase):
    def setUp(self):
        self.today = datetime.date(2014, 7, 1)
        self.yesterday = self.today - datetime.timedelta(days=1)
        self.warehouse = WarehouseFactory()

    def _get_sample_usage(self):
        usage = mock.Mock(
            tenant_id=123,
            sample1=123,
            sample2=345,
        )
        usage.to_dict = mock.Mock(
            return_value={
                'sample1': usage.sample1,
                'sample2': usage.sample2,
                'tenant_id': usage.tenant_id,
            }
        )
        return usage

    def test_save_usage(self):
        usage_types = {
            'sample1': UsageTypeFactory(),
            'sample2': UsageTypeFactory(),
        }
        usage = self._get_sample_usage()
        TenantInfoFactory(
            tenant_id=usage.tenant_id
        )
        result = save_usage(usage, self.today, usage_types, self.warehouse)
        self.assertEquals(result, True)
        self.assertEquals(DailyUsage.objects.count(), 2)

    def test_save_usage_invalid_tenant(self):
        usage = self._get_sample_usage()
        TenantInfoFactory.build(
            tenant_id=usage.tenant_id
        )
        result = save_usage(usage, self.today, [], self.warehouse)
        self.assertEquals(result, False)

    def test_clear_usages(self):
        DailyUsageFactory.create_batch(
            10,
            type__symbol=USAGE_SYMBOL_TMPL.format('abc'),
            date=self.today,
        )
        DailyUsageFactory.create_batch(
            10,
            type__symbol=USAGE_SYMBOL_TMPL.format('abc'),
            date=self.yesterday,
        )
        self.assertEquals(DailyUsage.objects.count(), 20)
        clear_openstack_simple_usages(self.today)
        self.assertEquals(DailyUsage.objects.count(), 10)

    # TODO: finish unit tests (get_usages, main plugin)
