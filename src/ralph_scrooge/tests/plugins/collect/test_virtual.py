# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from mock import patch, MagicMock

from django.test import TestCase
from django.test.utils import override_settings

from ralph.util import api_scrooge
from ralph_scrooge import models
from ralph_scrooge.plugins.collect import virtual
from ralph_scrooge.tests.utils.factory import (
    AssetInfoFactory,
    DailyAssetInfoFactory,
    DailyVirtualInfoFactory,
    ServiceEnvironmentFactory,
    UsageTypeFactory,
)
from ralph_scrooge.utils.common import AttributeDict


class TestVirtualPlugin(TestCase):
    usage_names = {
        'virtual_cores': 'Virtual CPU cores',
        'virtual_disk': 'Virtual disk MB',
        'virtual_memory': 'Virtual memory MB',
    }

    def setUp(self):
        self.today = date(2014, 7, 1)
        self.service_environment = ServiceEnvironmentFactory()

    def test_get_or_create_usages(self):
        virtual.get_or_create_usages(self.usage_names)
        self.assertEqual(models.UsageType.objects.all().count(), 3)

    def test_update_when_device_id_is_none(self):
        self.assertRaises(
            virtual.DeviceIdCannotBeNoneError,
            virtual.update,
            group_name='sample',
            data=AttributeDict(device_id=None),
            usages={},
            date=self.today,
        )

    def test_update_when_service_id_is_none(self):
        self.assertRaises(
            virtual.ServiceUidCannotBeNoneError,
            virtual.update,
            group_name='sample',
            data=AttributeDict(device_id=1, service_id=None),
            usages={},
            date=self.today,
        )

    def test_update_when_environment_is_none(self):
        self.assertRaises(
            virtual.EnvironmentCannotBeNoneError,
            virtual.update,
            group_name='sample',
            data=AttributeDict(
                device_id=1,
                service_id=1,
                environment_id=None,
            ),
            usages={},
            date=self.today,
        )

    @patch.object(virtual, 'update_virtual_info', MagicMock())
    @patch.object(virtual, 'update_virtual_usage', MagicMock())
    def test_update(self):
        service_environment = ServiceEnvironmentFactory.create()
        virtual.update(
            'virtual_group',
            AttributeDict(
                device_id=1,
                service_id=service_environment.service.ci_id,
                environment_id=service_environment.environment.ci_id,
                model_id=1,
                model_name='sample model',
            ),
            {'key': 'value', 'key2': 'value2'},
            self.today,
        )
        self.assertEqual(virtual.update_virtual_usage.call_count, 2)
        self.assertEqual(virtual.update_virtual_info.call_count, 1)

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
        self.assertEqual(virtual_info.name, data['name'])
        self.assertEqual(virtual_info.device_id, data['device_id'])
        self.assertEqual(
            virtual_info.type_id,
            models.PRICING_OBJECT_TYPES.VIRTUAL
        )
        self.assertEqual(virtual_info.model.name, data['model_name'])
        self.assertEqual(virtual_info.model.manufacturer, group_name)
        self.assertEqual(virtual_info.model.model_id, data['model_id'])
        self.assertEqual(
            virtual_info.model.type_id,
            models.PRICING_OBJECT_TYPES.VIRTUAL
        )

    def test_update_virtual_virtual_info(self):
        service_env = ServiceEnvironmentFactory.create()
        data = AttributeDict(
            device_id=1,
            name='sample',
            service_id=service_env.service.ci_id,
            environment_id=service_env.environment.ci_id,
            model_id=1,
            model_name='sample model',
        )
        daily_virtual_info = virtual.update_virtual_info(
            'virtual_group',
            data,
            self.today,
            service_env,
        )
        self._compare_daily_virtual_info(
            daily_virtual_info,
            data,
            service_env,
            'virtual_group',
        )
        self.assertIsNone(daily_virtual_info.hypervisor)

    def test_update_virtual_virtual_info_with_hypervisor(self):
        service_env = ServiceEnvironmentFactory.create()
        hypervisor = DailyAssetInfoFactory(date=self.today)
        data = AttributeDict(
            device_id=1,
            name='sample',
            service_id=service_env.service.ci_id,
            environment_id=service_env.environment.ci_id,
            model_id=1,
            hypervisor_id=hypervisor.asset_info.device_id,
            model_name='sample model',
        )
        daily_virtual_info = virtual.update_virtual_info(
            'virtual_group',
            data,
            self.today,
            service_env,
        )
        self._compare_daily_virtual_info(
            daily_virtual_info,
            data,
            service_env,
            'virtual_group',
        )
        self.assertEqual(
            hypervisor.asset_info.device_id,
            daily_virtual_info.hypervisor.asset_info.device_id
        )

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

    @override_settings(
        VIRTUAL_SERVICES={'example_group': ['example_service']},
    )
    @patch.object(
        api_scrooge,
        'get_virtual_usages',
        lambda *args, **kwargs: [AttributeDict(device_id=None)],
    )
    def test_virtual_when_asset_info_is_none(self):
        self.assertEqual(
            virtual.virtual(today=self.today),
            (True, 'Virtual: None new, 0 updated, 1 total'),
        )

    @override_settings(
        VIRTUAL_SERVICES={'example_group': ['example_service']},
    )
    @patch.object(
        api_scrooge,
        'get_virtual_usages',
        lambda *args, **kwargs: [AttributeDict(
            device_id=1,
            service_id=None
        )],
    )
    def test_virtual_when_service_id_is_none(self):
        self.assertEqual(
            virtual.virtual(today=self.today),
            (True, 'Virtual: None new, 0 updated, 1 total'),
        )

    @override_settings(
        VIRTUAL_SERVICES={'example_group': ['example_service']},
    )
    @patch.object(
        api_scrooge,
        'get_virtual_usages',
        lambda *args, **kwargs: [AttributeDict(
            device_id=1,
            service_id=1,
            environment_id=None,
        )],
    )
    def test_virtual_when_environment_is_none(self):
        self.assertEqual(
            virtual.virtual(today=self.today),
            (True, 'Virtual: None new, 0 updated, 1 total'),
        )

    @override_settings(
        VIRTUAL_SERVICES={'example_group': ['example_service']},
    )
    @patch.object(
        api_scrooge,
        'get_virtual_usages',
        lambda *args, **kwargs: [AttributeDict(
            device_id=1,
            service_id=1,
            environment_id=1,
        )],
    )
    def test_virtual_when_service_environment_does_not_exist(self):
        self.assertEqual(
            virtual.virtual(today=self.today),
            (True, 'Virtual: None new, 0 updated, 1 total'),
        )

    @override_settings(
        VIRTUAL_SERVICES={'example_group': ['example_service']},
    )
    @patch.object(
        api_scrooge,
        'get_virtual_usages',
        lambda *args, **kwargs: [AttributeDict(
            device_id=1,
            service_id=1,
            environment_id=1,
            hypervisor_id=1,
        )],
    )
    def test_virtual_when_asset_info_does_not_exist(self):
        self.assertEqual(
            virtual.virtual(today=self.today),
            (True, 'Virtual: None new, 0 updated, 1 total'),
        )

    @override_settings(
        VIRTUAL_SERVICES={'example_group': ['example_service']},
    )
    @patch.object(
        api_scrooge,
        'get_virtual_usages',
        lambda *args, **kwargs: [AttributeDict(
            device_id=1,
            service_id=1,
            environment_id=1,
            hypervisor_id=1,
        )],
    )
    def test_virtual_when_daily_asset_info_does_not_exist(self):
        AssetInfoFactory.create(device_id=1)
        self.assertEqual(
            virtual.virtual(today=self.today),
            (True, 'Virtual: None new, 0 updated, 1 total'),
        )

    @override_settings(
        VIRTUAL_SERVICES={'example_group': ['example_service']},
    )
    @patch.object(
        api_scrooge,
        'get_virtual_usages',
        lambda *args, **kwargs: [AttributeDict(
            device_id=1,
            service_id=1,
            environment_id=1,
            hypervisor_id=1,
            name='example_name',
            virtual_disk=100,
            virtual_memory=100,
            virtual_cores=100,
            model_id=1,
            model_name='sample model',
        )],
    )
    @patch.object(virtual, 'ServiceEnvironment', MagicMock())
    def test_virtual(self):
        service_environment = ServiceEnvironmentFactory.create()
        asset_info = AssetInfoFactory.create(device_id=1)
        DailyAssetInfoFactory.create(asset_info=asset_info, date=self.today)
        virtual.ServiceEnvironment.objects.get = (
            lambda *args, **kwargs: service_environment
        )
        self.assertEqual(
            virtual.virtual(today=self.today),
            (True, 'Virtual: None new, 1 updated, 1 total'),
        )
