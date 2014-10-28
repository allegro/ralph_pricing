# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from ralph_scrooge.models import (
    AssetInfo,
    DailyAssetInfo,
    DailyPricingObject,
    DailyUsage,
    PricingObject,
    UsageType,
)
from ralph_scrooge.plugins.collect import asset
from ralph_scrooge.tests.utils.factory import (
    AssetInfoFactory,
    DailyAssetInfoFactory,
    EnvironmentFactory,
    PricingObjectModelFactory,
    ServiceEnvironmentFactory,
    ServiceFactory,
    UsageTypeFactory,
    WarehouseFactory,
)


class TestAssetPlugin(TestCase):
    def setUp(self):
        # self.service = ServiceFactory.create()
        # self.environment = EnvironmentFactory.create()
        self.service_environment = ServiceEnvironmentFactory()
        self.date = datetime.date.today()
        self.warehouse = WarehouseFactory.create()
        self.model = PricingObjectModelFactory()
        self.value = 100
        self.data = {
            'asset_id': 1,
            'sn': 'SerialNumber',
            'barcode': 'Barcode',
            'device_id': 1,
            'asset_name': 'AssetName',
            'depreciation_rate': 25,
            'is_depreciated': True,
            'price': 100,
            'service_id': self.service_environment.service.ci_id,
            'warehouse_id': self.warehouse.id_from_assets,
            'environment_id': self.service_environment.environment.ci_id,  # noqa
            'cores_count': 4,
            'power_consumption': 200,
            'collocation': 2,
            'model_id': self.model.model_id,
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
        self.assertEqual(usage_type, UsageType.objects.get())
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
            asset_id=self.data['asset_id'],
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
            asset_id=self.data['asset_id'],
            warehouse=self.warehouse,
        )
        data = [self.data.copy(), self.data.copy()]
        data[1]['asset_id'] = 2
        data[1]['barcode'] = 'Barcode2'

        for d in data:
            asset.get_asset_info(self.service_environment, self.warehouse, d)
        self.assertEqual(AssetInfo.objects.count(), 2)
        asset1 = AssetInfo.objects.get(asset_id=1)
        asset2 = AssetInfo.objects.get(asset_id=2)
        self.assertEqual(asset1.barcode, data[0]['barcode'])
        self.assertEqual(asset2.barcode, data[1]['barcode'])
        self.assertEqual(asset2.sn, data[1]['sn'])
        self.assertEqual(asset2.device_id, data[1]['device_id'])
        self.assertIsNone(asset1.sn)
        self.assertIsNone(asset1.device_id)

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

    def test_update_assets_when_service_does_not_exist(self):
        self.data['service_id'] = ServiceFactory.build().ci_id
        with self.assertRaises(asset.ServiceEnvironmentDoesNotExistError):
            asset.update_assets(
                self.data,
                self.date,
                {
                    'depreciation': UsageTypeFactory.create(),
                    'assets_count': UsageTypeFactory.create(),
                    'cores_count': UsageTypeFactory.create(),
                    'power_consumption': UsageTypeFactory.create(),
                    'collocation': UsageTypeFactory.create(),
                }
            )

    def test_update_assets_when_warehouse_does_not_exist(self):
        self.data['warehouse_id'] = WarehouseFactory.build().id_from_assets
        with self.assertRaises(asset.WarehouseDoesNotExistError):
            asset.update_assets(
                self.data,
                self.date,
                {
                    'depreciation': UsageTypeFactory.create(),
                    'assets_count': UsageTypeFactory.create(),
                    'cores_count': UsageTypeFactory.create(),
                    'power_consumption': UsageTypeFactory.create(),
                    'collocation': UsageTypeFactory.create(),
                }
            )

    def test_update_assets_when_environment_does_not_exist(self):
        self.data['environment_id'] = EnvironmentFactory.build().ci_id
        with self.assertRaises(asset.ServiceEnvironmentDoesNotExistError):
            asset.update_assets(
                self.data,
                self.date,
                {
                    'depreciation': UsageTypeFactory.create(),
                    'assets_count': UsageTypeFactory.create(),
                    'cores_count': UsageTypeFactory.create(),
                    'power_consumption': UsageTypeFactory.create(),
                    'collocation': UsageTypeFactory.create(),
                }
            )

    def test_update_assets(self):
        self.assertTrue(asset.update_assets(
            self.data,
            self.date,
            {
                'depreciation': UsageTypeFactory.create(),
                'assets_count': UsageTypeFactory.create(),
                'cores_count': UsageTypeFactory.create(),
                'power_consumption': UsageTypeFactory.create(),
                'collocation': UsageTypeFactory.create(),
            }
        ))
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
            2,  # 1 dummy for service environment, 1 regular
        )
        self.assertEqual(
            DailyPricingObject.objects.all().count(),
            1,
        )

    def test_assets_when_new_pricing_object(self):
        asset.get_assets = lambda x: [self.data]
        self.assertEqual(
            asset.asset(today=self.date),
            (True, u'1 new, 0 updated, 1 total')
        )

    def test_assets_when_update_pricing_object(self):
        asset.get_assets = lambda x: [self.data]
        asset.asset(today=self.date)
        self.assertEqual(
            asset.asset(today=self.date),
            (True, u'0 new, 1 updated, 1 total')
        )

    def test_assets_when_no_effect(self):
        self.data['service_id'] = ServiceFactory.build().ci_id
        asset.get_assets = lambda x: [self.data]
        self.assertEqual(
            asset.asset(today=self.date),
            (True, u'0 new, 0 updated, 1 total')
        )
