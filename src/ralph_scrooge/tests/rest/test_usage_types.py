# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APIClient

from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import UsageTypeFactory


class TestUsageTypesAPI(ScroogeTestCase):

    def setUp(self):
        superuser = get_user_model().objects.create_superuser(
            'test', 'test@test.test', 'test'
        )
        self.client = APIClient()
        self.client.force_authenticate(superuser)
        UsageTypeFactory.create_batch(10)

    def test_get_usage_types(self):
        url = reverse('v010:usagetype-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 10)

    def test_get_usage_type_by_symbol(self):
        UsageTypeFactory(symbol='symbol.1')
        response = self.client.get(
            reverse('v010:usagetype-detail', args=['symbol.1'])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json['symbol'], 'symbol.1')
