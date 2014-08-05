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
    PricingObject,
    DailyPricingObject,
    UsageType,
    DailyUsage,
)
from ralph_scrooge.plugins.collect import asset
from ralph_scrooge.tests.utils.factory import (
    WarehouseFactory,
    ServiceFactory,
    PricingObjectFactory,
    AssetInfoFactory,
    DailyPricingObjectFactory,
    UsageTypeFactory,
)


class TestAssetPlugin(TestCase):
    def setUp(self):
        self.service = ServiceFactory.create()
        self.date = datetime.date.today()
        self.warehouse = WarehouseFactory.create()
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
            'service_ci_uid': self.service.ci_uid,
            'warehouse_id': self.warehouse.id_from_assets,
            'core': 4,
            'power_consumption': 200,
            'collocation': 2,
        }

    def test_get_usage(self):
        self.assertEqual(
            asset.get_usage('test_symbol', 'test_name', True, False, True),
            UsageType.objects.all()[0]
        )

    def test_create_pricing_object(self):
        self.assertEqual(
            asset.create_pricing_object(self.service, self.data),
            PricingObject.objects.all()[:1].get(),
        )

    def test_get_asset_and_pricing_object_when_asset_info_not_exist(self):
        self.assertEqual(
            asset.get_asset_and_pricing_object(
                self.service,
                self.warehouse,
                self.data,
            ),
            (
                AssetInfo.objects.all()[:1].get(),
                PricingObject.objects.all()[:1].get(),
                True,
            )
        )

    def test_get_asset_and_pricing_object_when_asset_info_exist(self):
        AssetInfo.objects.create(
            asset_id=self.data['asset_id'],
            pricing_object=PricingObjectFactory.create(),
            warehouse=self.warehouse,
        )
        self.assertEqual(
            asset.get_asset_and_pricing_object(
                self.service,
                self.warehouse,
                self.data,
            ),
            (
                AssetInfo.objects.all()[:1].get(),
                PricingObject.objects.all()[:1].get(),
                False,
            )
        )

    def test_get_daily_pricing_object(self):
        self.assertEqual(
            asset.get_daily_pricing_object(
                PricingObjectFactory.create(),
                self.service,
                self.date,
            ),
            DailyPricingObject.objects.all()[:1].get()
        )

    def test_get_daily_asset_info(self):
        self.assertEqual(
            asset.get_daily_asset_info(
                AssetInfoFactory.create(),
                DailyPricingObjectFactory.create(
                    pricing_object=PricingObjectFactory.create(),
                ),
                self.date,
                self.data,
            ),
            DailyAssetInfo.objects.all()[:1].get()
        )

    def test_update_usage(self):
        asset.update_usage(
            self.service,
            DailyPricingObjectFactory.create(
                pricing_object=PricingObjectFactory.create(),
            ),
            UsageTypeFactory.create(),
            self.value,
            self.date,
            self.warehouse,
        )
        self.assertEqual(
            DailyUsage.objects.all().count(),
            1
        )

    def test_update_assets_when_service_does_not_exist(self):
        self.data['service_ci_uid'] = 2
        self.assertRaises(
            asset.ServiceDoesNotExistError,
            asset.update_assets,
            data=self.data,
            date=self.date,
            usages={
                'core': UsageTypeFactory.create(),
                'power_consumption': UsageTypeFactory.create(),
                'collocation': UsageTypeFactory.create(),
            },
        )

    def test_update_assets_when_warehouse_does_not_exist(self):
        self.data['warehouse_id'] = 2
        self.assertRaises(
            asset.WarehouseDoesNotExistError,
            asset.update_assets,
            data=self.data,
            date=self.date,
            usages={
                'core': UsageTypeFactory.create(),
                'power_consumption': UsageTypeFactory.create(),
                'collocation': UsageTypeFactory.create(),
            },
        )

    def test_update_assets(self):
        self.assertEqual(
            asset.update_assets(
                self.data,
                self.date,
                {
                    'core': UsageTypeFactory.create(),
                    'power_consumption': UsageTypeFactory.create(),
                    'collocation': UsageTypeFactory.create(),
                }
            ),
            True
        )
        self.assertEqual(
            DailyUsage.objects.all().count(),
            3,
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
            1,
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
        self.data['service_ci_uid'] = 3
        asset.get_assets = lambda x: [self.data]
        self.assertEqual(
            asset.asset(today=self.date),
            (True, u'0 new, 0 updated, 1 total')
        )
