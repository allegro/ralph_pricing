# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy

from django.test import TestCase

from ralph_scrooge.models import (
    Environment,
    OwnershipType,
    ProfitCenter,
    Service,
)
from ralph_scrooge.plugins.collect.ralph3_service_environment import (
    update_service,
    update_environment,
)
from ralph_scrooge.tests.utils.factory import (
    ProfitCenterFactory,
    Ralph3OwnerFactory,
    ServiceFactory,
)
from ralph_scrooge.tests.plugins.collect.samples.ralph3_service_environment import (  # noqa
    SAMPLE_ENVIRONMENTS,
    SAMPLE_SERVICES,
)


class TestServiceEnvironmentCollectPlugin(TestCase):
    def setUp(self):
        self.data = deepcopy(SAMPLE_SERVICES[0])
        self.default_profit_center = ProfitCenter(pk=1)
        ProfitCenterFactory.reset_sequence()
        self.profit_centers = ProfitCenterFactory.create_batch(2)
        Ralph3OwnerFactory.reset_sequence()
        # Don't create more than 6 owners (see remark in Ralph3UserFactory for
        # explaination).
        self.owners = Ralph3OwnerFactory.create_batch(6)

    def _create_and_test_service(self, data):
        """
        General method to check if created/updated service match passed data
        """
        created, saved_service = update_service(
            data, self.default_profit_center
        )

        self.assertEquals(saved_service.name, data['name'])
        self.assertEquals(saved_service.symbol, data['uid'])

        # ownership
        self.assertEquals(
            saved_service.serviceownership_set.count(),
            len(data['business_owners']) + len(data['technical_owners'])
        )
        self.assertEquals(
            set(
                saved_service.serviceownership_set.filter(
                    type=OwnershipType.business
                ).values_list('owner__user__username', flat=True)
            ),
            set([o['username'] for o in data['business_owners']])
        )
        self.assertEquals(
            set(
                saved_service.serviceownership_set.filter(
                    type=OwnershipType.technical
                ).values_list('owner__user__username', flat=True)
            ),
            set([o['username'] for o in data['technical_owners']])
        )
        return created, saved_service

    def test_new_service(self):
        """
        Basic test for new service
        """
        self.assertEquals(Service.objects.count(), 0)
        created, service = self._create_and_test_service(self.data)
        self.assertTrue(created)
        self.assertEquals(Service.objects.count(), 1)
        self.assertIn(service.profit_center, self.profit_centers)

    def test_new_service_without_profit_center(self):
        """
        Basic test for new service without profit center
        """
        self.data['profit_center'] = None
        self.assertEquals(Service.objects.count(), 0)
        created, service = self._create_and_test_service(self.data)
        self.assertTrue(created)
        self.assertEquals(Service.objects.count(), 1)
        self.assertEquals(service.profit_center, self.default_profit_center)

    def test_service_update(self):
        """
        Check update of service data
        """
        created, service = self._create_and_test_service(self.data)
        self.assertTrue(created)
        service = ServiceFactory.build()
        self.data['name'] = service.name
        created, service = self._create_and_test_service(self.data)
        self.assertFalse(created)
        self.assertEquals(Service.objects.count(), 1)

    def test_owners_delete(self):
        """
        Checks if owners are correctly deleted
        """
        created, service = self._create_and_test_service(self.data)
        self.assertTrue(created)
        self.assertEquals(Service.objects.count(), 1)
        # remove one owner from technical and business
        self.data['technical_owners'].pop()
        del self.data['business_owners'][0]
        created, service = self._create_and_test_service(self.data)
        self.assertFalse(created)
        self.assertEquals(Service.objects.count(), 1)

    def test_owners_change(self):
        """
        Checks if owners are correctly added
        """
        created, service = self._create_and_test_service(self.data)
        self.assertTrue(created)
        self.assertEquals(Service.objects.count(), 1)
        # move one owner from technical to business
        self.data['business_owners'].append(
            self.data['technical_owners'].pop()
        )
        # add new technical owner
        self.data['technical_owners'].append({
            'username': self.owners[5].user.username,
        })
        created, service = self._create_and_test_service(self.data)
        self.assertFalse(created)
        self.assertEquals(Service.objects.count(), 1)

    def _compare_environments(self, environment, sample_data):
        self.assertEquals(environment.name, sample_data['name'])
        self.assertEquals(environment.ralph3_id, sample_data['id'])

    def test_add_environment(self):
        sample_data = SAMPLE_ENVIRONMENTS[0]
        self.assertTrue(update_environment(sample_data))
        environment = Environment.objects.get(ralph3_id=sample_data['id'])
        self._compare_environments(environment, sample_data)

    def test_update_environment(self):
        sample_data = SAMPLE_ENVIRONMENTS[0]
        self.assertTrue(update_environment(sample_data))
        environment = Environment.objects.get(ralph3_id=sample_data['id'])
        self._compare_environments(environment, sample_data)

        sample_data2 = SAMPLE_ENVIRONMENTS[1]
        sample_data2['id'] = sample_data['id']
        self.assertFalse(update_environment(sample_data2))
        environment = Environment.objects.get(
            ralph3_id=sample_data2['id']
        )
        self._compare_environments(environment, sample_data2)

    # TODO(xor-xor): Consider re-adding 'test_batch_update' test which has been
    # removed due to 'service' and 'environment' plugins being merged into one.

    # TODO(xor-xor): What about adding test for
    # SYNC_SERVICES_ONLY_CALCULATED_IN_SCROOGE..?
