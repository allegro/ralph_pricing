# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings

from ralph_scrooge import models
from ralph_scrooge.rest.components import ComponentsContent
from ralph_scrooge.tests.utils.factory import (
    DailyAssetInfoFactory,
    ServiceEnvironmentFactory,
)
from rest_framework.test import APIClient


class TestComponents(TestCase):
    def setUp(self):
        self.components = ComponentsContent()
        self.se1 = ServiceEnvironmentFactory()
        self.se2 = ServiceEnvironmentFactory(
            service=self.se1.service,
        )
        self.se3 = ServiceEnvironmentFactory()
        self.today = datetime.date(2014, 10, 11)

        self.dpo1, self.dpo2 = DailyAssetInfoFactory.create_batch(
            2,
            service_environment=self.se1,
            pricing_object__service_environment=self.se1,
            date=self.today,
        )
        self.dpo3 = DailyAssetInfoFactory(
            service_environment=self.se2,
            pricing_object__service_environment=self.se2,
            date=self.today,
        )
        self.dpo3 = DailyAssetInfoFactory(
            service_environment=self.se3,
            pricing_object__service_environment=self.se3,
            date=self.today,
        )
        self.maxDiff = None

    @override_settings(COMPONENTS_TABLE_SCHEMA={'Asset': {}, 'IP Address': {}})
    def test_get_types(self):
        result = self.components.get_types()
        self.assertEquals(
            set([r.id for r in result]),
            set([
                models.PRICING_OBJECT_TYPES.ASSET.id,
                models.PRICING_OBJECT_TYPES.IP_ADDRESS.id,
                ]),
        )

    def test_get_daily_pricing_objects(self):
        result = self.components.get_daily_pricing_objects(
            year=self.today.year,
            month=self.today.month,
            day=self.today.day,
            service=self.se1.service.id,
            env=self.se1.environment.id,
        )
        self.assertEquals(result.count(), 2)

    def test_get_daily_pricing_objects_without_env(self):
        result = self.components.get_daily_pricing_objects(
            year=self.today.year,
            month=self.today.month,
            day=self.today.day,
            service=self.se1.service.id,
        )
        self.assertEquals(result.count(), 3)

    def test_get_field(self):
        path = 'service_environment.service.profit_center.name'
        result = self.components.get_field(models.DailyPricingObject, path)
        self.assertEquals(
            result,
            models.ProfitCenter._meta.get_field_by_name('name')[0]
        )

    def test_get_field_one_to_one(self):
        path = 'pricing_object.service_environment.service.name'
        result = self.components.get_field(models.DailyAssetInfo, path)
        self.assertEquals(
            result,
            models.Service._meta.get_field_by_name('name')[0]
        )

    def test_get_field_error(self):
        path = 'service_environment.service.profit_center.name1'
        result = self.components.get_field(models.DailyPricingObject, path)
        self.assertIsNone(result)

    def test_get_field_error_inside(self):
        path = 'service_environment.service1.profit_center.name'
        result = self.components.get_field(models.DailyPricingObject, path)
        self.assertIsNone(result)

    def test_get_headers(self):
        fields = ['id', 'asset_info.sn', 'asset_info.barcode']
        headers = self.components.get_headers(models.DailyAssetInfo, fields)
        self.assertEquals(headers, {
            '0': 'Id',
            '1': 'Serial Number',
            '2': 'Barcode',
        })

    def test_get_headers_with_prefix(self):
        fields = ['id', 'name', 'assetinfo.sn', 'assetinfo.barcode']
        headers = self.components.get_headers(
            models.DailyAssetInfo,
            fields,
            prefix='pricing_object',
        )
        self.assertEquals(headers, {
            '0': 'Id',
            '1': 'Name',
            '2': 'Serial Number',
            '3': 'Barcode',
        })

    def test_get_headers_with_alias(self):
        fields = ['id', 'name', 'assetinfo.sn', ('assetinfo.barcode', 'Alias')]
        headers = self.components.get_headers(
            models.DailyAssetInfo,
            fields,
            prefix='pricing_object',
        )
        self.assertEquals(headers, {
            '0': 'Id',
            '1': 'Name',
            '2': 'Serial Number',
            '3': 'Alias',
        })

    @override_settings(COMPONENTS_TABLE_SCHEMA={'Asset': {
        'fields': [
            'pricing_object.id',
            'pricing_object.name',
            ('service_environment.service.name', 'Serv')
        ],
        'model': 'ralph_scrooge.models.DailyAssetInfo',
    }})
    def test_process_single_type(self):
        asset_type = models.PricingObjectType.objects.get(
            pk=models.PRICING_OBJECT_TYPES.ASSET.id
        )
        dpo = models.DailyPricingObject.objects.all()
        result = self.components.process_single_type(asset_type, dpo)

        def get_asset_dict(a):
            return {
                '0': a.pricing_object.id,
                '1': a.pricing_object.name,
                '2': a.service_environment.service.name,
            }
        self.assertEquals(result, {
            'name': asset_type.name,
            'icon_class': asset_type.icon_class,
            'slug': asset_type.name.lower().replace(' ', '_'),
            'value': map(get_asset_dict, dpo),
            'schema': {
                '0': 'Id',
                '1': 'Name',
                '2': 'Serv',
            },
            'color': asset_type.color,
        })

    def test_api_view_returns_data_from_pricing_objects(self):
        User.objects.create_superuser('test', 'test@test.test', 'test')
        client = APIClient()
        client.login(username='test', password='test')
        resp = client.get('/scrooge/rest/components/{}/{}/{}/{}/{}/'.format(
            self.se1.service.id,
            self.se1.environment.id,
            self.today.year,
            self.today.month,
            self.today.day,
        ))
        data = json.loads(resp.content)
        self.assertEqual(len(data[0]['value']), 2)
