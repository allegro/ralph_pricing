# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.test import TestCase
from django.test.utils import override_settings

from ralph_scrooge.models import PricingObjectType
from ralph_scrooge.plugins.collect.tenant import (
    get_tenant_service,
    get_tenant_unknown_service,
    InvalidTenantService,
    save_tenant_info,
    save_daily_tenant_info,
    tenant as tenant_plugin,
    UnknownServiceNotConfigured,
)
from ralph_scrooge.tests.utils.factory import (
    ServiceFactory,
    TenantInfoFactory,
)


TEST_SETTINGS_SITES = dict(
    OPENSTACK_SITES=[
        {
            'OS_METERING_URL': "http://127.0.0.1:8777",
            'OS_TENANT_NAME': 'testtenant',
            'OS_USERNAME': 'testuser',
            'OS_PASSWORD': 'supersecretpass',
            'OS_AUTH_URL': "http://127.0.0.1:5000/v2.0",
            'CEILOMETER_CONNECTION': "mysql://foo:bar@example.com:3306",
            'WAREHOUSE': 'WH1',
        },
        {
            'OS_METERING_URL': "http://127.0.0.2:8777",
            'OS_TENANT_NAME': 'testtenant2',
            'OS_USERNAME': 'testuser2',
            'OS_PASSWORD': 'supersecretpass2',
            'OS_AUTH_URL': "http://127.0.0.2:5000/v2.0",
            'CEILOMETER_CONNECTION': "mysql://foo:bar@example.com:3307",
            'WAREHOUSE': 'WH2',
        },
    ],
)
TEST_SETTINGS_UNKNOWN_SERVICES = dict(
    UNKNOWN_SERVICES={
        'tenant': 'os-1'
    }
)
TEST_SETTINGS_TENANT_FIELD = dict(
    OPENSTACK_TENANT_SERVICE_FIELD='tenant_service'
)
# join settings
TEST_SETTINGS = reduce(
    lambda a, d: a.update(d) or a,
    [
        TEST_SETTINGS_SITES,
        TEST_SETTINGS_UNKNOWN_SERVICES,
        TEST_SETTINGS_TENANT_FIELD
    ],
    {}
)


