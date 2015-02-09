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
from ralph_scrooge.plugins.collect.vip import (
    get_vip_model,
    get_unknown_service_environment,
    save_vip_info,
    save_daily_vip_info,
    vip as vip_plugin,
    UnknownServiceEnvironmentNotConfiguredError,
)
from ralph_scrooge.tests.utils.factory import (
    AssetInfoFactory,
    PricingObjectFactory,
    PricingObjectModelFactory,
    ServiceEnvironmentFactory,
    VIPInfoFactory,
)

VIP_TYPES = ['VIP1']
UNKNOWN_SERVICE_ENVIRONMENT = ('vip-1', 'env1')
TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS = dict(
    UNKNOWN_SERVICES_ENVIRONMENTS={
        'vip': {
            VIP_TYPES[0]: UNKNOWN_SERVICE_ENVIRONMENT,
        }
    },
    VIP_TYPES=VIP_TYPES,
)


class TestVIPCollectPlugin(TestCase):
    def setUp(self):
        self.service_environment = ServiceEnvironmentFactory()
        self.unknown_service_environment = ServiceEnvironmentFactory(
            service__name=UNKNOWN_SERVICE_ENVIRONMENT[0],
            environment__name=UNKNOWN_SERVICE_ENVIRONMENT[0],
        )
        self.asset_info = AssetInfoFactory()
        self.today = datetime.date(2014, 7, 1)
        self.model = PricingObjectModelFactory(
            type_id=PRICING_OBJECT_TYPES.VIP,
            name=VIP_TYPES[0],
        )
        self.load_balancer = AssetInfoFactory()

    def _get_sample_vip(self):
        return {
            'vip_id': 1,
            'service_id': self.service_environment.service.ci_id,
            'environment_id': self.service_environment.environment.ci_id,
            'name': 'VIP1',
            'port': 80,
            'ip_address': '127.0.0.1',
            'type_id': self.model.model_id,
            'type': self.model.name,
            'device_id': self.load_balancer.device_id
        }

    def _compare_vips(self, sample_vip, vip_info, check_load_balancer=True):
        self.assertEquals(
            vip_info.vip_id,
            sample_vip['vip_id']
        )
        self.assertEquals(vip_info.name, sample_vip['name'])
        self.assertEquals(vip_info.port, sample_vip['port'])
        self.assertEquals(
            vip_info.ip_info.name,
            sample_vip['ip_address']
        )
        self.assertEquals(
            vip_info.model.model_id,
            sample_vip['type_id']
        )
        self.assertEquals(vip_info.model.name, sample_vip['type'])
        self.assertEquals(vip_info.type_id, PRICING_OBJECT_TYPES.VIP)
        if check_load_balancer:
            self.assertEquals(vip_info.load_balancer, self.load_balancer)

    def test_get_vip_model(self):
        sample_vip = self._get_sample_vip()
        model = get_vip_model(sample_vip)
        self.assertEquals(model, self.model)

    def test_save_vip_info(self):
        sample_vip = self._get_sample_vip()
        created, vip_info = save_vip_info(
            sample_vip,
            self.unknown_service_environment
        )
        self.assertTrue(created)
        self._compare_vips(sample_vip, vip_info)
        self.assertEquals(
            vip_info.service_environment,
            self.service_environment
        )
        self.assertEquals(
            vip_info.ip_info.service_environment,
            self.service_environment
        )

    def test_save_vip_info_ip_exists(self):
        sample_vip = self._get_sample_vip()
        ip_info = PricingObjectFactory(
            type_id=PRICING_OBJECT_TYPES.IP_ADDRESS,
            name=sample_vip['ip_address']
        )
        created, vip_info = save_vip_info(
            sample_vip,
            self.unknown_service_environment
        )
        self.assertTrue(created)
        self._compare_vips(sample_vip, vip_info)
        self.assertEquals(ip_info.id, vip_info.ip_info.id)

    def test_save_vip_info_vip_exists(self):
        sample_vip = self._get_sample_vip()
        vip_info = VIPInfoFactory(vip_id=sample_vip['vip_id'])
        created, plugin_vip_info = save_vip_info(
            sample_vip,
            self.unknown_service_environment
        )
        self.assertFalse(created)
        self._compare_vips(sample_vip, plugin_vip_info)
        self.assertEquals(vip_info.id, plugin_vip_info.id)

    def test_save_vip_info_without_load_balancer(self):
        sample_vip = self._get_sample_vip()
        sample_vip['device_id'] = None
        created, vip_info = save_vip_info(
            sample_vip,
            self.unknown_service_environment
        )
        self.assertTrue(created)
        self._compare_vips(sample_vip, vip_info, check_load_balancer=False)
        self.assertIsNone(vip_info.load_balancer)

    def test_save_vip_info_invalid_service_environment(self):
        service_environment = ServiceEnvironmentFactory.build()
        sample_vip = self._get_sample_vip()
        sample_vip['service_id'] = service_environment.service.ci_id
        sample_vip['environment_id'] = service_environment.environment.ci_id
        created, vip_info = save_vip_info(
            sample_vip,
            self.unknown_service_environment
        )
        self.assertTrue(created)
        self._compare_vips(sample_vip, vip_info)
        self.assertEquals(
            vip_info.service_environment,
            self.unknown_service_environment
        )
        self.assertEquals(
            vip_info.ip_info.service_environment,
            self.unknown_service_environment
        )

    def test_save_daily_vip_info(self):
        vip_info = VIPInfoFactory()
        sample_vip = self._get_sample_vip()
        result = save_daily_vip_info(
            sample_vip,
            vip_info,
            self.today
        )
        self.assertEquals(result.vip_info, vip_info)
        self.assertEquals(result.pricing_object, vip_info)
        self.assertEquals(result.date, self.today)
        self.assertEquals(
            result.service_environment,
            vip_info.service_environment
        )

    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS)
    def test_get_vip_unknown_service_environment(self):
        service_environment = ServiceEnvironmentFactory(
            service__ci_uid=UNKNOWN_SERVICE_ENVIRONMENT[0],
            environment__name=UNKNOWN_SERVICE_ENVIRONMENT[1],
        )
        self.assertEquals(
            service_environment,
            get_unknown_service_environment(VIP_TYPES[0])
        )

    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS)
    def test_get_vip_unknown_service_invalid_config(self):
        ServiceEnvironmentFactory()
        with self.assertRaises(UnknownServiceEnvironmentNotConfiguredError):
            get_unknown_service_environment('VIP2')

    def test_get_vip_unknown_service_not_configured(self):
        with self.assertRaises(UnknownServiceEnvironmentNotConfiguredError):
            get_unknown_service_environment('VIP2')

    @mock.patch('ralph_scrooge.plugins.collect.vip.api_scrooge.get_vips')
    @mock.patch('ralph_scrooge.plugins.collect.vip.update_vip')
    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS)
    def test_vip_plugin(
        self,
        update_vip_mock,
        get_vips_mock
    ):
        unknown_service_environment = ServiceEnvironmentFactory(
            service__ci_uid=UNKNOWN_SERVICE_ENVIRONMENT[0],
            environment__name=UNKNOWN_SERVICE_ENVIRONMENT[1],
        )
        update_vip_mock.return_value = True
        vips_list = [self._get_sample_vip()] * 5
        get_vips_mock.return_value = vips_list
        result = vip_plugin(self.today)
        self.assertEquals(
            result,
            (True, 'VIPs: 5 new, 0 updated, 5 total')
        )
        self.assertEquals(update_vip_mock.call_count, 5)
        update_vip_mock.assert_any_call(
            vips_list[0],
            self.today,
            unknown_service_environment,
        )

    @mock.patch('ralph_scrooge.plugins.collect.vip.get_unknown_service_environment')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect.vip.logger')
    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS)
    def test_vip_plugin_unknown_service_not_configured(
        self,
        logger_mock,
        get_unknown_service_environment_mock
    ):
        get_unknown_service_environment_mock.side_effect = (
            UnknownServiceEnvironmentNotConfiguredError()
        )
        result = vip_plugin(self.today)
        self.assertTrue(logger_mock.error.called)
        self.assertEquals(
            result,
            (True, 'VIPs: 0 new, 0 updated, 0 total')
        )
