# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date, timedelta

from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.models import PRICING_OBJECT_TYPES
from ralph_scrooge.report.report_services_changes import ServicesChangesReport
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import (
    AssetInfoFactory,
    DailyAssetInfoFactory,
    DailyPricingObjectFactory,
    PricingObjectFactory,
    ServiceEnvironmentFactory,
)


class TestServicesChangesReport(ScroogeTestCase):
    def setUp(self):
        self.se1 = ServiceEnvironmentFactory()
        self.se2 = ServiceEnvironmentFactory()
        self.se3 = ServiceEnvironmentFactory(
            service=self.se1.service,
        )
        self.today = date(2013, 10, 12)
        self.yesterday = self.today - timedelta(days=1)

    def _create_pricing_objects(self):
        self.po1 = PricingObjectFactory(
            service_environment=self.se1,
            type_id=PRICING_OBJECT_TYPES.UNKNOWN,
        )
        self.dpo1 = DailyPricingObjectFactory(
            service_environment=self.se1,
            pricing_object=self.po1,
            date=self.today,
        )
        self.dpo2 = DailyPricingObjectFactory(
            service_environment=self.se2,
            pricing_object=self.po1,
            date=self.yesterday,
        )

    def _create_asset_info(self):
        self.ai = AssetInfoFactory(
            service_environment=self.se1,
            barcode='123',
            sn='987654321',
        )
        self.dai1 = DailyAssetInfoFactory(
            service_environment=self.se1,
            pricing_object=self.ai,
            asset_info=self.ai,
            date=self.today,
        )
        self.dai2 = DailyAssetInfoFactory(
            service_environment=self.se2,
            pricing_object=self.ai,
            asset_info=self.ai,
            date=self.yesterday,
        )

    def _get_default_result(self, update_with=None):
        pricing_object_types = ServicesChangesReport._get_types()
        result = {pot: [] for pot in pricing_object_types}
        if update_with:
            result.update(update_with)
        return result

    def test_get_types(self):
        pricing_object_types = ServicesChangesReport._get_types()
        self.assertNotIn(PRICING_OBJECT_TYPES.DUMMY, pricing_object_types)
        self.assertEquals(
            len(pricing_object_types),
            len(PRICING_OBJECT_TYPES.__choices__) - 1
        )

    def test_report_pricing_object(self):
        self._create_pricing_objects()
        for percent, result in ServicesChangesReport.get_data(
            start=date(2013, 10, 10),
            end=date(2013, 10, 13),
        ):
            pass
        self.assertEquals(result, self._get_default_result({
            PRICING_OBJECT_TYPES.UNKNOWN: [(
                self.po1.id,
                self.po1.name,
                date(2013, 10, 12),
                self.se2.service.name,
                self.se2.environment.name,
                self.se1.service.name,
                self.se1.environment.name,
            )],
        }))

    def test_report_asset(self):
        self._create_asset_info()
        for percent, result in ServicesChangesReport.get_data(
            start=date(2013, 10, 10),
            end=date(2013, 10, 13),
        ):
            pass
        self.assertEquals(result, self._get_default_result({
            PRICING_OBJECT_TYPES.ASSET: [(
                self.ai.id,
                self.ai.name,
                self.ai.barcode,
                self.ai.sn,
                self.ai.asset_id,
                date(2013, 10, 12),
                self.se2.service.name,
                self.se2.environment.name,
                self.se1.service.name,
                self.se1.environment.name,
            )],
        }))

    def test_get_header(self):
        header = ServicesChangesReport.get_header()
        default = [
            _('ID'),
            _('Name'),
            # PLACE FOR ADDITIONAL HEADERS
            _('Change date'),
            _('Service before change'),
            _('Environment before change'),
            _('Service after change'),
            _('Environment after change'),
        ]
        asset_header = default[:]
        asset_header[2:2] = [
            _('Barcode'),
            _('SN'),
            _('Asset ID'),
        ]
        self.assertEquals(header, {
            PRICING_OBJECT_TYPES.ASSET: [asset_header],
            PRICING_OBJECT_TYPES.VIRTUAL: [default],
            PRICING_OBJECT_TYPES.TENANT: [default],
            PRICING_OBJECT_TYPES.IP_ADDRESS: [default],
            PRICING_OBJECT_TYPES.VIP: [default],
            PRICING_OBJECT_TYPES.DATABASE: [default],
            PRICING_OBJECT_TYPES.UNKNOWN: [default],
        })
