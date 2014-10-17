# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.test import TestCase
from django.test.utils import override_settings

from ralph_scrooge.models import PRICING_OBJECT_TYPES
from ralph_scrooge.plugins.collect.tenant import (
    get_model,
    get_unknown_service_environment,
    save_tenant_info,
    save_daily_tenant_info,
    tenant as tenant_plugin,
    UnknownServiceEnvironmentNotConfiguredError,
)
from ralph_scrooge.tests.utils.factory import (
    PricingObjectModelFactory,
    ServiceEnvironmentFactory,
    TenantInfoFactory,
)

OPENSTACK_TENANTS_MODELS = ['OpenStack M1']
UNKNOWN_SERVICE_ENVIRONMENT = ('os-1', 'env1')
TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS = dict(
    UNKNOWN_SERVICES_ENVIRONMENTS={
        'tenant': {
            OPENSTACK_TENANTS_MODELS[0]: UNKNOWN_SERVICE_ENVIRONMENT,
        }
    },
    OPENSTACK_TENANTS_MODELS=OPENSTACK_TENANTS_MODELS,
)


class TestServiceCollectPlugin(TestCase):
    def setUp(self):
        self.service_environment = ServiceEnvironmentFactory()
        self.unknown_service_environment = ServiceEnvironmentFactory(
            service__name=UNKNOWN_SERVICE_ENVIRONMENT[0],
            environment__name=UNKNOWN_SERVICE_ENVIRONMENT[0],
        )
        self.today = datetime.date(2014, 7, 1)
        self.model = PricingObjectModelFactory(
            type_id=PRICING_OBJECT_TYPES.TENANT,
            name=OPENSTACK_TENANTS_MODELS[0],
        )

    def _get_sample_tenant(self):
        return {
            'device_id': 10,
            'tenant_id': '123456789',
            'service_id': self.service_environment.service.id,
            'environment_id': self.service_environment.environment.id,
            'name': 'sample_tenant',
            'model_id': self.model.model_id,
            'model_name': OPENSTACK_TENANTS_MODELS[0],
            'remarks': 'qwerty',
        }

    def _compare_tenants(self, sample_tenant, tenant_info):
        self.assertEquals(tenant_info.tenant_id, sample_tenant['tenant_id'])
        self.assertEquals(tenant_info.name, sample_tenant['name'])
        self.assertEquals(tenant_info.remarks, sample_tenant['remarks'])
        self.assertEquals(
            tenant_info.model.model_id,
            sample_tenant['model_id']
        )
        self.assertEquals(tenant_info.model.name, sample_tenant['model_name'])
        self.assertEquals(tenant_info.type_id, PRICING_OBJECT_TYPES.TENANT)

    def test_get_tenant_model(self):
        sample_tenant = self._get_sample_tenant()
        model = get_model(sample_tenant)
        self.assertEquals(model, self.model)

    def test_save_tenant_info(self):
        sample_tenant = self._get_sample_tenant()
        sample_tenant['service_id'] = self.service_environment.service.ci_id
        sample_tenant['environment_id'] = (
            self.service_environment.environment.ci_id
        )
        created, tenant_info = save_tenant_info(
            sample_tenant,
            self.unknown_service_environment
        )
        self.assertTrue(created)
        self._compare_tenants(sample_tenant, tenant_info)
        self.assertEquals(
            tenant_info.service_environment,
            self.service_environment
        )

    def test_save_tenant_info_invalid_service_environment(self):
        service_environment = ServiceEnvironmentFactory.build()
        sample_tenant = self._get_sample_tenant()
        sample_tenant['service_id'] = service_environment.service.ci_id
        sample_tenant['environment_id'] = service_environment.environment.ci_id
        created, tenant_info = save_tenant_info(
            sample_tenant,
            self.unknown_service_environment
        )
        self.assertTrue(created)
        self._compare_tenants(sample_tenant, tenant_info)
        self.assertEquals(
            tenant_info.service_environment,
            self.unknown_service_environment
        )

    def test_save_daily_tenant_info(self):
        tenant_info = TenantInfoFactory()
        sample_tenant = self._get_sample_tenant()
        result = save_daily_tenant_info(
            sample_tenant,
            tenant_info,
            self.today
        )
        self.assertEquals(result.tenant_info, tenant_info)
        self.assertEquals(result.pricing_object, tenant_info)
        self.assertEquals(result.date, self.today)
        self.assertEquals(
            result.service_environment,
            tenant_info.service_environment
        )

    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS)
    def test_get_tenant_unknown_service_environment(self):
        service_environment = ServiceEnvironmentFactory(
            service__ci_uid=UNKNOWN_SERVICE_ENVIRONMENT[0],
            environment__name=UNKNOWN_SERVICE_ENVIRONMENT[1],
        )
        self.assertEquals(
            service_environment,
            get_unknown_service_environment(OPENSTACK_TENANTS_MODELS[0])
        )

    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS)
    def test_get_tenant_unknown_service_invalid_config(self):
        ServiceEnvironmentFactory()
        with self.assertRaises(UnknownServiceEnvironmentNotConfiguredError):
            get_unknown_service_environment('OpenStack M2')

    def test_get_tenant_unknown_service_not_configured(self):
        with self.assertRaises(UnknownServiceEnvironmentNotConfiguredError):
            get_unknown_service_environment('OpenStack M2')

    @mock.patch('ralph_scrooge.plugins.collect.tenant.api_scrooge.get_openstack_tenants')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect.tenant.update_tenant')
    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS)
    def test_tenant_plugin(
        self,
        update_tenant_mock,
        get_openstack_tenants_mock
    ):
        unknown_service_environment = ServiceEnvironmentFactory(
            service__ci_uid=UNKNOWN_SERVICE_ENVIRONMENT[0],
            environment__name=UNKNOWN_SERVICE_ENVIRONMENT[1],
        )
        update_tenant_mock.return_value = True
        tenants_list = [self._get_sample_tenant()] * 5
        get_openstack_tenants_mock.return_value = tenants_list
        result = tenant_plugin(self.today)
        self.assertEquals(
            result,
            (True, 'Tenants: 5 new, 0 updated, 5 total')
        )
        self.assertEquals(update_tenant_mock.call_count, 5)
        update_tenant_mock.assert_any_call(
            tenants_list[0],
            self.today,
            unknown_service_environment,
        )

    @mock.patch('ralph_scrooge.plugins.collect.tenant.get_unknown_service_environment')  # noqa
    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS)
    def test_tenant_plugin_unknown_service_not_configured(
        self,
        get_unknown_service_environment_mock
    ):
        get_unknown_service_environment_mock.side_effect = (
            UnknownServiceEnvironmentNotConfiguredError()
        )
        result = tenant_plugin(self.today)
        self.assertEquals(
            result,
            (
                False,
                'Unknown service environment not configured for {}'.format(
                    OPENSTACK_TENANTS_MODELS[0]
                )
            )
        )
