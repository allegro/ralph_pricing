# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.test.utils import override_settings

from ralph_scrooge.plugins.collect._openstack_base import (
    OpenStackBasePlugin,
    TenantNotFoundError,
)
from ralph_scrooge.models import DailyUsage
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.plugins.collect.samples.openstack import (
    SAMPLE_OPENSTACK,
)
from ralph_scrooge.tests.utils.factory import (
    DailyTenantInfoFactory,
    OpenstackDailyUsageTypeFactory,
    TenantInfoFactory,
    WarehouseFactory,
)

CEILOMETER_SETTINGS = [
    {
        'CONNECTION': "mysql://foo:bar@example.com:3306",
        'WAREHOUSE': 'WH1',
    },
    {
        'CONNECTION': "mysql://foo:bar@example.com:3307",
        'WAREHOUSE': 'WH2',
        'USAGE_PREFIX': 'OS_VERSION',
    }
]
TEST_SETTINGS_SCROOGE_OPENSTACK_CEILOMETER = {
    'OPENSTACK_CEILOMETER': CEILOMETER_SETTINGS
}


class TestOpenStackBasePlugin(ScroogeTestCase):
    def setUp(self):
        self.today = datetime.date(2014, 7, 1)
        self.yesterday = self.today - datetime.timedelta(days=1)
        self.plugin = OpenStackBasePlugin()

    def test_format_date(self):
        d = datetime.datetime(2014, 7, 1, 11, 12, 13)
        result = self.plugin._format_date(d)
        self.assertEqual(result, 1404205933.0)

    def test_get_dates_from_to(self):
        d = datetime.date(2014, 7, 1)
        result = self.plugin._get_dates_from_to(d)
        self.assertEqual(result, (
            datetime.datetime(2014, 7, 1, 0, 0, 0),
            datetime.datetime(2014, 7, 1, 23, 59, 59, 999999),
        ))

    def test_get_usage_type(self):
        flavor_name = 'Sample Flavor:test'
        usage_type = self.plugin.get_usage_type(flavor_name)
        self.assertEquals(usage_type.name, 'openstack.Sample Flavor:test')
        self.assertEquals(usage_type.symbol, 'openstack.sample_flavor.test')

    def test_get_usage_type_with_prefix(self):
        flavor_name = 'Sample Flavor:test'
        usage_type = self.plugin.get_usage_type(flavor_name, prefix='OS')
        self.assertEquals(usage_type.name, 'openstack.OS.Sample Flavor:test')
        self.assertEquals(usage_type.symbol, 'openstack.os.sample_flavor.test')

    def test_get_daily_tenant(self):
        daily_tenant = DailyTenantInfoFactory(date=self.today)
        result = self.plugin.get_daily_tenant(
            daily_tenant.tenant_info.tenant_id,
            self.today
        )
        self.assertEquals(daily_tenant, result)

    @mock.patch('ralph_scrooge.plugins.collect._openstack_base.logger')
    def test_get_daily_tenant_without_daily_tenant(self, logger_mock):
        tenant = TenantInfoFactory()
        self.plugin.get_daily_tenant(tenant.tenant_id, self.today)
        self.assertTrue(logger_mock.warning.called)

    def test_get_daily_tenant_without_tenant(self):
        tenant = TenantInfoFactory.build()
        with self.assertRaises(TenantNotFoundError):
            self.plugin.get_daily_tenant(tenant.tenant_id, self.today)

    @mock.patch('ralph_scrooge.plugins.collect._openstack_base.create_engine')
    def test_get_usages(self, create_engine_mock):
        self.plugin.query = '{from_ts} - {to_ts}'

        def execute_mock(sql):
            return SAMPLE_OPENSTACK

        connection_mock = mock.MagicMock()
        connection_mock.execute.side_effect = execute_mock

        engine_mock = mock.MagicMock()
        engine_mock.connect.return_value = connection_mock

        create_engine_mock.return_value = engine_mock

        result = self.plugin.get_usages(
            self.yesterday,
            "mysql://foo:bar@example.com:3306"
        )
        self.assertEqual(result, SAMPLE_OPENSTACK)

    def test_save_usages(self):
        warehouse = WarehouseFactory()
        daily_tenant1 = DailyTenantInfoFactory(date=self.today)
        daily_tenant2 = DailyTenantInfoFactory(date=self.today)
        daily_tenant3 = DailyTenantInfoFactory.build(date=self.today)
        instance1_usage_type = self.plugin.get_usage_type('instance1')
        usages = [
            (daily_tenant1.tenant_info.tenant_id, 100, 'instance1'),
            (daily_tenant1.tenant_info.tenant_id, 200, 'instance2'),
            (daily_tenant2.tenant_info.tenant_id, 300, 'instance1'),
            (daily_tenant3.tenant_info.tenant_id, 100, 'instance1'),
        ]
        self.assertEquals(
            (3, 4),
            self.plugin.save_usages(usages, self.today, warehouse)
        )
        daily_tenant2_usage = daily_tenant2.dailyusage_set.all()[:1].get()
        self.assertEquals(DailyUsage.objects.count(), 3)
        self.assertEquals(daily_tenant2_usage.date, self.today)
        self.assertEquals(
            daily_tenant2_usage.service_environment,
            daily_tenant2.service_environment
        )
        self.assertEquals(
            daily_tenant2_usage.daily_pricing_object.id,
            daily_tenant2.dailypricingobject_ptr.id
        )
        self.assertEquals(daily_tenant2_usage.value, 300)
        self.assertEquals(daily_tenant2_usage.type, instance1_usage_type)
        self.assertEquals(daily_tenant2_usage.warehouse, warehouse)

    def test_save_usages_with_prefix(self):
        warehouse = WarehouseFactory()
        daily_tenant1 = DailyTenantInfoFactory(date=self.today)
        daily_tenant2 = DailyTenantInfoFactory(date=self.today)
        daily_tenant3 = DailyTenantInfoFactory.build(date=self.today)
        # because of prefix, this usage type should not be used
        instance1_usage_type = self.plugin.get_usage_type('instance1')
        usages = [
            (daily_tenant1.tenant_info.tenant_id, 100, 'instance1'),
            (daily_tenant1.tenant_info.tenant_id, 200, 'instance2'),
            (daily_tenant2.tenant_info.tenant_id, 300, 'instance1'),
            (daily_tenant3.tenant_info.tenant_id, 100, 'instance1'),
        ]
        self.assertEquals(
            (3, 4),
            self.plugin.save_usages(usages, self.today, warehouse, prefix='OS')
        )
        daily_tenant2_usage = daily_tenant2.dailyusage_set.all()[:1].get()
        self.assertEquals(DailyUsage.objects.count(), 3)
        self.assertEquals(daily_tenant2_usage.date, self.today)
        self.assertEquals(
            daily_tenant2_usage.service_environment,
            daily_tenant2.service_environment
        )
        self.assertEquals(
            daily_tenant2_usage.daily_pricing_object.id,
            daily_tenant2.dailypricingobject_ptr.id
        )
        self.assertEquals(daily_tenant2_usage.value, 300)
        self.assertNotEqual(daily_tenant2_usage.type, instance1_usage_type)
        self.assertEquals(daily_tenant2_usage.warehouse, warehouse)

    def test_clear_previous_usages(self):
        OpenstackDailyUsageTypeFactory.create_batch(
            20,
            date=self.today,
        )
        OpenstackDailyUsageTypeFactory.create_batch(
            10,
            date=self.yesterday,
        )
        self.assertEquals(DailyUsage.objects.count(), 30)
        self.plugin.clear_previous_usages(self.today)
        self.assertEquals(DailyUsage.objects.count(), 10)

    @mock.patch('ralph_scrooge.plugins.collect._openstack_base.OpenStackBasePlugin.get_usages')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect._openstack_base.OpenStackBasePlugin.clear_previous_usages')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect._openstack_base.OpenStackBasePlugin.save_usages')  # noqa
    @override_settings(**TEST_SETTINGS_SCROOGE_OPENSTACK_CEILOMETER)
    def test_run_plugin(
        self,
        save_usages_mock,
        clear_previous_usages_mock,
        get_usages_mock,
    ):
        get_usages_mock.return_value = SAMPLE_OPENSTACK
        save_usages_mock.return_value = (3, 4)

        warehouse1 = WarehouseFactory(name='WH1')
        warehouse2 = WarehouseFactory(name='WH2')

        result = self.plugin.run_plugin(
            CEILOMETER_SETTINGS,
            self.today
        )
        self.assertEquals(result, (6, 8))
        clear_previous_usages_mock.assert_called(self.today)
        self.assertEquals(get_usages_mock.call_count, 2)
        get_usages_mock.assert_any_call(
            self.today,
            CEILOMETER_SETTINGS[0]['CONNECTION'],
            {}
        )
        self.assertEquals(get_usages_mock.call_count, 2)
        save_usages_mock.assert_any_call(
            SAMPLE_OPENSTACK,
            self.today,
            warehouse1,
            prefix=None,
        )
        save_usages_mock.assert_any_call(
            SAMPLE_OPENSTACK,
            self.today,
            warehouse2,
            prefix='OS_VERSION',
        )
