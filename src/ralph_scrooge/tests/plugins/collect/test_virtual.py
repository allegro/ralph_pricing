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
    ServiceEnvironmentFactory,
    UsageTypeFactory,
    VirtualInfoFactory,
)
from ralph_scrooge.utils import AttributeDict


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
            data=AttributeDict(device_id=None),
            usages={},
            date=self.today,
        )

    def test_update_when_service_id_is_none(self):
        self.assertRaises(
            virtual.ServiceUidCannotBeNoneError,
            virtual.update,
            data=AttributeDict(device_id=1, service_id=None),
            usages={},
            date=self.today,
        )

    def test_update_when_environment_is_none(self):
        self.assertRaises(
            virtual.EnvironmentCannotBeNoneError,
            virtual.update,
            data=AttributeDict(
                device_id=1,
                service_id=1,
                environment_id=None,
            ),
            usages={},
            date=self.today,
        )

    @patch.object(virtual, 'AssetInfo', MagicMock())
    @patch.object(virtual, 'DailyAssetInfo', MagicMock())
    def test_update_when_hypervisor_id_is_none(self):
        service_environment = ServiceEnvironmentFactory.create()
        virtual.update(
            AttributeDict(
                device_id=1,
                service_id=service_environment.service.ci_id,
                environment_id=service_environment.environment.ci_id,
                hypervisor_id=1,
            ),
            {},
            self.today,
        )
        virtual.AssetInfo.objects.get.assert_called_once_with(device_id=1)

    @patch.object(virtual, 'update_virtual_usage', MagicMock())
    def test_update(self):
        service_environment = ServiceEnvironmentFactory.create()
        virtual.update(
            AttributeDict(
                device_id=1,
                service_id=service_environment.service.ci_id,
                environment_id=service_environment.environment.ci_id,
            ),
            {'key': 'value'},
            self.today,
        )
        self.assertEqual(virtual.update_virtual_usage.call_count, 1)

    def test_update_virtual_usage_when_no_virtual_info(self):
        virtual.update_virtual_usage(
            DailyAssetInfoFactory.create(),
            ServiceEnvironmentFactory.create(),
            UsageTypeFactory.create(),
            {'device_id': 1, 'name': 'example_name'},
            self.today,
            100,
        )
        self.assertEqual(models.VirtualInfo.objects.all().count(), 1)
        self.assertEqual(models.DailyVirtualInfo.objects.all().count(), 1)
        self.assertEqual(models.DailyUsage.objects.all().count(), 1)

    def test_update_virtual_usage(self):
        virtual.update_virtual_usage(
            DailyAssetInfoFactory.create(),
            ServiceEnvironmentFactory.create(),
            UsageTypeFactory.create(),
            {
                'device_id': VirtualInfoFactory.create().device_id,
                'name': 'example_name',
            },
            self.today,
            100,
        )
        self.assertEqual(models.VirtualInfo.objects.all().count(), 1)

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
    @patch.object(virtual, 'ServiceEnvironment', MagicMock())
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
    @patch.object(virtual, 'ServiceEnvironment', MagicMock())
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
