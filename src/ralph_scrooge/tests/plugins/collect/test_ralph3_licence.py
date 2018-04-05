# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from decimal import Decimal

from mock import patch

from ralph_scrooge.models.extra_cost import LicenceCost, EXTRA_COST_TYPES
from ralph_scrooge.plugins.collect.ralph3_licence import (
    update_licence,
    ralph3_licence
)
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import DailyAssetInfoFactory
from ralph_scrooge.tests.utils.url_helpers import get_pricing_object_url


class TestRalph3LicencePlugin(ScroogeTestCase):
    def setUp(self):
        self.today = date(2017, 2, 17)
        self.daily_asset1 = DailyAssetInfoFactory()
        self.daily_asset2 = DailyAssetInfoFactory()
        self.data = {
            'id': 1,
            '__str__': 'licence: 2018-03-27',
            'base_objects': [],
            'invoice_date': date(2018, 3, 27),
            'valid_thru': date(2018, 4, 18),
            'price': '1000.00',
        }

    def _assertLicenceCostWithData(self, licence_cost, data, price_divider=1):
        self.assertEqual(licence_cost.licence_id, data['id'])
        self.assertEqual(licence_cost.start, data['invoice_date'])
        self.assertEqual(licence_cost.end, data['valid_thru'])
        self.assertEqual(licence_cost.remarks, data['__str__'])
        self.assertEqual(licence_cost.extra_cost_type.id,
                         EXTRA_COST_TYPES.LICENCE.id)
        self.assertEqual(licence_cost.cost,
                         (Decimal(data['price']) / price_divider))

    def test_licence_with_no_base_objects(self):
        # TODO (mbleschke) - change when added support for this case
        result = update_licence(self.data)

        self.assertEqual(result, 0)
        self.assertEqual(LicenceCost.objects.count(), 0)

    def test_licence_with_one_base_object_adds_one_licence_cost(self):
        self.data['base_objects'].append({
            'base_object': get_pricing_object_url(
                self.daily_asset1.asset_info.ralph3_asset_id
            )
        })

        result = update_licence(self.data)
        licence_cost = LicenceCost.objects.get()

        self.assertEqual(LicenceCost.objects.count(), 1)
        self.assertEqual(result, 1)
        self._assertLicenceCostWithData(licence_cost, self.data)

    def test_licence_with_multiple_base_object_adds_multiple_licence_cost(self):  # noqa
        self.data['base_objects'].extend([
            {
                'base_object': get_pricing_object_url(
                    self.daily_asset1.asset_info.ralph3_asset_id
                )
            },
            {
                'base_object': get_pricing_object_url(
                    self.daily_asset2.asset_info.ralph3_asset_id
                )
            }
        ])

        result = update_licence(self.data)
        licence_costs = LicenceCost.objects.all()

        self.assertEqual(result, 2)
        self.assertEqual(LicenceCost.objects.count(), 2)
        self._assertLicenceCostWithData(licence_costs[0], self.data,
                                        price_divider=2)
        self._assertLicenceCostWithData(licence_costs[1], self.data,
                                        price_divider=2)

    def test_licence_with_not_existing_pricing_object_wont_add_licence_cost(self):  # noqa
        self.data['base_objects'].append({
            'base_object': get_pricing_object_url(999)
        })

        result = update_licence(self.data)

        self.assertEqual(result, 0)
        self.assertEqual(LicenceCost.objects.count(), 0)

    def test_licence_with_existing_cost_will_update_licence_cost(self):
        self.data['base_objects'].append({
            'base_object': get_pricing_object_url(
                self.daily_asset1.asset_info.ralph3_asset_id
            )
        })

        update_licence(self.data)
        self.data['price'] = '250.0'
        result = update_licence(self.data)
        licence_cost = LicenceCost.objects.get()

        self.assertEqual(LicenceCost.objects.count(), 1)
        self.assertEqual(result, 1)
        self._assertLicenceCostWithData(licence_cost, self.data)

    @patch('ralph_scrooge.plugins.collect.ralph3_licence.update_licence')
    @patch('ralph_scrooge.plugins.collect.ralph3_licence.get_from_ralph')
    def test_licence_plugin(self, get_from_ralph_mock, update_licence_mock):
        update_licence_mock.return_value = 3

        def get_licences(endpoint, logger, query=None):
            return [self.data, self.data]

        get_from_ralph_mock.side_effect = get_licences

        result = ralph3_licence(today=date(2017, 2, 17))
        self.assertEquals(
            result,
            (True, 'Licence: 2 total for 6 pricing objects')
        )
        self.assertEquals(update_licence_mock.call_count, 2)
