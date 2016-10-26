# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.test import TransactionTestCase
from django.test.utils import override_settings

from ralph_scrooge.models import (
    AssetInfo,
    DailyAssetInfo,
    DailyPricingObject,
    DailyUsage,
    PricingObject,
    UsageType,
)
from ralph_scrooge.plugins.collect import ralph3_asset as asset
from ralph_scrooge.tests import ScroogeTestCaseMixin
from ralph_scrooge.tests.utils.factory import (
    AssetInfoFactory,
    DailyAssetInfoFactory,
    EnvironmentFactory,
    ServiceEnvironmentFactory,
    ServiceFactory,
    UsageTypeFactory,
    WarehouseFactory,
)


UNKNOWN_SERVICE_ENVIRONMENT = ('os-1', 'env1')
TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS = dict(
    UNKNOWN_SERVICES_ENVIRONMENTS={
        'ralph3_asset': UNKNOWN_SERVICE_ENVIRONMENT
    },
)


@override_settings(**TEST_SETTINGS_UNKNOWN_SERVICES_ENVIRONMENTS)
class TestAssetPlugin(ScroogeTestCaseMixin, TransactionTestCase):
    def setUp(self):
        ServiceFactory.reset_sequence()
        EnvironmentFactory.reset_sequence()
        ServiceEnvironmentFactory.reset_sequence()
        self.service_environment = ServiceEnvironmentFactory()
        self.unknown_service_environment = ServiceEnvironmentFactory(
            service__ci_uid=UNKNOWN_SERVICE_ENVIRONMENT[0],
            environment__name=UNKNOWN_SERVICE_ENVIRONMENT[1],
        )
        self.date = datetime.date.today()
        self.warehouse = WarehouseFactory.create()
        self.value = 100
        self.data = {
            'id': 1,
            '__str__': 'data center asset: s12345.mydc.net (BC: Barcode / SN: SerialNumber)',  # noqa
            'sn': 'SerialNumber',
            'barcode': 'Barcode',
            'hostname': 'host1',
            'depreciation_rate': 25,
            'force_depreciation': False,
            'invoice_date': '2014-08-10',
            'depreciation_end_date': None,
            'status': 'in use',
            'price': 100,
            'service_env': {
                'service': 'Service-1',
                'environment': 'Environment1',
                'service_uid': 'uid-1',
            },
            'rack': {
                'server_room': {
                    'data_center': {'id': 1},
                },
            },
            'model': {
                'cores_count': 4,
                'power_consumption': 200,
                'height_of_device': 2,
            },
        }

    def test_get_usage(self):
        usage_type = asset.get_usage(
            'test_symbol',
            'test_name',
            True,
            False,
            True,
            'SU',
        )
        self.assertEqual(usage_type, UsageType.objects_admin.get())
        self.assertEqual(usage_type.symbol, 'test_symbol')
        self.assertEqual(usage_type.name, 'test_name')
        self.assertEqual(usage_type.by_warehouse, True)
        self.assertEqual(usage_type.by_cost, False)
        self.assertEqual(usage_type.average, True)
        self.assertEqual(usage_type.usage_type, 'SU')

    def test_get_asset_and_pricing_object_when_asset_info_not_exist(self):
        self.assertEqual(
            asset.get_asset_info(
                self.service_environment,
                self.warehouse,
                self.data,
            ),
            (
                AssetInfo.objects.all()[:1].get(),
                True,
            )
        )

    def test_get_asset_and_pricing_object_when_asset_info_exist(self):
        AssetInfoFactory(
            ralph3_asset_id=self.data['id'],
            warehouse=self.warehouse,
        )
        self.assertEqual(
            asset.get_asset_info(
                self.service_environment,
                self.warehouse,
                self.data,
            ),
            (
                AssetInfo.objects.all()[:1].get(),
                False,
            )
        )

    def test_get_asset_info_integrity_error(self):
        AssetInfoFactory(
            ralph3_asset_id=self.data['id'],
            warehouse=self.warehouse,
        )
        data = [self.data.copy(), self.data.copy()]
        data[1]['id'] = 2
        data[1]['barcode'] = 'Barcode2'

        for d in data:
            asset.get_asset_info(self.service_environment, self.warehouse, d)
        self.assertEqual(AssetInfo.objects.count(), 2)
        asset1 = AssetInfo.objects.get(ralph3_asset_id=1)
        asset2 = AssetInfo.objects.get(ralph3_asset_id=2)
        self.assertEqual(asset1.barcode, data[0]['barcode'])
        self.assertEqual(asset2.barcode, data[1]['barcode'])
        self.assertEqual(asset2.sn, data[1]['sn'])
        self.assertIsNone(asset1.sn)

    def test_get_daily_asset_info(self):
        self.assertEqual(
            asset.get_daily_asset_info(
                AssetInfoFactory.create(),
                self.date,
                self.data,
            ),
            DailyAssetInfo.objects.all()[:1].get()
        )

    def test_update_usage(self):
        asset.update_usage(
            DailyAssetInfoFactory(),
            self.warehouse,
            UsageTypeFactory(),
            self.value,
            self.date,
        )
        self.assertEqual(
            DailyUsage.objects.all().count(),
            1
        )

    def test_a_update_asset_when_service_does_not_exist(self):
        self.data['service_env']['service_uid'] = 'uid-xxx'
        self.usages = {
            'depreciation': UsageTypeFactory.create(),
            'assets_count': UsageTypeFactory.create(),
            'cores_count': UsageTypeFactory.create(),
            'power_consumption': UsageTypeFactory.create(),
            'collocation': UsageTypeFactory.create(),
        }
        asset.update_asset(
            self.data, self.date, self.usages, self.unknown_service_environment
        )
        asset_info = AssetInfo.objects.get()
        self.assertEqual(
            asset_info.service_environment, self.unknown_service_environment
        )

    def test_update_asset_when_warehouse_does_not_exist(self):
        self.data['rack']['server_room']['data_center'] = None
        self.usages = {
            'depreciation': UsageTypeFactory.create(),
            'assets_count': UsageTypeFactory.create(),
            'cores_count': UsageTypeFactory.create(),
            'power_consumption': UsageTypeFactory.create(),
            'collocation': UsageTypeFactory.create(),
        }
        asset.update_asset(
            self.data, self.date, self.usages, self.unknown_service_environment
        )
        asset_info = AssetInfo.objects.get()
        self.assertEqual(asset_info.warehouse_id, 1)  # from fixtures

    def test_update_asset_when_rack_empty(self):
        self.data['rack'] = None
        self.usages = {
            'depreciation': UsageTypeFactory.create(),
            'assets_count': UsageTypeFactory.create(),
            'cores_count': UsageTypeFactory.create(),
            'power_consumption': UsageTypeFactory.create(),
            'collocation': UsageTypeFactory.create(),
        }
        asset.update_asset(
            self.data, self.date, self.usages, self.unknown_service_environment
        )
        asset_info = AssetInfo.objects.get()
        self.assertEqual(asset_info.warehouse_id, 1)  # from fixtures

    def test_update_asset_when_environment_does_not_exist(self):
        self.data['service_env']['environment'] = 'Non-ExistentEnv'
        self.usages = {
            'depreciation': UsageTypeFactory.create(),
            'assets_count': UsageTypeFactory.create(),
            'cores_count': UsageTypeFactory.create(),
            'power_consumption': UsageTypeFactory.create(),
            'collocation': UsageTypeFactory.create(),
        }
        asset.update_asset(
            self.data, self.date, self.usages, self.unknown_service_environment
        )
        asset_info = AssetInfo.objects.get()
        self.assertEqual(
            asset_info.service_environment, self.unknown_service_environment
        )

    def test_update_asset(self):
        self.usages = {
            'depreciation': UsageTypeFactory.create(),
            'assets_count': UsageTypeFactory.create(),
            'cores_count': UsageTypeFactory.create(),
            'power_consumption': UsageTypeFactory.create(),
            'collocation': UsageTypeFactory.create(),
        }
        self.assertTrue(
            asset.update_asset(
                self.data, self.date, self.usages,
                self.unknown_service_environment
            )
        )
        self.assertEqual(
            DailyUsage.objects.all().count(),
            5,
        )
        self.assertEqual(
            AssetInfo.objects.all().count(),
            1,
        )
        self.assertEqual(
            DailyAssetInfo.objects.all().count(),
            1,
        )
        self.assertEqual(
            PricingObject.objects.all().count(),
            3,  # 2 dummy for service environment, 1 regular
        )
        self.assertEqual(
            DailyPricingObject.objects.all().count(),
            1,
        )

    @mock.patch('ralph_scrooge.plugins.collect.ralph3_asset.get_combined_data')
    def test_assets_when_new_pricing_object(self, get_combined_data_mock):

        def sample_get_combined_data(queries):
            return data

        data = [self.data]
        get_combined_data_mock.side_effect = sample_get_combined_data
        self.assertEqual(
            asset.ralph3_asset(today=self.date),
            (True, u'1 new assets, 0 updated, 1 total')
        )

    @mock.patch('ralph_scrooge.plugins.collect.ralph3_asset.get_combined_data')
    def test_assets_when_update_pricing_object(self, get_combined_data_mock):

        def sample_get_combined_data(queries):
            return data

        data = [self.data]
        get_combined_data_mock.side_effect = sample_get_combined_data
        self.assertEqual(
            asset.ralph3_asset(today=self.date),
            (True, u'1 new assets, 0 updated, 1 total')
        )
        self.assertEqual(
            asset.ralph3_asset(today=self.date),
            (True, u'0 new assets, 1 updated, 1 total')
        )
