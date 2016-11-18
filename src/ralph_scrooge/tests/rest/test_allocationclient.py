# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils import factory
from ralph_scrooge import models


class TestAllocationClient(ScroogeTestCase):

    def setUp(self):
        get_user_model().objects.create_superuser(
            'test', 'test@test.test', 'test'
        )
        self.client = APIClient()
        self.client.login(username='test', password='test')

        self.date = datetime.date(year=2014, month=12, day=1)

    def _create_daily_usage(self, usage_type, daily_pricing_object):
        service_environment = factory.ServiceEnvironmentFactory()
        pricing_service = factory.PricingServiceFactory()
        pricing_service.services.add(service_environment.service)
        return service_environment, factory.DailyUsageFactory(
            date=self.date,
            service_environment=service_environment,
            daily_pricing_object=daily_pricing_object,
            type=usage_type,
        )

    def _init_service_division(self, forecast=False):
        self.service_environment_base = factory.ServiceEnvironmentFactory()
        self.pricing_service = factory.PricingServiceFactory()
        self.pricing_service.services.add(
            self.service_environment_base.service
        )
        self.pricing_service.save()
        self.service_usage_type = factory.ServiceUsageTypesFactory(
            usage_type=factory.UsageTypeFactory(),
            pricing_service=self.pricing_service,
        )
        pricing_object = self.service_environment_base.pricing_objects.get(
            type_id=models.PRICING_OBJECT_TYPES.DUMMY
        )
        daily_pricing_object = factory.DailyPricingObjectFactory(
            service_environment=self.service_environment_base,
            date=self.date,
            pricing_object=pricing_object,
        )
        pricing_object.daily_pricing_object = daily_pricing_object
        self.service_environment_1, self.daily_usage1 = (
            self._create_daily_usage(
                self.service_usage_type.usage_type,
                daily_pricing_object,
            )
        )
        self.service_environment_2, self.daily_usage2 = (
            self._create_daily_usage(
                self.service_usage_type.usage_type,
                daily_pricing_object,
            )
        )

    def _create_extra_cost(self, service_environment):
        return factory.ExtraCostFactory(
            start=self.date,
            end=self.date + datetime.timedelta(days=30),
            service_environment=service_environment,
            extra_cost_type=models.ExtraCostType.objects_admin.get(id=1),
        )

    def _create_team_division(self, service_environment, team):
        return factory.TeamServiceEnvironmentPercentFactory(
            team_cost=factory.TeamCostFactory(
                team=team,
                start=self.date,
                end=self.date + datetime.timedelta(days=30),
            ),
            service_environment=service_environment
        )

    def test_get_service_division_when_there_is_no_usages(self):
        service_environment_base = factory.ServiceEnvironmentFactory()
        usage_types_before_request = models.UsageType.objects.count()
        response = self.client.get(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/{3}/'.format(
                service_environment_base.service.id,
                service_environment_base.environment.id,
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['serviceDivision'],
            {
                "rows": [],
                "name": "Service Division",
                "template": "taballocationclientdivision.html",
            }
        )
        # check if get request does not create new usage type
        self.assertEqual(
            models.UsageType.objects.count(),
            usage_types_before_request
        )

    def test_get_service_division_when_there_are_two_daily_usages(self):
        self._init_service_division()
        response = self.client.get(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/{3}/'.format(
                self.service_environment_base.service.id,
                self.service_environment_base.environment.id,
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['serviceDivision'],
            {
                "rows": [{
                    "value": float(self.daily_usage1.value),
                    "env": self.service_environment_1.environment.id,
                    "service": self.service_environment_1.service.id
                }, {
                    "value": float(self.daily_usage2.value),
                    "env": self.service_environment_2.environment.id,
                    "service": self.service_environment_2.service.id
                }],
                "name": "Service Division",
                "template": "taballocationclientdivision.html",
            }
        )

    def test_get_service_division_with_different_service_usage_date(self):
        self._init_service_division()
        self.service_usage_type.end = self.date - relativedelta(months=1)
        self.service_usage_type.save()
        usage_types_before_request = models.UsageType.objects.count()
        response = self.client.get(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/{3}/'.format(
                self.service_environment_base.service.id,
                self.service_environment_base.environment.id,
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['serviceDivision'],
            {
                "rows": [],
                "name": "Service Division",
                "template": "taballocationclientdivision.html",
            }
        )
        # check if get request does not create new usage type
        self.assertEqual(
            models.UsageType.objects.count(),
            usage_types_before_request
        )

    def test_save_service_division(self):
        service_environment_base = factory.ServiceEnvironmentFactory()
        service_environment_1 = factory.ServiceEnvironmentFactory()
        response = self.client.post(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/{3}/{4}/save/'.format(
                service_environment_base.service.id,
                service_environment_base.environment.id,
                self.date.year,
                self.date.month,
                'servicedivision'
            ),
            {
                'rows': [{
                    "service": service_environment_1.service.id,
                    "env": service_environment_1.environment.id,
                    "value": 100,
                }]
            },
            format='json'
        )
        response = self.client.get(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/{3}/'.format(
                service_environment_base.service.id,
                service_environment_base.environment.id,
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['serviceDivision'],
            {
                "rows": [{
                    "value": 100.0,
                    "env": service_environment_1.environment.id,
                    "service": service_environment_1.service.id
                }],
                "name": "Service Division",
                "template": "taballocationclientdivision.html",
            }
        )

    def test_save_service_division_with_different_service_usage_date(self):
        service_environment_1 = factory.ServiceEnvironmentFactory()
        self._init_service_division()
        self.service_usage_type.end = self.date - relativedelta(months=1)
        self.service_usage_type.save()
        usage_types_before_request = models.UsageType.objects.count()
        service_usage_types_before_request = (
            models.ServiceUsageTypes.objects.count()
        )
        response = self.client.post(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/{3}/{4}/save/'.format(
                self.service_environment_base.service.id,
                self.service_environment_base.environment.id,
                self.date.year,
                self.date.month,
                'servicedivision'
            ),
            {
                'rows': [{
                    "service": service_environment_1.service.id,
                    "env": service_environment_1.environment.id,
                    "value": 100,
                }]
            },
            format='json'
        )
        response = self.client.get(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/{3}/'.format(
                self.service_environment_base.service.id,
                self.service_environment_base.environment.id,
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['serviceDivision'],
            {
                "rows": [{
                    "value": 100.0,
                    "env": service_environment_1.environment.id,
                    "service": service_environment_1.service.id
                }],
                "name": "Service Division",
                "template": "taballocationclientdivision.html",
            }
        )
        # check if this request created new usage type and created
        # new service usage type with valid dates
        self.assertEqual(
            models.UsageType.objects.count(),
            usage_types_before_request + 1
        )
        self.assertEqual(
            models.ServiceUsageTypes.objects.count(),
            service_usage_types_before_request + 1
        )
        self.assertEqual(
            set(self.pricing_service.serviceusagetypes_set.values_list(
                'start',
                'end'
            )),
            set([
                (datetime.date.min, self.date - relativedelta(months=1)),
                (
                    self.date - relativedelta(months=1) + timedelta(days=1),
                    datetime.date.max
                ),
            ])
        )

    def test_get_extra_costs_when_there_is_no_extra_costs(self):
        service_environment_base = factory.ServiceEnvironmentFactory()
        response = self.client.get(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/{3}/'.format(
                service_environment_base.service.id,
                service_environment_base.environment.id,
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['serviceExtraCost'],
            {
                "rows": [],
                "name": "Extra Cost",
                "template": "tabextracosts.html",
            }
        )

    def test_get_extra_costs_when_there_are_two_extra_costs(self):
        service_environment_base = factory.ServiceEnvironmentFactory()
        extra_cost1 = self._create_extra_cost(service_environment_base)
        extra_cost2 = self._create_extra_cost(service_environment_base)
        response = self.client.get(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/{3}/'.format(
                service_environment_base.service.id,
                service_environment_base.environment.id,
                self.date.year,
                self.date.month,
            )
        )

        self.assertEquals(
            json.loads(response.content)['serviceExtraCost'],
            {
                "rows": [{
                    "remarks": extra_cost1.remarks,
                    "id": extra_cost1.id,
                    "value": float(extra_cost1.cost),
                }, {
                    "remarks": extra_cost2.remarks,
                    "id": extra_cost2.id,
                    "value": float(extra_cost2.cost),
                }],
                "name": "Extra Cost",
                "template": "tabextracosts.html",
            }
        )

    def test_save_extra_cost(self):
        service_environment_base = factory.ServiceEnvironmentFactory()
        response = self.client.post(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/{3}/{4}/save/'.format(
                service_environment_base.service.id,
                service_environment_base.environment.id,
                self.date.year,
                self.date.month,
                'serviceextracost'
            ),
            {
                'rows': [{
                    "remarks": "test remarks",
                    "value": 100,
                }]
            },
            format='json'
        )
        response = self.client.get(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/{3}/'.format(
                service_environment_base.service.id,
                service_environment_base.environment.id,
                self.date.year,
                self.date.month,
            )
        )

        extra_cost = models.ExtraCost.objects.all()
        self.assertEquals(extra_cost.count(), 1)
        self.assertEquals(
            json.loads(response.content)['serviceExtraCost'],
            {
                "rows": [{
                    "remarks": "test remarks",
                    "value": extra_cost[0].cost,
                    "id": extra_cost[0].id,
                }],
                "name": "Extra Cost",
                "template": "tabextracosts.html",
            }
        )

    def test_get_team_division_when_there_is_no_team_divisions(self):
        team_base = factory.TeamFactory()
        response = self.client.get(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/'.format(
                team_base.id,
                self.date.year,
                self.date.month,
            )
        )
        self.assertEquals(
            json.loads(response.content)['teamDivision'],
            {
                "rows": [],
                "name": "Team Division",
                "template": "taballocationclientdivision.html",
            }
        )

    def test_save_team_division(self):
        team_base = factory.TeamFactory()
        service_environment = factory.ServiceEnvironmentFactory()
        response = self.client.post(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/{3}/save/'.format(
                team_base.id,
                self.date.year,
                self.date.month,
                'teamdivision'
            ),
            {
                'rows': [{
                    "service": service_environment.service.id,
                    "env": service_environment.environment.id,
                    "value": 100,
                }]
            },
            format='json'
        )
        response = self.client.get(
            '/scrooge/rest/allocationclient/{0}/{1}/{2}/'.format(
                team_base.id,
                self.date.year,
                self.date.month,
            )
        )
        team_division = models.TeamServiceEnvironmentPercent.objects.all()
        self.assertEquals(team_division.count(), 1)
        self.assertEquals(
            json.loads(response.content)['teamDivision'],
            {
                "rows": [{
                    "value": team_division[0].percent,
                    "id": team_division[0].id,
                    "service": (
                        team_division[0].service_environment.service.id
                    ),
                    "env": (
                        team_division[0].service_environment.environment.id
                    )
                }],
                "name": "Team Division",
                "template": "taballocationclientdivision.html",
            }
        )
