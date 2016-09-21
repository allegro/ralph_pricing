# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json
from copy import deepcopy

from django.core.urlresolvers import reverse
from django.test import TestCase

from ralph_scrooge.models import DailyUsage, ServiceUsageTypes
from ralph_scrooge.tests.utils.factory import (
    PricingObjectFactory,
    PricingServiceFactory,
    ServiceEnvironmentFactory,
    UsageTypeFactory,
)
from rest_framework.test import APIClient

# XXX
from ralph_scrooge.models import (
    DailyUsage,
    PricingObject,
    PricingService,
    ServiceEnvironment,
    UsageType,
)
from pprint import pprint

def print_state():
    print('PricingService:')
    print(PricingService.objects.all())
    print('\n')
    print('ServiceEnvironment:')
    print(ServiceEnvironment.objects.all())
    print('\n')
    print('PricingObject:')
    print(PricingObject.objects.all())
    print('\n')
    print('UsageType:')
    print(UsageType.objects.all())
    print('\n')
    print('ServiceUsageTypes:')
    print(ServiceUsageTypes.objects.all())
    print('\n')
    print('DailyUsage:')
    print(DailyUsage.objects.all())
    print('\n')


class TestPricingServiceUsages(TestCase):

    def setUp(self):
        self.date = datetime.date(2016, 9, 8)
        self.today = datetime.date.today()  # XXX unused..?
        client = APIClient()
        self.pricing_service = PricingServiceFactory()
        self.pricing_object1 = PricingObjectFactory()
        self.pricing_object2 = PricingObjectFactory()
        self.service_environment1 = self.pricing_object1.service_environment
        self.service_environment2 = self.pricing_object2.service_environment
        self.usage_type1 = UsageTypeFactory()
        self.usage_type2 = UsageTypeFactory()
        ServiceUsageTypes.objects.create(
            usage_type=self.usage_type1,
            pricing_service=self.pricing_service,
            start=datetime.date.min,
            end=datetime.date.max,
            percent=50,
        )
        ServiceUsageTypes.objects.create(
            usage_type=self.usage_type2,
            pricing_service=self.pricing_service,
            start=datetime.date.min,
            end=datetime.date.max,
            percent=50,
        )

    def test_save_usages_successfully_when_pricing_object_given(self):
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": "2016-09-08",
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 40,
                        },
                    ],
                },
            ]
        }

        self.assertEquals(DailyUsage.objects.all().count(), 0)
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        daily_usages = DailyUsage.objects.order_by('id')
        self.assertEquals(daily_usages.count(), 1)
        self.assertEquals(
            daily_usages[0].service_environment,
            self.service_environment1
        )
        self.assertEquals(daily_usages[0].date, self.date)
        self.assertEquals(daily_usages[0].type, self.usage_type1)
        self.assertEquals(daily_usages[0].value, 40)


    def test_save_usages_successfully_when_service_and_environment_given(self):
        service_name = self.pricing_object1.service_environment.service.name
        environment_name = (
            self.pricing_object1.service_environment.environment.name
        )
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": "2016-09-08",
            "usages": [
                {
                    "service": service_name,
                    "environment": environment_name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 40,
                        },
                    ],
                },
            ]
        }

        self.assertEquals(DailyUsage.objects.all().count(), 0)
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        daily_usages = DailyUsage.objects.order_by('id')
        self.assertEquals(daily_usages.count(), 1)
        self.assertEquals(
            daily_usages[0].service_environment,
            self.service_environment1
        )
        self.assertEquals(daily_usages[0].date, self.date)
        self.assertEquals(daily_usages[0].type, self.usage_type1)
        self.assertEquals(daily_usages[0].value, 40)


    def test_save_usages_successfully_when_service_id_and_environment_given(self):  # noqa
        service_id = self.pricing_object1.service_environment.service_id
        environment_name = (
            self.pricing_object1.service_environment.environment.name
        )
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": "2016-09-08",
            "usages": [
                {
                    "service_id": service_id,
                    "environment": environment_name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 40,
                        },
                    ],
                },
            ]
        }

        self.assertEquals(DailyUsage.objects.all().count(), 0)
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        daily_usages = DailyUsage.objects.order_by('id')
        self.assertEquals(daily_usages.count(), 1)
        self.assertEquals(
            daily_usages[0].service_environment,
            self.service_environment1
        )
        self.assertEquals(daily_usages[0].date, self.date)
        self.assertEquals(daily_usages[0].type, self.usage_type1)
        self.assertEquals(daily_usages[0].value, 40)

    def test_save_usages_successfully_when_service_uid_and_environment_given(self):  # noqa
        service_uid = self.pricing_object1.service_environment.service.ci_uid
        environment_name = (
            self.pricing_object1.service_environment.environment.name
        )
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": "2016-09-08",
            "usages": [
                {
                    "service_uid": service_uid,
                    "environment": environment_name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 40,
                        },
                    ],
                },
            ]
        }

        self.assertEquals(DailyUsage.objects.all().count(), 0)
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        daily_usages = DailyUsage.objects.order_by('id')
        self.assertEquals(daily_usages.count(), 1)
        self.assertEquals(
            daily_usages[0].service_environment,
            self.service_environment1
        )
        self.assertEquals(daily_usages[0].date, self.date)
        self.assertEquals(daily_usages[0].type, self.usage_type1)
        self.assertEquals(daily_usages[0].value, 40)


    def test_for_error_when_non_existing_pricing_service_given(self):
        pricing_service_usage = {
            "pricing_service": 'fake_pricing_service',
            "date": "2016-09-08",
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 40,
                        },
                    ],
                },
            ]
        }

        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        errors = json.loads(resp.content)['pricing_service']
        self.assertEquals(len(errors), 1)
        self.assertIn('fake_pricing_service', errors[0])


    def test_for_error_when_non_existing_service_given(self):
        environment_name = (
            self.pricing_object1.service_environment.environment.name
        )
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": "2016-09-08",
            "usages": [
                {
                    "service": 'fake_service',
                    "environment": environment_name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 40,
                        },
                    ],
                },
            ]
        }

        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        errors = json.loads(resp.content)['usages'][0]['non_field_errors']
        self.assertEquals(len(errors), 1)
        self.assertIn('fake_service', errors[0])
        self.assertIn('does not exist', errors[0])


    # def test_for_error_when_invalid_service_id_given(self):
    #     pass

    # def test_for_error_when_invalid_service_uid_given(self):
    #     pass

    # def test_for_error_when_invalid_environment_given(self):
    #     pass

    # def test_for_error_when_invalid_usage_given(self):
    #     pass

    # XXX Consider adding 'missing' variant for the tests above.

    def test_not_overwriting_by_default(self):
        # 1st POST (same day, same usage type):
        # daily usage 1: service env 1, value 40
        # daily usage 2: service env 2, value 60
        #
        # 2nd POST (same day, same usage type):
        # daily usage 1: service env 1, value 50
        #
        # final result:
        # daily usage 1: service env 1, value 40
        # daily usage 2: service env 2, value 60
        # daily usage 3: service env 1, value 50
        #
        # Nothing gets deleted/replaced, new daily usage should be added to the
        # existing ones, despite the fact that it has the same service
        # environment as the one from the 1st POST.
        #
        # Please note that service environment is given here implicitly, via
        # pricing object.

        pricing_service_usage_1st_post = {
            "pricing_service": self.pricing_service.name,
            "date": "2016-09-08",
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 40,
                        },
                    ],
                },
                {
                    "pricing_object": self.pricing_object2.name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 60,
                        },
                    ]
                }
            ]
        }
        pricing_service_usage_2nd_post = {
            "pricing_service": self.pricing_service.name,
            "date": "2016-09-08",
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 50,
                        },
                    ],
                },
            ]
        }

        # 1st POST
        self.assertEquals(DailyUsage.objects.all().count(), 0)
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage_1st_post),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        daily_usages = DailyUsage.objects.order_by('id')
        self.assertEquals(daily_usages.count(), 2)
        self.assertEquals(
            daily_usages[0].service_environment,
            self.service_environment1
        )
        self.assertEquals(
            daily_usages[1].service_environment,
            self.service_environment2
        )
        self.assertEquals(daily_usages[0].date, self.date)
        self.assertEquals(daily_usages[1].date, self.date)
        self.assertEquals(daily_usages[0].type, self.usage_type1)
        self.assertEquals(daily_usages[1].type, self.usage_type1)
        self.assertEquals(daily_usages[0].value, 40)
        self.assertEquals(daily_usages[1].value, 60)

        # 2nd POST
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage_2nd_post),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        daily_usages = DailyUsage.objects.order_by('id')
        self.assertEquals(daily_usages.count(), 3)
        self.assertEquals(
            daily_usages[0].service_environment,
            self.service_environment1
        )
        self.assertEquals(
            daily_usages[1].service_environment,
            self.service_environment2
        )
        self.assertEquals(
            daily_usages[2].service_environment,
            self.service_environment1
        )
        self.assertEquals(daily_usages[0].date, self.date)
        self.assertEquals(daily_usages[1].date, self.date)
        self.assertEquals(daily_usages[2].date, self.date)
        self.assertEquals(daily_usages[0].type, self.usage_type1)
        self.assertEquals(daily_usages[1].type, self.usage_type1)
        self.assertEquals(daily_usages[2].type, self.usage_type1)
        self.assertEquals(daily_usages[0].value, 40)
        self.assertEquals(daily_usages[1].value, 60)
        self.assertEquals(daily_usages[2].value, 50)


    def test_overwrite_delete_all_previous(self):
        # 1st POST (same day, same usage type):
        # daily usage 1: service env 1, value 40
        # daily usage 2: service env 2, value 60
        #
        # 2nd POST (same day, same usage type):
        # daily usage 1: service env 1, value 50
        #
        # final result:
        # daily usage 1: service env 1, value 50
        #
        # All daily usages from the same day, with the same usage type should
        # be deleted - only usages from the 2nd POST should remain, despite
        # the fact that 1st POST contained daily usage for different service
        # environment than the 2nd one.
        #
        # Please note that service environment is given here implicitly, via
        # pricing object.

        pricing_service_usage_1st_post = {
            "pricing_service": self.pricing_service.name,
            "date": "2016-09-08",
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 40,
                        },
                    ],
                },
                {
                    "pricing_object": self.pricing_object2.name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 60,
                        },
                    ]
                }
            ]
        }
        pricing_service_usage_2nd_post = {
            "pricing_service": self.pricing_service.name,
            "overwrite": "delete_all_previous",
            "date": "2016-09-08",
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 50,
                        },
                    ],
                },
            ]
        }

        # 1st POST
        self.assertEquals(DailyUsage.objects.all().count(), 0)
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage_1st_post),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        daily_usages = DailyUsage.objects.order_by('id')
        self.assertEquals(daily_usages.count(), 2)
        self.assertEquals(
            daily_usages[0].service_environment,
            self.service_environment1
        )
        self.assertEquals(
            daily_usages[1].service_environment,
            self.service_environment2
        )
        self.assertEquals(daily_usages[0].date, self.date)
        self.assertEquals(daily_usages[1].date, self.date)
        self.assertEquals(daily_usages[0].type, self.usage_type1)
        self.assertEquals(daily_usages[1].type, self.usage_type1)
        self.assertEquals(daily_usages[0].value, 40)
        self.assertEquals(daily_usages[1].value, 60)

        # 2nd POST
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage_2nd_post),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        daily_usages = DailyUsage.objects.all()
        self.assertEquals(daily_usages.count(), 1)
        self.assertEquals(
            daily_usages[0].service_environment,
            self.service_environment1
        )
        self.assertEquals(daily_usages[0].date, self.date)
        self.assertEquals(daily_usages[0].type, self.usage_type1)
        self.assertEquals(daily_usages[0].value, 50)


    def test_overwrite_values_only(self):
        # 1st POST (same day, same usage type):
        # daily usage 1: service env 1, value 40
        # daily usage 2: service env 2, value 60
        #
        # 2nd POST (same day, same usage type):
        # daily usage 1: service env 1, value 50
        #
        # final result:
        # daily usage 1: service env 2, value 60
        # daily usage 2: service env 1, value 50
        #
        # All daily usages from the same day, with the same usage type *and
        # the same service environment* should be replaced by the new daily
        # usage - the one with different service environment should remain
        # untouched.
        #
        # Please note that service environment is given here implicitly, via
        # pricing object.

        pricing_service_usage_1st_post = {
            "pricing_service": self.pricing_service.name,
            "date": "2016-09-08",
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 40,
                        },
                    ],
                },
                {
                    "pricing_object": self.pricing_object2.name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 60,
                        },
                    ]
                }
            ]
        }
        pricing_service_usage_2nd_post = {
            "pricing_service": self.pricing_service.name,
            "overwrite": "values_only",
            "date": "2016-09-08",
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 50,
                        },
                    ],
                },
            ]
        }

        # 1st POST
        self.assertEquals(DailyUsage.objects.all().count(), 0)
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage_1st_post),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        daily_usages = DailyUsage.objects.order_by('id')
        self.assertEquals(daily_usages.count(), 2)
        self.assertEquals(
            daily_usages[0].service_environment,
            self.service_environment1
        )
        self.assertEquals(
            daily_usages[1].service_environment,
            self.service_environment2
        )
        self.assertEquals(daily_usages[0].date, self.date)
        self.assertEquals(daily_usages[1].date, self.date)
        self.assertEquals(daily_usages[0].type, self.usage_type1)
        self.assertEquals(daily_usages[1].type, self.usage_type1)
        self.assertEquals(daily_usages[0].value, 40)
        self.assertEquals(daily_usages[1].value, 60)

        # 2nd POST
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage_2nd_post),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        daily_usages = DailyUsage.objects.order_by('id')
        self.assertEquals(daily_usages.count(), 2)
        self.assertEquals(
            daily_usages[0].service_environment,
            self.service_environment2
        )
        self.assertEquals(
            daily_usages[1].service_environment,
            self.service_environment1
        )
        self.assertEquals(daily_usages[0].date, self.date)
        self.assertEquals(daily_usages[1].date, self.date)
        self.assertEquals(daily_usages[0].type, self.usage_type1)
        self.assertEquals(daily_usages[1].type, self.usage_type1)
        self.assertEquals(daily_usages[0].value, 60)
        self.assertEquals(daily_usages[1].value, 50)


    # def test_get_pricing_service_usages(self):
    #     pass
