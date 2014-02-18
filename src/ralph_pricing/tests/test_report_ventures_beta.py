# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from ralph_pricing import models
from ralph_pricing.views.ventures_beta import AllVenturesBeta as AllVentures


class TestReportVenturesBeta(TestCase):
    def setUp(self):
        self.day = day = datetime.date(2013, 4, 25)

        # ventures
        self.venture = models.Venture(venture_id=1, name='a', is_active=True)
        self.venture.save()
        subventure = models.Venture(
            venture_id=2,
            parent=self.venture,
            name='b',
            is_active=False,
        )
        subventure.save()

        # devices (assets)
        device = models.Device(
            device_id=3,
            asset_id=5,
        )
        device.save()
        daily = models.DailyDevice(
            pricing_device=device,
            date=day,
            name='ziew',
            price=1337,
            pricing_venture=self.venture,
        )
        daily.save()

        other_device = models.Device(
            device_id=2,
            asset_id=3,
        )
        other_device.save()
        other_daily = models.DailyDevice(
            pricing_device=other_device,
            date=day,
            name='ziew',
            price=833833,
            pricing_venture=subventure,
        )
        other_daily.save()

        # warehouse
        self.warehouse = models.Warehouse(name='Warehouse1')
        self.warehouse.save()

        # usages
        usage_type = models.UsageType(name='ut1')
        usage_type.save()
        daily_usage = models.DailyUsage(
            type=usage_type,
            value=32,
            date=day,
            pricing_venture=self.venture,
        )
        daily_usage.save()
        usage_type2 = models.UsageType(name='ut2')
        usage_type2.save()

        # usages by warehouse
        warehouse_usage_type = models.UsageType(
            name='waciki2',
            by_warehouse=True,
        )
        warehouse_usage_type.save()
        daily_warehouse_usage = models.DailyUsage(
            type=warehouse_usage_type,
            value=120,
            date=day,
            pricing_venture=self.venture,
            warehouse=self.warehouse,
        )
        daily_warehouse_usage.save()

    def test_get_usage_types(self):
        """
        Test if usage types are correctly filtered and ordered
        """
        pass

    def test_get_as_currency(self):
        """
        Test if decimal is properly 'transformed' to currency
        """
        pass

    def test_prepare_field(self):
        """
        Test if field is properly prepared for placing it in report
        """
        pass

    def test_prepare_row(self):
        """
        Test if whole row is properly prepared for placing it in report
        """
        pass

    def test_get_ventures(self):
        """
        Test if ventures are correctly filtered
        """
        pass

    def test_get_report_data(self):
        """
        Test generating data for whole report
        """
        pass

    def test_get_schema(self):
        """
        Test getting full schema for report
        """
        pass

    def test_get_header(self):
        """
        Test getting headers for report
        """
        pass
