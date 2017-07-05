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
from ralph_scrooge.tests.utils.factory import (
    DailyUsageFactory,
    ServiceEnvironmentFactory
)


class TestUsageTypesAPI(ScroogeTestCase):

    def setUp(self):
        superuser = get_user_model().objects.create_superuser(
            'test', 'test@test.test', 'test'
        )
        self.client = APIClient()
        self.client.force_authenticate(superuser)
        se1 = ServiceEnvironmentFactory(service__ci_uid='sc-123')
        se2 = ServiceEnvironmentFactory(service__ci_uid='sc-321')
        DailyUsageFactory.create_batch(
            10,
            date='2017-07-01',
            service_environment=se1,
        )
        DailyUsageFactory.create_batch(
            20,
            date='2017-08-01',
            service_environment=se2
        )

    def test_get_daily_usages(self):
        url = reverse('v0_10:dailyusage-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 30)

    def test_filter_daily_usages_by_date(self):
        response = self.client.get(
            '{}?{}'.format(
                reverse('v0_10:dailyusage-list'), 'date__gte=2017-07-03'
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 20)

    def test_filter_daily_usages_by_service_uid(self):
        response = self.client.get(
            '{}?{}'.format(
                reverse('v0_10:dailyusage-list'), 'service_uid=sc-321'
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 20)
