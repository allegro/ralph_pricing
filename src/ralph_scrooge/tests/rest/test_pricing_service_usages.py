# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from rest_framework.test import APIClient

from ralph_scrooge.models import (
    DailyUsage,
    Environment,
    PricingService,
    Service,
    ServiceUsageTypes,
    UsageType,
)
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import (
    DailyUsageFactory,
    PricingObjectFactory,
    PricingServiceFactory,
    UsageTypeFactory,
)


class TestPricingServiceUsages(ScroogeTestCase):

    def setUp(self):
        self.date = datetime.date(2016, 9, 8)
        self.date_as_str = self.date.strftime("%Y-%m-%d")
        self.pricing_service = PricingServiceFactory()
        self.pricing_object1 = PricingObjectFactory()
        self.pricing_object2 = PricingObjectFactory()
        self.service_environment1 = self.pricing_object1.service_environment
        self.service_environment2 = self.pricing_object2.service_environment
        self.usage_type = UsageTypeFactory()
        ServiceUsageTypes.objects.create(
            usage_type=self.usage_type,
            pricing_service=self.pricing_service,
            start=datetime.date(2016, 9, 1),
            end=datetime.date.max,
        )
        superuser = get_user_model().objects.create_superuser(
            'test', 'test@test.test', 'test'
        )
        self.client = APIClient()
        self.client.force_authenticate(superuser)

    def test_save_usages_successfully_when_pricing_object_is_given(self):
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertEquals(daily_usages[0].type, self.usage_type)
        self.assertEquals(daily_usages[0].value, 40)

    def test_save_usages_successfully_when_service_and_environment_is_given(self):  # noqa
        service_name = self.pricing_object1.service_environment.service.name
        environment_name = (
            self.pricing_object1.service_environment.environment.name
        )
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "service": service_name,
                    "environment": environment_name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertEquals(daily_usages[0].type, self.usage_type)
        self.assertEquals(daily_usages[0].value, 40)

    def test_save_usages_successfully_when_service_id_and_environment_is_given(self):  # noqa
        service_id = self.pricing_object1.service_environment.service_id
        environment_name = (
            self.pricing_object1.service_environment.environment.name
        )
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "service_id": service_id,
                    "environment": environment_name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertEquals(daily_usages[0].type, self.usage_type)
        self.assertEquals(daily_usages[0].value, 40)

    def test_save_usages_successfully_when_service_uid_and_environment_is_given(self):  # noqa
        service_uid = self.pricing_object1.service_environment.service.ci_uid
        environment_name = (
            self.pricing_object1.service_environment.environment.name
        )
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "service_uid": service_uid,
                    "environment": environment_name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertEquals(daily_usages[0].type, self.usage_type)
        self.assertEquals(daily_usages[0].value, 40)

    def test_for_error_when_non_existing_pricing_service_is_given(self):
        pricing_service_usage = {
            "pricing_service": 'fake_pricing_service',
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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

    def test_for_error_when_pricing_service_missing(self):
        pricing_service_usage = {
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertIn('This field is required', errors[0])

    def test_for_error_when_non_existing_service_is_given(self):
        non_existing_service = 'fake_service'
        self.assertFalse(
            Service.objects.filter(name=non_existing_service).exists()
        )
        environment_name = (
            self.pricing_object1.service_environment.environment.name
        )
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "service": non_existing_service,
                    "environment": environment_name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertIn(non_existing_service, errors[0])
        self.assertIn('does not exist', errors[0])

    def test_for_error_when_non_existing_service_id_is_given(self):
        non_existing_service_id = 9999
        self.assertFalse(
            Service.objects.filter(id=non_existing_service_id).exists()
        )
        environment_name = (
            self.pricing_object1.service_environment.environment.name
        )
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "service_id": non_existing_service_id,
                    "environment": environment_name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertIn(str(non_existing_service_id), errors[0])
        self.assertIn('does not exist', errors[0])

    def test_for_error_when_non_existing_service_uid_is_given(self):
        non_existing_service_uid = 'xx-123'
        self.assertFalse(
            Service.objects.filter(ci_uid=non_existing_service_uid).exists()
        )
        environment_name = (
            self.pricing_object1.service_environment.environment.name
        )
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "service_uid": non_existing_service_uid,
                    "environment": environment_name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertIn(non_existing_service_uid, errors[0])
        self.assertIn('does not exist', errors[0])

    def test_for_error_when_env_without_service_or_service_id_or_service_uid_is_given(self):  # noqa
        environment_name = (
            self.pricing_object1.service_environment.environment.name
        )
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "environment": environment_name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertIn('service', errors[0])
        self.assertIn('Invalid combination of fields', errors[0])

    def test_for_error_when_non_existing_environment_is_given(self):
        service_name = self.pricing_object1.service_environment.service.name
        non_existing_env = 'fake_env'
        self.assertFalse(
            Environment.objects.filter(name=non_existing_env).exists()
        )
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "service": service_name,
                    "environment": non_existing_env,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertIn(non_existing_env, errors[0])
        self.assertIn('does not exist', errors[0])

    def test_for_error_when_service_without_environment_is_given(self):
        service_name = self.pricing_object1.service_environment.service.name
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "service": service_name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertIn('service environment', errors[0])
        self.assertIn('does not exist', errors[0])

    def test_for_error_when_non_existing_usage_type_is_given(self):
        non_existing_usage_type = 'fake_usage_type'
        self.assertFalse(
            UsageType.objects.filter(symbol=non_existing_usage_type).exists()
        )
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": non_existing_usage_type,
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
        errors = json.loads(resp.content)['usages'][0]['usages'][0]['symbol']
        self.assertEquals(len(errors), 1)
        self.assertIn(non_existing_usage_type, errors[0])
        self.assertIn('does not exist', errors[0])

    def test_for_error_when_usages_are_missing(self):
        # "inner" usages
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                },
            ]
        }

        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        errors = json.loads(resp.content)['usages'][0]['usages']
        self.assertEquals(len(errors), 1)
        self.assertIn('This field is required', errors[0])

        # "outer" usages
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
        }

        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        errors = json.loads(resp.content)['usages']
        self.assertEquals(len(errors), 1)
        self.assertIn('This field is required', errors[0])

    def test_for_error_when_usages_are_empty_lists(self):
        # "inner" usages
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [],
                },
            ]
        }
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        errors = json.loads(resp.content)['usages'][0]['usages']
        self.assertEquals(len(errors), 1)
        self.assertIn('This field cannot be empty', errors[0])

        # "outer" usages
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [],
        }
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        errors = json.loads(resp.content)['usages']
        self.assertEquals(len(errors), 1)
        self.assertIn('This field cannot be empty', errors[0])

    def test_for_error_when_usages_are_none(self):
        # "inner" usages
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": None,
                },
            ]
        }
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        errors = json.loads(resp.content)['usages'][0]['usages']
        self.assertEquals(len(errors), 1)
        self.assertIn('This field may not be null', errors[0])

        # "outer" usages
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": None,
        }
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        errors = json.loads(resp.content)['usages']
        self.assertEquals(len(errors), 1)
        self.assertIn('This field may not be null', errors[0])

    def test_usages_are_appended_when_not_overwriting_by_default_opt_is_chosen(self):  # noqa
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
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 40,
                        },
                    ],
                },
                {
                    "pricing_object": self.pricing_object2.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 60,
                        },
                    ]
                }
            ]
        }
        pricing_service_usage_2nd_post = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertEquals(daily_usages[0].type, self.usage_type)
        self.assertEquals(daily_usages[1].type, self.usage_type)
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
        self.assertEquals(daily_usages[0].type, self.usage_type)
        self.assertEquals(daily_usages[1].type, self.usage_type)
        self.assertEquals(daily_usages[2].type, self.usage_type)
        self.assertEquals(daily_usages[0].value, 40)
        self.assertEquals(daily_usages[1].value, 60)
        self.assertEquals(daily_usages[2].value, 50)

    def test_usages_are_deleted_when_overwrite_delete_all_previous_opt_is_chosen(self):  # noqa
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
        # All previously uploaded daily usages from the same day, with
        # the same usage type should be deleted - only usages from the
        # 2nd POST should remain, despite the fact that 1st POST
        # contained daily usage for different service environment than
        # the 2nd one.
        #
        # Please note that service environment is given here implicitly, via
        # pricing object.

        pricing_service_usage_1st_post = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 40,
                        },
                    ],
                },
                {
                    "pricing_object": self.pricing_object2.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 60,
                        },
                    ]
                }
            ]
        }
        pricing_service_usage_2nd_post = {
            "pricing_service": self.pricing_service.name,
            "overwrite": "delete_all_previous",
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertEquals(daily_usages[0].type, self.usage_type)
        self.assertEquals(daily_usages[1].type, self.usage_type)
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
        self.assertEquals(daily_usages[0].type, self.usage_type)
        self.assertEquals(daily_usages[0].value, 50)

    def test_usages_are_replaced_when_overwrite_values_only_opt_is_chosen(self):  # noqa
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
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 40,
                        },
                    ],
                },
                {
                    "pricing_object": self.pricing_object2.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 60,
                        },
                    ]
                }
            ]
        }
        pricing_service_usage_2nd_post = {
            "pricing_service": self.pricing_service.name,
            "overwrite": "values_only",
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
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
        self.assertEquals(daily_usages[0].type, self.usage_type)
        self.assertEquals(daily_usages[1].type, self.usage_type)
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
        self.assertEquals(daily_usages[0].type, self.usage_type)
        self.assertEquals(daily_usages[1].type, self.usage_type)
        self.assertEquals(daily_usages[0].value, 60)
        self.assertEquals(daily_usages[1].value, 50)

    def test_posted_pricing_service_usage_is_the_same_when_fetched_with_get(self):  # noqa
        # create additional service usage time, invalid now (should not be
        # returned in get response)
        self.usage_type2 = UsageTypeFactory()
        ServiceUsageTypes.objects.create(
            usage_type=self.usage_type2,
            pricing_service=self.pricing_service,
            start=datetime.date.min,
            end=datetime.date(2016, 8, 31),
        )
        # create some daily usage for this invalid usage type
        DailyUsageFactory(
            daily_pricing_object=self.pricing_object1.get_daily_pricing_object(
                self.date
            ),
            type=self.usage_type2,
            date=self.date,
            value=10,
        )

        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 40,
                        },
                    ],
                },
                {
                    "pricing_object": self.pricing_object2.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 60,
                        },
                    ],
                },
            ]
        }

        env1 = self.pricing_object1.service_environment.environment.name
        service1 = self.pricing_object1.service_environment.service.name
        service1_id = self.pricing_object1.service_environment.service_id
        service1_uid = self.pricing_object1.service_environment.service.ci_uid

        env2 = self.pricing_object2.service_environment.environment.name
        service2 = self.pricing_object2.service_environment.service.name
        service2_id = self.pricing_object2.service_environment.service_id
        service2_uid = self.pricing_object2.service_environment.service.ci_uid

        expected_response = {
            "date": self.date_as_str,
            "pricing_service": self.pricing_service.name,
            "pricing_service_id": self.pricing_service.id,
            "usages": [
                {
                    "environment": env1,
                    "pricing_object": self.pricing_object1.name,
                    "service": service1,
                    "service_id": service1_id,
                    "service_uid": service1_uid,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 40.0,
                            "remarks": "",
                        }
                    ]
                },
                {
                    "environment": env2,
                    "pricing_object": self.pricing_object2.name,
                    "service": service2,
                    "service_id": service2_id,
                    "service_uid": service2_uid,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 60.0,
                            "remarks": "",
                        }
                    ]
                }
            ]
        }

        self.assertEquals(DailyUsage.objects.all().count(), 1)
        self.assertEquals(PricingService.objects.all().count(), 1)
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        self.assertEquals(DailyUsage.objects.all().count(), 3)
        self.assertEquals(PricingService.objects.all().count(), 1)

        url = reverse(
            'list_pricing_service_usages',
            kwargs={
                'pricing_service_id': PricingService.objects.all()[0].id,
                'usages_date': self.date_as_str,
            }
        )
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)
        received_response = json.loads(resp.content)
        usages = received_response['usages']
        self.assertEqual(len(usages), 2)
        self.assertNestedDictsEqual(expected_response, received_response)

        # check filtering by `service_id`
        url_with_filter = "{}?service_id={}".format(url, service1_id)
        resp = self.client.get(url_with_filter)
        self.assertEquals(resp.status_code, 200)
        received_response = json.loads(resp.content)
        usages = received_response['usages']
        self.assertEqual(len(usages), 1)
        self.assertEqual(usages[0]['service_id'], service1_id)

    def test_for_error_when_invalid_date_in_correct_format_given_in_URL(self):
        invalid_date = '2016-09-33'
        resp = self.client.get(
            reverse(
                'list_pricing_service_usages',
                kwargs={
                    'pricing_service_id': PricingService.objects.all()[0].id,
                    'usages_date': invalid_date,
                }
            )
        )
        self.assertEquals(resp.status_code, 400)
        self.assertIn(invalid_date, resp.content)
        self.assertIn("invalid date", resp.content)

    def test_save_usages_successfully_when_ignoring_unknown_services(self):
        service1_uid = self.pricing_object1.service_environment.service.ci_uid
        env1 = self.pricing_object1.service_environment.environment.name
        service2_uid = self.pricing_object2.service_environment.service.ci_uid
        env2 = self.pricing_object2.service_environment.environment.name
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "ignore_unknown_services": True,
            "usages": [
                {
                    "service_uid": service1_uid,
                    "environment": env1,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 40,
                        },
                    ],
                },
                {
                    "service_uid": 'unknown',
                    "environment": 'prod',
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 30,
                        },
                    ],
                },
                {
                    "service_uid": service2_uid,
                    "environment": env2,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 20,
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
        self.assertEquals(daily_usages.count(), 2)
        self.assertEquals(
            daily_usages[0].service_environment,
            self.service_environment1
        )
        self.assertEquals(daily_usages[0].date, self.date)
        self.assertEquals(daily_usages[0].type, self.usage_type)
        self.assertEquals(daily_usages[0].value, 40)
        self.assertEquals(
            daily_usages[1].service_environment,
            self.service_environment2
        )
        self.assertEquals(daily_usages[1].date, self.date)
        self.assertEquals(daily_usages[1].type, self.usage_type)
        self.assertEquals(daily_usages[1].value, 20)

    def test_remarks_are_saved_when_given_and_can_be_read_back_with_get(self):
        remarks = "some test remarks"
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 40,
                            "remarks": remarks
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
        self.assertEquals(daily_usages[0].remarks, remarks)

        resp = self.client.get(
            reverse(
                'list_pricing_service_usages',
                kwargs={
                    'pricing_service_id': PricingService.objects.all()[0].id,
                    'usages_date': self.date_as_str,
                }
            )
        )
        self.assertEquals(resp.status_code, 200)
        received_response = json.loads(resp.content)
        self.assertEquals(
            received_response['usages'][0]['usages'][0]['remarks'],
            remarks
        )

    def test_blank_remarks_are_saved(self):
        pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": self.date_as_str,
            "usages": [
                {
                    "pricing_object": self.pricing_object1.name,
                    "usages": [
                        {
                            "symbol": self.usage_type.symbol,
                            "value": 40,
                            "remarks": ''
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
        self.assertEquals(daily_usages[0].remarks, '')
