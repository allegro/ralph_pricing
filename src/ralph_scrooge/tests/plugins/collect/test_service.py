# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.test import TestCase

from ralph_scrooge.models import Service, OwnershipType
from ralph_scrooge.plugins.collect.service import (
    service as service_plugin,
    update_service,
)
from ralph_scrooge.tests.utils.factory import (
    BusinessLineFactory,
    OwnerFactory,
    ServiceFactory,
)
from ralph_scrooge.tests.plugins.collect.samples.service import SAMPLE_SERVICES


class TestServiceCollectPlugin(TestCase):
    def setUp(self):
        self.business_line = BusinessLineFactory()
        self.owners = OwnerFactory.create_batch(7)

    def _sample_data(self):
        service = ServiceFactory.build()
        return {
            'ci_uid': service.ci_uid,
            'name': service.name,
            'business_line': self.business_line.ci_uid,
            'technical_owners': [o.cmdb_id for o in self.owners[:3]],
            'business_owners': [o.cmdb_id for o in self.owners[3:6]],
        }

    def _create_and_test_service(self, data):
        """
        General method to check if created/updated service match passed data
        """
        date = datetime.date(2014, 07, 01)
        created = update_service(data, date)

        saved_service = Service.objects.get(ci_uid=data['ci_uid'])
        self.assertEquals(saved_service.name, data['name'])

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
        return created

    def test_new_service(self):
        """
        Basic test for new service
        """
        data = self._sample_data()
        self.assertEquals(Service.objects.count(), 0)
        self.assertTrue(self._create_and_test_service(data))
        self.assertEquals(Service.objects.count(), 1)

    def test_service_update(self):
        """
        Check update of service data
        """
        data = self._sample_data()
        self.assertTrue(self._create_and_test_service(data))
        service = ServiceFactory.build()
        data['name'] = service.name
        self.assertFalse(self._create_and_test_service(data))
        self.assertEquals(Service.objects.count(), 1)

    def test_owners_delete(self):
        """
        Checks if owners are correctly deleted
        """
        data = self._sample_data()
        self.assertTrue(self._create_and_test_service(data))
        self.assertEquals(Service.objects.count(), 1)
        # remove one owner from technical and business
        data['technical_owners'].pop()
        del data['business_owners'][0]
        self.assertFalse(self._create_and_test_service(data))
        self.assertEquals(Service.objects.count(), 1)

    def test_owners_change(self):
        """
        Checks if owners are correctly added
        """
        data = self._sample_data()
        self.assertTrue(self._create_and_test_service(data))
        self.assertEquals(Service.objects.count(), 1)
        # move one owner from technical to business
        data['business_owners'].append(data['technical_owners'].pop())
        # add new technical owner
        data['technical_owners'].append(self.owners[6].cmdb_id)
        self.assertFalse(self._create_and_test_service(data))
        self.assertEquals(Service.objects.count(), 1)

    @mock.patch('ralph_scrooge.plugins.collect.service.update_service')
    @mock.patch('ralph_scrooge.plugins.collect.service.get_services')
    def test_batch_update(self, get_services_mock, update_service_mock):
        def sample_update_service(data, date):
            return int(data['ci_uid'].split('-')[-1]) % 2 == 0

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
        update_service_mock.call_count = 2
        update_service_mock.assert_any_call(SAMPLE_SERVICES[0], date)
        update_service_mock.assert_any_call(SAMPLE_SERVICES[1], date)
