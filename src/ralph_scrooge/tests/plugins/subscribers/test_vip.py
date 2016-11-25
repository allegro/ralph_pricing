# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from copy import deepcopy

from django.forms import ValidationError
from django.test.utils import override_settings

from ralph_scrooge.models import PRICING_OBJECT_TYPES
from ralph_scrooge.plugins.subscribers.vip import (
    validate_vip_event_data,
    normalize_lb_type,
    get_vip_model,
    get_service_env,
    save_vip_info,
    save_daily_vip_info,
)
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import (
    AssetInfoFactory,
    IPInfoFactory,
    PricingObjectModelFactory,
    ServiceEnvironmentFactory,
    VIPInfoFactory,
)

VIP_TYPES = ['HA Proxy', 'F5']
UNKNOWN_SERVICE_ENVIRONMENT = ('xx-456', 'test')
TEST_SETTINGS_UNKNOWN_SERVICE_ENVIRONMENTS = dict(
    UNKNOWN_SERVICES_ENVIRONMENTS={
        'vip': {
            VIP_TYPES[0]: UNKNOWN_SERVICE_ENVIRONMENT,
        }
    },
    VIP_TYPES=VIP_TYPES,
)

EVENT_DATA = {
    "non_http": False,
    "load_balancer": "test-lb.local",
    "id": 111,
    "service": {
        "uid": "xx-123",
        "name": "test service"
    },
    "load_balancer_type": "HAPROXY",
    "port": 80,
    "name": "ralph-test.local_8000",
    "environment": "test",
    "venture": None,
    "protocol": "TCP",
    "partition": "default",
    "ip": "10.20.30.40"
}


