# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.test import TestCase

from ralph_scrooge.models import ProfitCenter, Service, OwnershipType
from ralph_scrooge.plugins.collect.service import (
    service as service_plugin,
    update_service,
)
from ralph_scrooge.tests.utils.factory import (
    ProfitCenterFactory,
    OwnerFactory,
    ServiceFactory,
)
from ralph_scrooge.tests.plugins.collect.samples.service import SAMPLE_SERVICES


class TestServiceCollectPlugin(TestCase):
    def setUp(self):
        self.default_profit_center = ProfitCenter(pk=1)
        self.profit_center = ProfitCenterFactory()
        self.owners = OwnerFactory.create_batch(7)

    def _sample_data(self):
        service = ServiceFactory.build()
        return {
            'ci_id': service.ci_id,
            'ci_uid': service.ci_uid,
            'name': service.name,
            'symbol': service.symbol,
            'profit_center': self.profit_center.ci_id,
            'technical_owners': [o.cmdb_id for o in self.owners[:3]],
            'business_owners': [o.cmdb_id for o in self.owners[3:6]],
        }

    def _create_and_test_service(self, data):
        """
        General method to check if created/updated service match passed data
        """
        date = datetime.date(2014, 07, 01)
        created = update_service(data, date, self.default_profit_center)

        saved_service = Service.objects.get(ci_id=data['ci_id'])
        self.assertEquals(saved_service.name, data['name'])
        self.assertEquals(saved_service.symbol, data['symbol'])

        # ownership
        self.assertEquals(
            saved_service.serviceownership_set.count(),
            len(data['business_owners']) + len(data['technical_owners'])
        )
        self.assertEquals(
            set(
                saved_service.serviceownership_set.filter(
                    type=OwnershipType.business
                ).values_list('owner__cmdb_id', flat=True)
            ),
            set(data['business_owners'])
        )
        self.assertEquals(
            set(
                saved_service.serviceownership_set.filter(
                    type=OwnershipType.technical
                ).values_list('owner__cmdb_id', flat=True)
            ),
            set(data['technical_owners'])
        )
        return created, saved_service

    def test_new_service(self):
        """
        Basic test for new service
        """
        data = self._sample_data()
        self.assertEquals(Service.objects.count(), 0)
        created, service = self._create_and_test_service(data)
        self.assertTrue(created)
        self.assertEquals(Service.objects.count(), 1)
        self.assertEquals(service.profit_center, self.profit_center)

    def test_new_service_without_profit_center(self):
        """
        Basic test for new service without business line
        """
        data = self._sample_data()
        data['profit_center'] = None
        self.assertEquals(Service.objects.count(), 0)
        created, service = self._create_and_test_service(data)
        self.assertTrue(created)
        self.assertEquals(Service.objects.count(), 1)
        self.assertEquals(service.profit_center, self.default_profit_center)

    def test_service_update(self):
        """
        Check update of service data
        """
        data = self._sample_data()
        created, service = self._create_and_test_service(data)
        self.assertTrue(created)
        service = ServiceFactory.build()
        data['name'] = service.name
        created, service = self._create_and_test_service(data)
        self.assertFalse(created)
        self.assertEquals(Service.objects.count(), 1)

    def test_owners_delete(self):
        """
        Checks if owners are correctly deleted
        """
        data = self._sample_data()
        created, service = self._create_and_test_service(data)
        self.assertTrue(created)
        self.assertEquals(Service.objects.count(), 1)
        # remove one owner from technical and business
        data['technical_owners'].pop()
        del data['business_owners'][0]
        created, service = self._create_and_test_service(data)
        self.assertFalse(created)
        self.assertEquals(Service.objects.count(), 1)

    def test_owners_change(self):
        """
        Checks if owners are correctly added
        """
        data = self._sample_data()
        created, service = self._create_and_test_service(data)
        self.assertTrue(created)
        self.assertEquals(Service.objects.count(), 1)
        # move one owner from technical to business
        data['business_owners'].append(data['technical_owners'].pop())
        # add new technical owner
        data['technical_owners'].append(self.owners[6].cmdb_id)
        created, service = self._create_and_test_service(data)
        self.assertFalse(created)
        self.assertEquals(Service.objects.count(), 1)

    @mock.patch('ralph_scrooge.plugins.collect.service.update_service')
    @mock.patch('ralph_scrooge.plugins.collect.service.get_services')
    def test_batch_update(self, get_services_mock, update_service_mock):
        def sample_update_service(data, date, default_profit_center):
            return data['ci_id'] % 2 == 0

        def sample_get_services():
            for owner in SAMPLE_SERVICES:
                yield owner

        date = datetime.date(2014, 07, 01)
        update_service_mock.side_effect = sample_update_service
        get_services_mock.side_effect = sample_get_services
        result = service_plugin(today=date)
        self.assertEquals(
            result,
            (True, '1 new service(s), 1 updated, 2 total')
        )
        self.assertEquals(update_service_mock.call_count, 2)
        update_service_mock.assert_any_call(
            SAMPLE_SERVICES[0],
            date,
            self.default_profit_center,
        )
        update_service_mock.assert_any_call(
            SAMPLE_SERVICES[1],
            date,
            self.default_profit_center,
        )
