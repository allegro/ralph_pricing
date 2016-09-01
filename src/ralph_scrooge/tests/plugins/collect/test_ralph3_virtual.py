# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from mock import patch

from django.db.models import Sum
from django.test import TestCase
from django.test.utils import override_settings

from ralph_scrooge import models
from ralph_scrooge.plugins.collect import ralph3_virtual as virtual
from ralph_scrooge.tests.utils.factory import (
    AssetInfoFactory,
    DailyVirtualInfoFactory,
    ServiceEnvironmentFactory,
    UsageTypeFactory,
    VirtualInfoFactory
)


VIRTUAL_GROUP_NAME = 'Xen'
UNKNOWN_SERVICE_ENVIRONMENT = ('os-1', 'env1')
TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS = dict(
    UNKNOWN_SERVICES_ENVIRONMENTS={
        'ralph3_virtual': {
            VIRTUAL_GROUP_NAME: UNKNOWN_SERVICE_ENVIRONMENT
        }
    },
)


@override_settings(
    VIRTUAL_SERVICES={'Xen': ['example_service']},
    **TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS
)
class TestVirtualPlugin(TestCase):
    usage_names = {
        'virtual_cores': 'Virtual CPU cores',
        'virtual_disk': 'Virtual disk MB',
        'virtual_memory': 'Virtual memory MB',
    }

    def setUp(self):
        self.today = date(2014, 7, 1)
        self.service_env = ServiceEnvironmentFactory(
            service__ci_uid='sc-12',
            environment__name='prod',
        )
        self.unknown_service_environment = ServiceEnvironmentFactory(
            service__ci_uid=UNKNOWN_SERVICE_ENVIRONMENT[0],
            environment__name=UNKNOWN_SERVICE_ENVIRONMENT[1],
        )
        self.hypervisor = AssetInfoFactory(ralph3_asset_id=1234)
        self.daily_hypervisor = self.hypervisor.get_daily_pricing_object(
            self.today
        )
        self.data = dict(
            id=1,
            hostname='sample',
            __str__='virtual server: sample',
            service_env={
                'service_uid': 'sc-12',
                'environment': 'prod',
            },
            hypervisor={
                'url': 'http://ralph.local/api/data-center-assets/1234/'
            },
            processors=[
                {'cores': 2}, {'cores': 4},
            ],
            memory=[
                {'size': 2048}, {'size': 4096},
            ],
            disk=[
                {'size': 2048}, {'size': 8192},
            ],
            type={
                'id': 10,
                'name': VIRTUAL_GROUP_NAME,
            }
        )

    def test_get_or_create_usages(self):
        virtual.get_or_create_usages(VIRTUAL_GROUP_NAME)
        self.assertEqual(models.UsageType.objects.all().count(), 3)

    def _compare_daily_virtual_info(
        self,
        daily_virtual_info,
        data,
        service_environment,
        group_name,
    ):
        virtual_info = daily_virtual_info.virtual_info
        self.assertEqual(
            daily_virtual_info.service_environment,
            service_environment
        )
        self.assertEqual(virtual_info.service_environment, service_environment)
        self.assertEqual(virtual_info.name, data['hostname'])
        self.assertEqual(virtual_info.ralph3_id, data['id'])
        self.assertEqual(
            virtual_info.type_id,
            models.PRICING_OBJECT_TYPES.VIRTUAL
        )
        self.assertEqual(virtual_info.model.name, data['type']['name'])
        self.assertEqual(virtual_info.model.model_id, data['type']['id'])
        self.assertEqual(
            virtual_info.model.type_id,
            models.PRICING_OBJECT_TYPES.VIRTUAL
        )

    def test_update_virtual_info(self):
        daily_virtual_info, _ = virtual.update_virtual_info(
            VIRTUAL_GROUP_NAME,
            self.data,
            self.today,
            self.service_env,
        )
        self._compare_daily_virtual_info(
            daily_virtual_info,
            self.data,
            self.service_env,
            VIRTUAL_GROUP_NAME,
        )
        self.assertEqual(daily_virtual_info.hypervisor, self.daily_hypervisor)

    def test_update_virtual_virtual_info_without_hypervisor(self):
        self.data['hypervisor'] = None
        daily_virtual_info, _ = virtual.update_virtual_info(
            VIRTUAL_GROUP_NAME,
            self.data,
            self.today,
            self.service_env,
        )
        self._compare_daily_virtual_info(
            daily_virtual_info,
            self.data,
            self.service_env,
            VIRTUAL_GROUP_NAME,
        )
        self.assertIsNone(daily_virtual_info.hypervisor)

    def test_update_virtual_usage(self):
        service_env = ServiceEnvironmentFactory.create()
        daily_virtual_info = DailyVirtualInfoFactory()
        usage_type = UsageTypeFactory.create()
        daily_usage = virtual.update_virtual_usage(
            daily_virtual_info,
            service_env,
            usage_type,
            self.today,
            100,
        )
        self.assertEqual(models.VirtualInfo.objects.all().count(), 1)
        self.assertEqual(daily_usage.service_environment, service_env)
        self.assertEqual(daily_usage.type, usage_type)
        self.assertEqual(daily_usage.date, self.today)
        self.assertEqual(daily_usage.value, 100)
        self.assertEqual(daily_usage.daily_pricing_object, daily_virtual_info)

    def test_update_virtual_server(self):
        usages = virtual.get_or_create_usages(VIRTUAL_GROUP_NAME)
        created = virtual.update_virtual_server(
            VIRTUAL_GROUP_NAME, self.data, usages, self.today,
            self.unknown_service_environment
        )
        self.assertTrue(created)
        vi = models.VirtualInfo.objects.get(ralph3_id=1)
        dvi = vi.get_daily_pricing_object(self.today)
        self._compare_daily_virtual_info(
            dvi, self.data, self.service_env, VIRTUAL_GROUP_NAME,
        )
        for usage, expected_value in [
            ('virtual_cores', 6),
            ('virtual_memory', 6144),
            ('virtual_disk', 10240),
        ]:
            ut = usages[usage][0]
            self.assertEqual(
                ut.dailyusage_set.filter(
                    daily_pricing_object=dvi, date=self.today
                ).aggregate(s=Sum('value'))['s'],
                expected_value
            )

    def test_update_existing_virtual_server(self):
        VirtualInfoFactory(ralph3_id=1)
        usages = virtual.get_or_create_usages(VIRTUAL_GROUP_NAME)
        created = virtual.update_virtual_server(
            VIRTUAL_GROUP_NAME, self.data, usages, self.today,
            self.unknown_service_environment
        )
        self.assertFalse(created)

    def test_update_virtual_server_with_unknown_service_env(self):
        usages = virtual.get_or_create_usages(VIRTUAL_GROUP_NAME)
        self.data['service_env']['environment'] = 'fake'
        virtual.update_virtual_server(
            VIRTUAL_GROUP_NAME, self.data, usages, self.today,
            self.unknown_service_environment
        )
        vi = models.VirtualInfo.objects.get(ralph3_id=1)
        self.assertEqual(
            vi.service_environment, self.unknown_service_environment
        )

    @patch('ralph_scrooge.plugins.collect.ralph3_virtual.get_from_ralph')
    def test_ralph3_virtual_plugin_new_virtual_server(
        self, get_from_ralph_mock
    ):
        get_from_ralph_mock.return_value = [self.data]
        self.assertEqual(
            virtual.ralph3_virtual(today=self.today),
            (True, 'Virtual: 1 new, 0 updated, 0 errors, 1 total'),
        )

    @patch('ralph_scrooge.plugins.collect.ralph3_virtual.get_from_ralph')
    def test_ralph3_virtual_plugin_existing_virtual_server(
        self, get_from_ralph_mock
    ):
        VirtualInfoFactory(ralph3_id=1)
        get_from_ralph_mock.return_value = [self.data]
        self.assertEqual(
            virtual.ralph3_virtual(today=self.today),
            (True, 'Virtual: 0 new, 1 updated, 0 errors, 1 total'),
        )

    @override_settings(UNKNOWN_SERVICES_ENVIRONMENTS={})
    @patch('ralph_scrooge.plugins.collect.ralph3_virtual.logger')
    def test_ralph3_virtual_plugin_unknown_service_env_not_configured(
        self, logger_mock
    ):
        self.assertEqual(
            virtual.ralph3_virtual(today=self.today),
            (True, 'Virtual: 0 new, 0 updated, 0 errors, 0 total'),
        )
        self.assertTrue(logger_mock.error.called)
        logger_mock.error.assert_called_with(
            'Unknown service-env not configured for "Xen"'
        )