class ValidateEventDataTestCase(ScroogeTestCase):

    def setUp(self):
        self.event_data = deepcopy(EVENT_DATA)

    def test_missing_id(self):
        self.event_data['id'] = None
        errors = validate_vip_event_data(self.event_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('missing id', errors)

    def test_missing_name(self):
        self.event_data['name'] = None
        errors = validate_vip_event_data(self.event_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('missing name', errors)

    def test_missing_ip_address(self):
        self.event_data['ip'] = None
        errors = validate_vip_event_data(self.event_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('missing IP address', errors)

    def test_invalid_port(self):
        self.event_data['port'] = -1
        errors = validate_vip_event_data(self.event_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('invalid port "-1"', errors)

        self.event_data['port'] = 66666
        errors = validate_vip_event_data(self.event_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('invalid port "66666"', errors)

        self.event_data['port'] = "invalid"
        errors = validate_vip_event_data(self.event_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('invalid port "invalid"', errors)

        self.event_data['port'] = None
        errors = validate_vip_event_data(self.event_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('invalid port "None"', errors)

    def test_missing_protocol(self):
        self.event_data['protocol'] = None
        errors = validate_vip_event_data(self.event_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('missing protocol', errors)

    def test_missing_service_uid(self):
        self.event_data['service']['uid'] = None
        errors = validate_vip_event_data(self.event_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('missing service UID', errors)

        self.event_data['service'] = None
        errors = validate_vip_event_data(self.event_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('missing service UID', errors)

    def test_missing_environment(self):
        self.event_data['environment'] = None
        errors = validate_vip_event_data(self.event_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('missing environment', errors)

    def test_missing_load_balancer_type(self):
        self.event_data['load_balancer_type'] = None
        errors = validate_vip_event_data(self.event_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('missing load_balancer_type', errors)

    def test_if_errors_aggregate(self):
        self.event_data['service'] = None
        self.event_data['environment'] = None
        errors = validate_vip_event_data(self.event_data)
        self.assertEqual(len(errors), 2)
        self.assertIn('missing service UID', errors)
        self.assertIn('missing environment', errors)


class TestVIPSubscribersPlugin(ScroogeTestCase):

    # TODO(xor-xor): Set check_load_balancer=True as a default value when it
    # will be clear what to do with VIPInfo.load_balancer field.
    def _compare_vips(self, vip_info, event_data, check_load_balancer=False):
        self.assertEquals(vip_info.external_id, event_data['id'])
        self.assertEquals(vip_info.name, event_data['name'])
        self.assertEquals(vip_info.port, event_data['port'])
        self.assertEquals(vip_info.ip_info.name, event_data['ip'])
        self.assertEquals(
            vip_info.model.name,
            normalize_lb_type(event_data['load_balancer_type']),
        )
        self.assertEquals(vip_info.type_id, PRICING_OBJECT_TYPES.VIP)
        if check_load_balancer:
            self.assertEquals(vip_info.load_balancer, self.load_balancer)

    def setUp(self):
        self.today = datetime.date.today()
        self.event_data = deepcopy(EVENT_DATA)
        self.model = PricingObjectModelFactory(
            name='HA Proxy',
            type_id=PRICING_OBJECT_TYPES.VIP,
        )
        self.service_env = ServiceEnvironmentFactory(
            service__ci_uid=self.event_data['service']['uid'],
            environment__name=self.event_data['environment'],
        )
        self.unknown_service_env = ServiceEnvironmentFactory(
            service__ci_uid=UNKNOWN_SERVICE_ENVIRONMENT[0],
            environment__name=UNKNOWN_SERVICE_ENVIRONMENT[1],
        )
        self.load_balancer = AssetInfoFactory()

    def test_normalize_lb_type(self):
        lb_type = normalize_lb_type('HAPROXY')
        self.assertEqual(lb_type, 'HA Proxy')
        lb_type = normalize_lb_type('F5')
        self.assertEqual(lb_type, 'F5')

    def test_get_vip_model(self):
        model = get_vip_model(self.event_data)
        self.assertEquals(model, self.model)

    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICE_ENVIRONMENTS)
    def test_get_known_service_env(self):
        service_env, service_env_found = get_service_env(self.event_data)
        self.assertEqual(service_env, self.service_env)
        self.assertTrue(service_env_found)

    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICE_ENVIRONMENTS)
    def test_get_unknown_service_env(self):
        self.event_data['service']['uid'] = 'non-existing uid'
        service_env, service_env_found = get_service_env(self.event_data)
        self.assertEqual(service_env, self.unknown_service_env)
        self.assertFalse(service_env_found)

    def test_save_vip_info(self):
        vip_info = save_vip_info(self.event_data)
        self.assertEquals(
            vip_info.service_environment,
            self.service_env,
        )
        self.assertEquals(
            vip_info.ip_info.service_environment,
            self.service_env,
        )
        self._compare_vips(vip_info, self.event_data)

    def test_ip_info_address_validation(self):
        with self.assertRaises(
            ValidationError, msg='Is not a valid IP address'
        ):
            IPInfoFactory(
                name='not valid ip',
                type_id=PRICING_OBJECT_TYPES.IP_ADDRESS,
            )

    def test_save_vip_info_ip_exists(self):
        ip_info = IPInfoFactory(
            name=self.event_data['ip'],
            type_id=PRICING_OBJECT_TYPES.IP_ADDRESS,
        )
        vip_info = save_vip_info(self.event_data)
        self._compare_vips(vip_info, self.event_data)
        self.assertEquals(ip_info.id, vip_info.ip_info.id)

    def test_save_vip_info_vip_exists(self):
        existing_vip_info = VIPInfoFactory(external_id=self.event_data['id'])
        vip_info = save_vip_info(self.event_data)
        self._compare_vips(vip_info, self.event_data)
        self.assertEquals(existing_vip_info.id, vip_info.id)

    @override_settings(**TEST_SETTINGS_UNKNOWN_SERVICE_ENVIRONMENTS)
    def test_save_vip_info_invalid_service_environment(self):
        service_env = ServiceEnvironmentFactory.build()
        self.event_data['service']['uid'] = service_env.service.ci_uid
        self.event_data['environment'] = service_env.environment.name
        vip_info = save_vip_info(self.event_data)
        self._compare_vips(vip_info, self.event_data)
        self.assertEquals(
            vip_info.service_environment,
            self.unknown_service_env
        )
        self.assertEquals(
            vip_info.ip_info.service_environment,
            self.unknown_service_env
        )

    def test_save_daily_vip_info(self):
        vip_info = VIPInfoFactory()
        daily_vip_info = save_daily_vip_info(vip_info, self.today)
        self.assertEquals(daily_vip_info.vip_info, vip_info)
        self.assertEquals(daily_vip_info.pricing_object, vip_info)
        self.assertEquals(daily_vip_info.date, self.today)
        self.assertEquals(
            daily_vip_info.service_environment,
            vip_info.service_environment
        )
