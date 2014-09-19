# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
import mock

from django.test import TestCase

from ralph_scrooge.models import Owner
from ralph_scrooge.plugins.collect.owner import (
    owner as owner_plugin,
    update_owner
)
from ralph_scrooge.tests.plugins.collect.samples.owner import SAMPLE_OWNERS
from ralph_scrooge.tests.utils.factory import UserFactory


class TestOwnerCollectPlugin(TestCase):
    def setUp(self):
        self.today = date(2014, 07, 01)

    def _compare_owner(self, owner, sample_data):
        self.assertEquals(owner.cmdb_id, sample_data['id'])
        self.assertEquals(owner.profile_id, sample_data['profile_id'])

    def test_add_owner(self):
        sample_data = SAMPLE_OWNERS[0]
        user = UserFactory()
        sample_data['profile_id'] = user.profile.id
        self.assertTrue(update_owner(sample_data, self.today))
        owner = Owner.objects.get(cmdb_id=sample_data['id'])
        self._compare_owner(owner, sample_data)

    def test_update_owner(self):
        sample_data = SAMPLE_OWNERS[0]
        user = UserFactory()
        sample_data['profile_id'] = user.profile.id
        self.assertTrue(update_owner(sample_data, self.today))
        owner = Owner.objects.get(cmdb_id=sample_data['id'])
        self._compare_owner(owner, sample_data)

        sample_data2 = SAMPLE_OWNERS[1]
        sample_data2['id'] = sample_data['id']
        user = UserFactory()
        sample_data2['profile_id'] = user.profile.id
        self.assertFalse(update_owner(sample_data2, self.today))
        owner = Owner.objects.get(cmdb_id=sample_data2['id'])
        self._compare_owner(owner, sample_data2)

    @mock.patch('ralph_scrooge.plugins.collect.owner.update_owner')
    @mock.patch('ralph_scrooge.plugins.collect.owner.get_owners')
    def test_batch_update(self, get_owners_mock, update_owner_mock):
        def sample_update_owner(data, date):
            return data['id'] % 2 == 0

        def sample_get_owners():
            for owner in SAMPLE_OWNERS:
                yield owner

        update_owner_mock.side_effect = sample_update_owner
        get_owners_mock.side_effect = sample_get_owners
        result = owner_plugin(today=self.today)
        self.assertEquals(
            result,
            (True, '1 new owner(s), 1 updated, 2 total')
        )
        update_owner_mock.call_count = 2
        update_owner_mock.assert_any_call(SAMPLE_OWNERS[0], self.today)
        update_owner_mock.assert_any_call(SAMPLE_OWNERS[1], self.today)