class TestServiceCollectPlugin(TestCase):
    def setUp(self):
        self.service = ServiceFactory()
        self.unknown_service = ServiceFactory()
        self.today = datetime.date(2014, 7, 1)

    def _get_sample_tenant(self):
        """
        Sample tenant from keystoneclient
        """
        return mock.Mock(
            id='12345qwerty',
            description='qwerty;asdfg;',
            name='sample_tenant',
            enabled=True,
        )

    def _compare_tenants(self, sample_tenant, tenant_info):
        self.assertEquals(tenant_info.tenant_id, sample_tenant.id)
        self.assertEquals(tenant_info.name, sample_tenant.name)
        self.assertEquals(tenant_info.remarks, sample_tenant.description)
        self.assertEquals(tenant_info.type, PricingObjectType.tenant)

    @override_settings(**TEST_SETTINGS_TENANT_FIELD)
    def test_get_tenant_service(self):
        tenant = self._get_sample_tenant()
        service = ServiceFactory()
        setattr(
            tenant,
            TEST_SETTINGS_TENANT_FIELD['OPENSTACK_TENANT_SERVICE_FIELD'],
            service.name  # TODO: change to symbol
        )
        self.assertEquals(service, get_tenant_service(tenant))

    @override_settings(**TEST_SETTINGS_TENANT_FIELD)
    def test_get_tenant_service_invalid_service(self):
        tenant = self._get_sample_tenant()
        service = ServiceFactory.build()
        setattr(
            tenant,
            TEST_SETTINGS_TENANT_FIELD['OPENSTACK_TENANT_SERVICE_FIELD'],
            service.name  # TODO: change to symbol
        )
        with self.assertRaises(InvalidTenantService):
            get_tenant_service(tenant)

    @override_settings(**TEST_SETTINGS_TENANT_FIELD)
    def test_get_tenant_service_without_service_field(self):
        tenant = self._get_sample_tenant()
        setattr(
            tenant,
            TEST_SETTINGS_TENANT_FIELD['OPENSTACK_TENANT_SERVICE_FIELD'],
            None
        )
        with self.assertRaises(InvalidTenantService):
            get_tenant_service(tenant)

    @mock.patch('ralph_scrooge.plugins.collect.tenant.get_tenant_service')
    def test_save_tenant_info(self, get_tenant_service_mock):
        get_tenant_service_mock.return_value = self.service
        sample_tenant = self._get_sample_tenant()
        created, tenant_info = save_tenant_info(
            sample_tenant,
            self.unknown_service,
        )
        self.assertTrue(created)
        self._compare_tenants(sample_tenant, tenant_info)
        self.assertEquals(tenant_info.service, self.service)

    @mock.patch('ralph_scrooge.plugins.collect.tenant.get_tenant_service')
    def test_save_tenant_info_unknown_service(self, get_tenant_service_mock):
        get_tenant_service_mock.side_effect = InvalidTenantService()
        sample_tenant = self._get_sample_tenant()
        created, tenant_info = save_tenant_info(
            sample_tenant,
            self.unknown_service,
        )
        self.assertTrue(created)
        self._compare_tenants(sample_tenant, tenant_info)
        self.assertEquals(tenant_info.service, self.unknown_service)

    def test_save_daily_tenant_info(self):
        tenant_info = TenantInfoFactory()
        sample_tenant = self._get_sample_tenant()
        result = save_daily_tenant_info(sample_tenant, tenant_info, self.today)
        self.assertEquals(result.tenant_info, tenant_info)
        self.assertEquals(result.pricing_object, tenant_info)
        self.assertEquals(result.date, self.today)
        self.assertEquals(result.service, tenant_info.service)
        self.assertEquals(result.enabled, sample_tenant.enabled)

    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES)
    def test_get_tenant_unknown_service(self):
        service = ServiceFactory(
            ci_uid=TEST_SETTINGS_UNKNOWN_SERVICES['UNKNOWN_SERVICES']['tenant']
        )
        self.assertEquals(service, get_tenant_unknown_service())

    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES)
    def test_get_tenant_unknown_service_invalid_config(self):
        ServiceFactory()
        with self.assertRaises(UnknownServiceNotConfigured):
            get_tenant_unknown_service()

    def test_get_tenant_unknown_service_not_configured(self):
        with self.assertRaises(UnknownServiceNotConfigured):
            get_tenant_unknown_service()

    @mock.patch('ralph_scrooge.plugins.collect.tenant.get_tenants_list')
    @mock.patch('ralph_scrooge.plugins.collect.tenant.update_tenant')
    @override_settings(**TEST_SETTINGS)
    def test_tenant_plugin(self, update_tenant_mock, get_tenants_list_mock):
        unknown_service = ServiceFactory(
            ci_uid=TEST_SETTINGS_UNKNOWN_SERVICES['UNKNOWN_SERVICES']['tenant']
        )
        update_tenant_mock.return_value = True
        tenants_list = [self._get_sample_tenant()] * 5
        get_tenants_list_mock.return_value = tenants_list
        result = tenant_plugin(self.today)
        self.assertEquals(
            result,
            (True, 'Tenants: 10 new, 0 updated, 10 total')
        )
        self.assertEquals(get_tenants_list_mock.call_count, 2)
        self.assertEquals(update_tenant_mock.call_count, 10)
        update_tenant_mock.assert_any_call(
            tenants_list[0],
            self.today,
            unknown_service
        )
        for site in TEST_SETTINGS_SITES['OPENSTACK_SITES']:
            get_tenants_list_mock.assert_any_call(site)

    @override_settings(**TEST_SETTINGS_TENANT_FIELD)
    def test_tenant_plugin_unknown_service_not_configured(self):
        result = tenant_plugin(self.today)
        self.assertEquals(
            result,
            (False, 'Unknown service not configured for tenant plugin')
        )

    def test_tenant_plugin_service_field_not_configured(self):
        result = tenant_plugin(self.today)
        self.assertEquals(
            result,
            (False, 'Tenant service field not configured')
        )
