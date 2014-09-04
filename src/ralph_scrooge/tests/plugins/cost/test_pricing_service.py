# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from dateutil import rrule
from decimal import Decimal as D

from django.test import TestCase

from ralph_scrooge import models
from ralph_scrooge.plugins.cost.pricing_service import PricingServicePlugin
from ralph_scrooge.tests.plugins.cost.sample.pricing_service_costs import (
    PRICING_SERVICE_COSTS,
)
from ralph_scrooge.tests.utils.factory import (
    DailyUsageFactory,
    DailyPricingObjectFactory,
    ExtraCostTypeFactory,
    PricingServiceFactory,
    ServiceEnvironmentFactory,
    TeamFactory,
    UsageTypeFactory,
)


class TestPricingServicePlugin(TestCase):
    def setUp(self):
        self.today = date(2013, 10, 10)
        self.start = date(2013, 10, 1)
        self.end = date(2013, 10, 30)

        # TODO: unify with usages generator

        # base usages
        self.base_usage_type = UsageTypeFactory(
            usage_type='BU',
            by_cost=True,
        )

        # regular usage
        self.regular_usage_type = UsageTypeFactory(
            usage_type='RU',
            by_cost=False,
        )

        # team
        self.team = TeamFactory()

        # extra cost
        self.extra_cost_type = ExtraCostTypeFactory()

        # pricing services
        self.pricing_service1 = PricingServiceFactory()
        self.pricing_service1.regular_usage_types.add(self.regular_usage_type)
        self.pricing_service1.save()

        # NOTICE THAT PRICING SERVICE 2 IS NOT CHARGED FOR REGULAR USAGE
        self.pricing_service2 = PricingServiceFactory()

        # services
        self.service_environments = ServiceEnvironmentFactory.create_batch(
            2,
            service__pricing_service=self.pricing_service1,
        )
        self.service_environments.append(ServiceEnvironmentFactory.create(
            service__pricing_service=self.pricing_service2,
        ))
        self.service_environments.extend(
            ServiceEnvironmentFactory.create_batch(3)
        )

        # pricing service usages
        self.service_usage_types = UsageTypeFactory.create_batch(
            3,
            usage_type='SU',
        )
        models.ServiceUsageTypes.objects.create(
            usage_type=self.service_usage_types[0],
            pricing_service=self.pricing_service1,
            start=self.start,
            end=self.end,
            percent=30,
        )
        models.ServiceUsageTypes.objects.create(
            usage_type=self.service_usage_types[1],
            pricing_service=self.pricing_service1,
            start=self.start,
            end=self.end,
            percent=70,
        )
        models.ServiceUsageTypes.objects.create(
            usage_type=self.service_usage_types[2],
            pricing_service=self.pricing_service2,
            start=self.start,
            end=self.end,
            percent=100,
        )

        # daily pricing objects
        # in pricing service 1 (& use pricing service 2)
        self.se1_dpo = DailyPricingObjectFactory.create_batch(
            2,
            service_environment=self.service_environments[0]
        )
        self.se2_dpo = DailyPricingObjectFactory.create_batch(
            2,
            service_environment=self.service_environments[1]
        )
        # in pricing service 2
        self.se3_dpo = DailyPricingObjectFactory.create_batch(
            2,
            service_environment=self.service_environments[2]
        )
        # use pricing service 1
        self.se4_dpo = DailyPricingObjectFactory.create_batch(
            2,
            service_environment=self.service_environments[3]
        )
        self.se5_dpo = DailyPricingObjectFactory.create_batch(
            2,
            service_environment=self.service_environments[4]
        )
        # use pricing service 2 (besides se1_dpo and se2_dpo)
        self.se6_dpo = DailyPricingObjectFactory.create_batch(
            2,
            service_environment=self.service_environments[5]
        )
        # other
        self.se7_dpo = DailyPricingObjectFactory.create_batch(
            2,
            service_environment=self.service_environments[5]
        )

        # SO FAR SUMMARY:
        # there are 2 pricing services:
        # pricing service 1: collect costs from 2 services (4 pricing objects:
        # se1_dpo and se2_dpo); is distributed according to usages of 2 service
        # usage types: sut[0] (30%) and sut[1] (70%)
        # pricing service 2: collect costs from 1 service (2 pricing objects:
        # se3_dpo); is distributed according to usages of 1 service usage type
        # (sut[2] -  100%)
        # there are also another 2 service environments (each has 2 pricing
        # objects)

        # USAGES
        # base usage type
        models.UsagePrice(
            type=self.base_usage_type,
            cost=4200,  # daily cost: 1
            forecast_cost=8400,  # daily cost: 2
            start=self.start,
            end=self.end,
        ).save()
        # regular usage type
        models.UsagePrice(
            type=self.regular_usage_type,
            price=10,
            forecast_price=20,
            start=self.start,
            end=self.end,
        ).save()
        days = rrule.rrule(rrule.DAILY, dtstart=self.start, until=self.end)
        for day in days:
            # TODO: fix assigning DPO with wrong date to DailyUsage
            for dpo in models.DailyPricingObject.objects.all():
                DailyUsageFactory(
                    date=day,
                    daily_pricing_object=dpo,
                    service_environment=dpo.service_environment,
                    value=10,
                    type=self.base_usage_type,
                )
                DailyUsageFactory(
                    date=day,
                    daily_pricing_object=dpo,
                    service_environment=dpo.service_environment,
                    value=5,
                    type=self.regular_usage_type,
                )

        # team
        team_cost = models.TeamCost(
            team=self.team,
            cost=300,  # daily cost: 10
            forecast_cost=600,  # daily cost: 20
            start=self.start,
            end=self.end,
        )
        team_cost.save()
        for se in self.service_environments[:5]:
            models.TeamServiceEnvironmentPercent(
                team_cost=team_cost,
                service_environment=se,
                percent=20,  # 2 per day per se
            ).save()

        # extra cost
        for se in self.service_environments[:5]:
            models.ExtraCost(
                extra_cost_type=self.extra_cost_type,
                start=self.start,
                end=self.end,
                service_environment=se,
                cost=3000,  # daily cost: 100
                forecast_cost=6000,  # daily cost: 200
            ).save()

        # pricing service 1 service usage types usages
        for dpo, multiplier in zip(self.se4_dpo + self.se5_dpo, [1, 1, 3, 3]):
            days = rrule.rrule(rrule.DAILY, dtstart=self.start, until=self.end)
            for day in days:
                DailyUsageFactory(
                    type=self.service_usage_types[0],
                    daily_pricing_object=dpo,
                    service_environment=dpo.service_environment,
                    value=10 * multiplier,
                    date=day,
                )
                DailyUsageFactory(
                    type=self.service_usage_types[1],
                    daily_pricing_object=dpo,
                    service_environment=dpo.service_environment,
                    value=50 * multiplier,
                    date=day,
                )

        # pricing service 2 service usage types usages
        for dpo in self.se1_dpo + self.se2_dpo + self.se6_dpo:
            days = rrule.rrule(rrule.DAILY, dtstart=self.start, until=self.end)
            for day in days:
                DailyUsageFactory(
                    type=self.service_usage_types[2],
                    daily_pricing_object=dpo,
                    service_environment=dpo.service_environment,
                    value=100,
                    date=day,
                )

    def test_get_service_base_usage_types_cost(self):
        result = PricingServicePlugin._get_service_base_usage_types_cost(
            self.today,
            pricing_service=self.pricing_service1,
            forecast=False,
            service_environments=self.pricing_service1.service_environments,
        )
        self.assertEquals(result, {self.base_usage_type.id: (D('40'), {})})

    def test_get_service_regular_usage_types_cost(self):
        result = PricingServicePlugin._get_service_regular_usage_types_cost(
            self.today,
            pricing_service=self.pricing_service1,
            forecast=False,
            service_environments=self.pricing_service1.service_environments,
        )
        self.assertEquals(result, {self.regular_usage_type.id: (D('200'), {})})

    def test_get_service_teams_cost(self):
        result = PricingServicePlugin._get_service_teams_cost(
            self.today,
            forecast=False,
            service_environments=self.pricing_service1.service_environments,
        )
        self.assertEquals(result, {self.team.id: (D('4'), {})})

    def test_get_service_extra_cost(self):
        result = PricingServicePlugin._get_service_extra_cost(
            self.today,
            forecast=False,
            service_environments=self.pricing_service1.service_environments,
        )
        self.assertEquals(result, {self.extra_cost_type.id: (D('200'), {})})

    def test_get_dependent_services_cost(self):
        result = PricingServicePlugin._get_dependent_services_cost(
            self.today,
            pricing_service=self.pricing_service1,
            forecast=False,
            service_environments=self.pricing_service1.service_environments,
        )
        self.assertEquals(result, {
            self.pricing_service2.id: [
                D('122'),
                {
                    self.base_usage_type.id: [D('20'), {}],
                    self.team.id: [D('2.00'), {}],
                    self.extra_cost_type.id: [D('100'), {}]
                }
            ]
        })

    def test_get_pricing_service_costs(self):
        costs = PricingServicePlugin._get_pricing_service_costs(
            date=self.today,
            pricing_service=self.pricing_service1,
            forecast=False,
            service_environments=self.pricing_service1.service_environments,
        )
        self.assertEquals(costs, {
            self.pricing_service1.id: (
                D('566'),
                {
                    self.base_usage_type.id: (D('40'), {}),
                    self.regular_usage_type.id: (D('200'), {}),
                    self.team.id: (D('4'), {}),
                    self.extra_cost_type.id: (D('200'), {}),
                    self.pricing_service2.id: [
                        D('122'),
                        {
                            self.base_usage_type.id: [D('20'), {}],
                            self.team.id: [D('2.00'), {}],
                            self.extra_cost_type.id: [D('100'), {}]
                        }
                    ]
                }
            )
        })

    def test_get_total_costs_from_costs(self):
        result = PricingServicePlugin._get_total_costs_from_costs(
            PRICING_SERVICE_COSTS
        )
        self.assertEquals(result, {
            1: [
                D(5100),
                {
                    2: [D(1800), {}],
                    3: [D(1600), {}],
                    4: [D(900), {}],
                    5: [D(800), {}],
                }
            ],
            6: [
                D(300),
                {
                    2: [D(100), {}],
                    3: [D(200), {}],
                }
            ]
        })

    # TODO: add tests for _distribute_costs

    def test_costs(self):
        costs = PricingServicePlugin(
            type='costs',
            date=self.today,
            pricing_service=self.pricing_service1,
            service_environments=self.service_environments,
            forecast=True,
        )
        po1 = self.se4_dpo[0].pricing_object.id
        po2 = self.se4_dpo[1].pricing_object.id
        po3 = self.se5_dpo[0].pricing_object.id
        po4 = self.se5_dpo[1].pricing_object.id
        self.assertEquals(costs, {
            self.service_environments[3].id: [
                {
                    'cost': D('141.5'),
                    'pricing_object_id': po1,
                    'type_id': self.pricing_service1.id,
                    '_children': [
                        {
                            'cost': D('10'),
                            'pricing_object_id': po1,
                            'type_id': self.base_usage_type.id,
                        },
                        {
                            'cost': D('50'),
                            'pricing_object_id': po1,
                            'type_id': self.regular_usage_type.id,
                        },
                        {
                            'cost': D('1'),
                            'pricing_object_id': po1,
                            'type_id': self.team.id,
                        },
                        {
                            'cost': D('50'),
                            'pricing_object_id': po1,
                            'type_id': self.extra_cost_type.id,
                        },
                        {
                            'cost': D('30.5'),
                            'pricing_object_id': po1,
                            'type_id': self.pricing_service2.id,
                            '_children': [
                                {
                                    'cost': D('5'),
                                    'pricing_object_id': po1,
                                    'type_id': self.base_usage_type.id,
                                },
                                {
                                    'cost': D('0.5'),
                                    'pricing_object_id': po1,
                                    'type_id': self.team.id,
                                },
                                {
                                    'cost': D('25'),
                                    'pricing_object_id': po1,
                                    'type_id': self.extra_cost_type.id,
                                }
                            ],
                        },
                    ],
                },
                {
                    'cost': D('141.5'),
                    'pricing_object_id': po2,
                    'type_id': self.pricing_service1.id,
                    '_children': [
                        {
                            'cost': D('10'),
                            'pricing_object_id': po2,
                            'type_id': self.base_usage_type.id,
                        },
                        {
                            'cost': D('50'),
                            'pricing_object_id': po2,
                            'type_id': self.regular_usage_type.id,
                        },
                        {
                            'cost': D('1'),
                            'pricing_object_id': po2,
                            'type_id': self.team.id,
                        },
                        {
                            'cost': D('50'),
                            'pricing_object_id': po2,
                            'type_id': self.extra_cost_type.id,
                        },
                        {
                            'cost': D('30.5'),
                            'pricing_object_id': po2,
                            'type_id': self.pricing_service2.id,
                            '_children': [
                                {
                                    'cost': D('5'),
                                    'pricing_object_id': po2,
                                    'type_id': self.base_usage_type.id,
                                },
                                {
                                    'cost': D('0.5'),
                                    'pricing_object_id': po2,
                                    'type_id': self.team.id,
                                },
                                {
                                    'cost': D('25'),
                                    'pricing_object_id': po2,
                                    'type_id': self.extra_cost_type.id,
                                }
                            ],
                        },
                    ],
                },
            ],
            self.service_environments[4].id: [
                {
                    'cost': D('424.5'),
                    'pricing_object_id': po3,
                    'type_id': self.pricing_service1.id,
                    '_children': [
                        {
                            'cost': D('30'),
                            'pricing_object_id': po3,
                            'type_id': self.base_usage_type.id
                        },
                        {
                            'cost': D('150'),
                            'pricing_object_id': po3,
                            'type_id': self.regular_usage_type.id,
                        },
                        {
                            'cost': D('3'),
                            'pricing_object_id': po3,
                            'type_id': self.team.id,
                        },
                        {
                            'cost': D('150'),
                            'pricing_object_id': po3,
                            'type_id': self.extra_cost_type.id,
                        },
                        {
                            'cost': D('91.5'),
                            'pricing_object_id': po3,
                            'type_id': self.pricing_service2.id,
                            '_children': [
                                {
                                    'cost': D('15'),
                                    'pricing_object_id': po3,
                                    'type_id': self.base_usage_type.id,
                                },
                                {
                                    'cost': D('1.5'),
                                    'pricing_object_id': po3,
                                    'type_id': self.team.id,
                                },
                                {
                                    'cost': D('75'),
                                    'pricing_object_id': po3,
                                    'type_id': self.extra_cost_type.id,
                                }
                            ],
                        }
                    ]
                },
                {
                    'cost': D('424.5'),
                    'pricing_object_id': po4,
                    'type_id': self.pricing_service1.id,
                    '_children': [
                        {
                            'cost': D('30'),
                            'pricing_object_id': po4,
                            'type_id': self.base_usage_type.id
                        },
                        {
                            'cost': D('150'),
                            'pricing_object_id': po4,
                            'type_id': self.regular_usage_type.id,
                        },
                        {
                            'cost': D('3'),
                            'pricing_object_id': po4,
                            'type_id': self.team.id,
                        },
                        {
                            'cost': D('150'),
                            'pricing_object_id': po4,
                            'type_id': self.extra_cost_type.id,
                        },
                        {
                            'cost': D('91.5'),
                            'pricing_object_id': po4,
                            'type_id': self.pricing_service2.id,
                            '_children': [
                                {
                                    'cost': D('15'),
                                    'pricing_object_id': po4,
                                    'type_id': self.base_usage_type.id,
                                },
                                {
                                    'cost': D('1.5'),
                                    'pricing_object_id': po4,
                                    'type_id': self.team.id,
                                },
                                {
                                    'cost': D('75'),
                                    'pricing_object_id': po4,
                                    'type_id': self.extra_cost_type.id,
                                }
                            ],
                        }
                    ]
                },
            ]
        })
