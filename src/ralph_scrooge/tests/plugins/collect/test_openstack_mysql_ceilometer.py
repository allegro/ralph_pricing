# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock
import time

from django.test import TestCase
from django.test.utils import override_settings

from ralph_scrooge.plugins.collect.openstack_mysql_ceilometer import (
    openstack_mysql_ceilometer as ceilometer_mysql_plugin,
    clear_ceilometer_stats,
    DailyTenantNotFoundError,
    get_daily_tenant,
    get_usage_type,
    get_ceilometer_usages,
    save_ceilometer_usages,
    TenantNotFoundError,
)
from ralph_scrooge.models import DailyUsage
from ralph_scrooge.tests.plugins.collect.samples.ceilometer import (
    SAMPLE_CEILOMETER,
)
from ralph_scrooge.tests.utils.factory import (
    DailyTenantInfoFactory,
    OpenstackDailyUsageTypeFactory,
    TenantInfoFactory,
    WarehouseFactory,
)

CEILOMETER_SETTINGS = [
    {
        'CEILOMETER_CONNECTION': "mysql://foo:bar@example.com:3306",
        'WAREHOUSE': 'WH1',
    },
    {
        'CEILOMETER_CONNECTION': "mysql://foo:bar@example.com:3307",
        'WAREHOUSE': 'WH2',
    }
]
TEST_SETTINGS_SCROOGE_OPENSTACK_CEILOMETER = {
    'OPENSTACK_CEILOMETER': CEILOMETER_SETTINGS
}


class TestOpenStackCeilometer(TestCase):
    def setUp(self):
        self.today = datetime.date(2014, 7, 1)
        self.yesterday = self.today - datetime.timedelta(days=1)

    def test_get_usage_type(self):
        flavor_name = 'Sample Flavor:test'
        usage_type = get_usage_type(flavor_name)
        self.assertEquals(usage_type.name, 'openstack.Sample Flavor:test')
        self.assertEquals(usage_type.symbol, 'openstack.sample_flavor.test')
        self.assertFalse(usage_type.show_in_services_report)

    def test_get_daily_tenant(self):
        daily_tenant = DailyTenantInfoFactory(date=self.today)
        result = get_daily_tenant(
            daily_tenant.tenant_info.tenant_id,
            self.today
        )
        self.assertEquals(daily_tenant, result)

    def test_get_daily_tenant_without_daily_tenant(self):
        tenant = TenantInfoFactory()
        with self.assertRaises(DailyTenantNotFoundError):
            get_daily_tenant(tenant.tenant_id, self.today)

    def test_get_daily_tenant_without_tenant(self):
        tenant = TenantInfoFactory.build()
        with self.assertRaises(TenantNotFoundError):
            get_daily_tenant(tenant.tenant_id, self.today)

    @mock.patch('ralph_scrooge.plugins.collect.openstack_mysql_ceilometer.create_engine')  # noqa
    def test_get_ceilometer_usages(self, create_engine_mock):
        from_ts = time.mktime(self.yesterday.timetuple())
        to_ts = time.mktime(self.today.timetuple())

        def execute_mock(sql):
            self.assertTrue(str(from_ts) in sql)
            self.assertTrue(str(to_ts) in sql)
            return SAMPLE_CEILOMETER

        connection_mock = mock.MagicMock()
        connection_mock.execute.side_effect = execute_mock

        engine_mock = mock.MagicMock()
        engine_mock.connect.return_value = connection_mock

        create_engine_mock.return_value = engine_mock

        result = get_ceilometer_usages(
            self.today,
            "mysql://foo:bar@example.com:3306"
        )
        self.assertEqual(result, SAMPLE_CEILOMETER)

    def test_save_ceilometer_usages(self):
        warehouse = WarehouseFactory()
        daily_tenant1 = DailyTenantInfoFactory(date=self.today)
        daily_tenant2 = DailyTenantInfoFactory(date=self.today)
        daily_tenant3 = DailyTenantInfoFactory.build(date=self.today)
        instance1_usage_type = get_usage_type('instance1')
        usages = [
            (daily_tenant1.tenant_info.tenant_id, 100, 'instance1'),
            (daily_tenant1.tenant_info.tenant_id, 200, 'instance2'),
            (daily_tenant2.tenant_info.tenant_id, 300, 'instance1'),
            (daily_tenant3.tenant_info.tenant_id, 100, 'instance1'),
        ]
        self.assertEquals(
            (3, 4),
            save_ceilometer_usages(usages, self.today, warehouse)
        )
        daily_tenant2_usage = daily_tenant2.dailyusage_set.all()[:1].get()
        self.assertEquals(DailyUsage.objects.count(), 3)
        self.assertEquals(daily_tenant2_usage.date, self.today)
        self.assertEquals(
            daily_tenant2_usage.service_environment,
            daily_tenant2.service_environment
        )
        self.assertEquals(
            daily_tenant2_usage.daily_pricing_object,
            daily_tenant2.dailypricingobject_ptr
        )
        self.assertEquals(daily_tenant2_usage.value, 50)
        self.assertEquals(daily_tenant2_usage.type, instance1_usage_type)
        self.assertEquals(daily_tenant2_usage.warehouse, warehouse)

    def test_clear_ceilometer_stats(self):
        OpenstackDailyUsageTypeFactory.create_batch(
            20,
            date=self.today,
        )
        OpenstackDailyUsageTypeFactory.create_batch(
            10,
            date=self.yesterday,
        )
        self.assertEquals(DailyUsage.objects.count(), 30)
        clear_ceilometer_stats(self.today)
        self.assertEquals(DailyUsage.objects.count(), 10)

    @mock.patch('ralph_scrooge.plugins.collect.openstack_mysql_ceilometer.get_ceilometer_usages')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect.openstack_mysql_ceilometer.clear_ceilometer_stats')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect.openstack_mysql_ceilometer.save_ceilometer_usages')  # noqa
    @override_settings(**TEST_SETTINGS_SCROOGE_OPENSTACK_CEILOMETER)
    def test_ceilometer_mysql_plugin(
        self,
        save_ceilometer_usages_mock,
        clear_ceilometer_stats_mock,
        get_ceilometer_usages_mock,
    ):
        get_ceilometer_usages_mock.return_value = SAMPLE_CEILOMETER
        save_ceilometer_usages_mock.return_value = (3, 4)

        warehouse1 = WarehouseFactory(name='WH1')
        warehouse2 = WarehouseFactory(name='WH2')

        result = ceilometer_mysql_plugin(self.today)
        self.assertEquals(result, (True, 'Ceilometer usages: 6 new, 8 total'))
        clear_ceilometer_stats_mock.assert_called(self.today)
        self.assertEquals(get_ceilometer_usages_mock.call_count, 2)
        get_ceilometer_usages_mock.assert_any_call(
            self.today,
            CEILOMETER_SETTINGS[0]['CEILOMETER_CONNECTION'],
        )
        self.assertEquals(get_ceilometer_usages_mock.call_count, 2)
        save_ceilometer_usages_mock.assert_any_call(
            SAMPLE_CEILOMETER,
            self.today,
            warehouse1,
        )
        save_ceilometer_usages_mock.assert_any_call(
            SAMPLE_CEILOMETER,
            self.today,
            warehouse2,
        )
