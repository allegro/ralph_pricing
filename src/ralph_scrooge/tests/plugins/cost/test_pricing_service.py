# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from dateutil import rrule
from decimal import Decimal as D
import mock

from django.test import TestCase
from django.test.utils import override_settings

from ralph_scrooge import models
from ralph_scrooge.plugins.cost.pricing_service import PricingServicePlugin
from ralph_scrooge.plugins.cost.pricing_service_fixed_price import (
    PricingServiceFixedPricePlugin
)
from ralph_scrooge.tests import ScroogeTestCase
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
        self.maxDiff = None
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
        # TOTAL DAILY PRICING OBJECTS: 14

        # USAGES
        # base usage type
        models.UsagePrice(
            type=self.base_usage_type,
            # cost per unit: 1, daily cost (usages are the same for each date):
            # 140, cost per daily pricing object: 10
            cost=4200,
            forecast_cost=8400,  # cost per unit: 2
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
        for dpo in self.se1_dpo + self.se6_dpo:
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

    @override_settings(SAVE_ONLY_FIRST_DEPTH_COSTS=False)
    def test_get_dependent_services_cost(self):
        result = PricingServicePlugin._get_dependent_services_cost(
            self.today,
            pricing_service=self.pricing_service1,
            forecast=False,
            service_environments=self.pricing_service1.service_environments,
        )
        # daily pricing objects which are under pricing service 1 (practically
        # under se1) are using extacly half of pricing service resources, so
        # they will be charged with half of total amount
        self.assertEquals(result, {
            self.pricing_service2.id: [
                D('61'),
                {
                    self.base_usage_type.id: [D('10'), {}],
                    self.team.id: [D('1'), {}],
                    self.extra_cost_type.id: [D('50'), {}]
                }
            ]
        })

    @override_settings(SAVE_ONLY_FIRST_DEPTH_COSTS=True)
    def test_get_dependent_services_cost_only_first_depth(self):
        result = PricingServicePlugin._get_dependent_services_cost(
            self.today,
            pricing_service=self.pricing_service1,
            forecast=False,
            service_environments=self.pricing_service1.service_environments,
        )
        self.assertEquals(result, {
            self.pricing_service2.id: [D('61'), {}]
        })

    @override_settings(SAVE_ONLY_FIRST_DEPTH_COSTS=False)
    def test_get_pricing_service_costs(self):
        costs = PricingServicePlugin._get_pricing_service_costs(
            date=self.today,
            pricing_service=self.pricing_service1,
            forecast=False,
        )
        self.assertEquals(costs, {
            self.pricing_service1.id: (
                D('505'),
                {
                    self.base_usage_type.id: (D('40'), {}),
                    self.regular_usage_type.id: (D('200'), {}),
                    self.team.id: (D('4'), {}),
                    self.extra_cost_type.id: (D('200'), {}),
                    self.pricing_service2.id: [
                        D('61'),
                        {
                            self.base_usage_type.id: [D('10'), {}],
                            self.team.id: [D('1'), {}],
                            self.extra_cost_type.id: [D('50'), {}]
                        }
                    ]
                }
            )
        })

    @override_settings(SAVE_ONLY_FIRST_DEPTH_COSTS=True)
    def test_get_pricing_service_costs_only_first_depth(self):
        costs = PricingServicePlugin._get_pricing_service_costs(
            date=self.today,
            pricing_service=self.pricing_service1,
            forecast=False,
        )
        self.assertEquals(costs, {
            self.pricing_service1.id: (
                D('505'),
                {
                    self.base_usage_type.id: (D('40'), {}),
                    self.regular_usage_type.id: (D('200'), {}),
                    self.team.id: (D('4'), {}),
                    self.extra_cost_type.id: (D('200'), {}),
                    self.pricing_service2.id: [D('61'), {}]
                }
            )
        })

    def test_get_pricing_service_costs2(self):
        # there are 4 daily pricing objects that are using pricing service 2:
        # 2 are in se1, 2 are in se6
        # total cost of pricing service 1 (which has 2 daily pricing objects)
        # for one day (today) is 122:
        #   base usage: 2 (dpo) * 10 (usage value) * 1 (cost per unit) = 20
        #   team: 10 (daily cost) * 0.2 (percent) = 2
        #   extra cost: 100 (daily cost)
        costs = PricingServicePlugin._get_pricing_service_costs(
            self.today,
            self.pricing_service2,
            forecast=False,
        )
        self.assertEquals(costs, {
            self.pricing_service2.id: (D('122'), {
                self.base_usage_type.id: (D('20'), {}),
                self.team.id: (D('2'), {}),
                self.extra_cost_type.id: (D('100'), {}),
            }),
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
        result = {
            self.service_environments[3].id: [
                {
                    'cost': D('126.25'),
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
                            'cost': D('15.25'),
                            'pricing_object_id': po2,
                            'type_id': self.pricing_service2.id,
                            '_children': [
                                {
                                    'cost': D('2.5'),
                                    'pricing_object_id': po2,
                                    'type_id': self.base_usage_type.id,
                                },
                                {
                                    'cost': D('0.25'),
                                    'pricing_object_id': po2,
                                    'type_id': self.team.id,
                                },
                                {
                                    'cost': D('12.5'),
                                    'pricing_object_id': po2,
                                    'type_id': self.extra_cost_type.id,
                                }
                            ],
                        },
                    ],
                },
                {
                    'cost': D('126.25'),
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
                            'cost': D('15.25'),
                            'pricing_object_id': po1,
                            'type_id': self.pricing_service2.id,
                            '_children': [
                                {
                                    'cost': D('2.5'),
                                    'pricing_object_id': po1,
                                    'type_id': self.base_usage_type.id,
                                },
                                {
                                    'cost': D('0.25'),
                                    'pricing_object_id': po1,
                                    'type_id': self.team.id,
                                },
                                {
                                    'cost': D('12.5'),
                                    'pricing_object_id': po1,
                                    'type_id': self.extra_cost_type.id,
                                }
                            ],
                        },
                    ],
                },
            ],
            self.service_environments[4].id: [
                {
                    'cost': D('378.75'),
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
                            'cost': D('45.75'),
                            'pricing_object_id': po4,
                            'type_id': self.pricing_service2.id,
                            '_children': [
                                {
                                    'cost': D('7.5'),
                                    'pricing_object_id': po4,
                                    'type_id': self.base_usage_type.id,
                                },
                                {
                                    'cost': D('0.75'),
                                    'pricing_object_id': po4,
                                    'type_id': self.team.id,
                                },
                                {
                                    'cost': D('37.5'),
                                    'pricing_object_id': po4,
                                    'type_id': self.extra_cost_type.id,
                                }
                            ],
                        }
                    ]
                },
                {
                    'cost': D('378.75'),
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
                            'cost': D('45.75'),
                            'pricing_object_id': po3,
                            'type_id': self.pricing_service2.id,
                            '_children': [
                                {
                                    'cost': D('7.5'),
                                    'pricing_object_id': po3,
                                    'type_id': self.base_usage_type.id,
                                },
                                {
                                    'cost': D('0.75'),
                                    'pricing_object_id': po3,
                                    'type_id': self.team.id,
                                },
                                {
                                    'cost': D('37.5'),
                                    'pricing_object_id': po3,
                                    'type_id': self.extra_cost_type.id,
                                }
                            ],
                        }
                    ]
                },
            ]
        }

        self.assertItemsEqual(costs, result)

    def test_total_costs(self):
        costs = PricingServicePlugin(
            type='total_cost',
            date=self.today,
            pricing_service=self.pricing_service1,
            service_environments=self.service_environments,
            forecast=True,
        )
        self.assertItemsEqual(
            costs,
            {self.pricing_service1.id: (D('1010'), {})}
        )

    def test_total_costs_for_all_service_environments(self):
        costs = PricingServicePlugin(
            type='total_cost',
            date=self.today,
            pricing_service=self.pricing_service1,
            forecast=True,
            for_all_service_environments=True,
        )
        self.assertItemsEqual(costs, {
            self.pricing_service1.id: [
                D('1010'), {
                    self.pricing_service2.id: [
                        D('122'),
                        {
                            self.base_usage_type.id: [D('20'), {}],
                            self.team.id: [D('2'), {}],
                            self.extra_cost_type.id: [D('100'), {}]
                        }
                    ],
                    self.base_usage_type.id: [D('80'), {}],
                    self.regular_usage_type.id: [D('400'), {}],
                    self.team.id: [D('8'), {}],
                    self.extra_cost_type.id: [D('400'), {}]
                }
            ]
        })


class TestPricingServiceDependency(TestCase):
    """
    Specific test cases to test pricing services dependency
    """
    def setUp(self):
        self.start = date(2014, 10, 1)
        self.end = date(2014, 10, 31)
        self.today = date(2014, 10, 12)

    def _init(self):
        self.ps1, self.ps2, self.ps3 = PricingServiceFactory.create_batch(3)
        self.se1, self.se2 = ServiceEnvironmentFactory.create_batch(
            2,
            service__pricing_service=self.ps1,
        )
        self.se3, self.se4 = ServiceEnvironmentFactory.create_batch(
            2,
            service__pricing_service=self.ps2,
        )
        self.se5 = ServiceEnvironmentFactory(
            service__pricing_service=self.ps3
        )
        self.other_se = ServiceEnvironmentFactory.create_batch(5)

        self.service_usage_types = UsageTypeFactory.create_batch(
            4,
            usage_type='SU',
        )

        self.ps1.excluded_services.add(self.other_se[0].service)
        self.ps1.save()

        self.ps2.excluded_services.add(self.other_se[1].service)
        self.ps2.save()

        self.service_usage_types[0].excluded_services.add(
            self.other_se[2].service
        )
        self.service_usage_types[0].save()

        self.service_usage_types[3].excluded_services.add(
            self.other_se[4].service
        )
        self.service_usage_types[3].save()

        models.ServiceUsageTypes.objects.create(
            usage_type=self.service_usage_types[0],
            pricing_service=self.ps1,
            start=self.start,
            end=self.end,
            percent=100,
        )
        models.ServiceUsageTypes.objects.create(
            usage_type=self.service_usage_types[1],
            pricing_service=self.ps2,
            start=self.start,
            end=self.end,
            percent=70,
        )
        models.ServiceUsageTypes.objects.create(
            usage_type=self.service_usage_types[2],
            pricing_service=self.ps2,
            start=self.start,
            end=self.end,
            percent=30,
        )
        models.ServiceUsageTypes.objects.create(
            usage_type=self.service_usage_types[3],
            pricing_service=self.ps3,
            start=self.start,
            end=self.end,
            percent=100,
        )

    def _init_one(self):
        """
        Creates pricing service with 2 service usages.
        Pricing service has se4 in excluded services, its usage type has se3 in
        excluded services.

        There are 3 daily pricing objects - one of them belongs to se1 (and
        should not be considered to calculate usages).
        """
        self.ps1 = PricingServiceFactory()
        self.se1, self.se2 = ServiceEnvironmentFactory.create_batch(
            2,
            service__pricing_service=self.ps1,
        )
        self.se3, self.se4 = ServiceEnvironmentFactory.create_batch(2)

        self.service_usage_types = UsageTypeFactory.create_batch(
            2,
            usage_type='SU',
        )
        self.service_usage_types[0].excluded_services.add(self.se3.service)
        self.service_usage_types[0].save()

        self.ps1.excluded_services.add(self.se4.service)
        self.ps1.save()

        models.ServiceUsageTypes.objects.create(
            usage_type=self.service_usage_types[0],
            pricing_service=self.ps1,
            start=self.start,
            end=self.end,
            percent=70,
        )
        models.ServiceUsageTypes.objects.create(
            usage_type=self.service_usage_types[1],
            pricing_service=self.ps1,
            start=self.start,
            end=self.end,
            percent=30,
        )

        self.dpo1 = DailyPricingObjectFactory()
        self.dpo2 = DailyPricingObjectFactory()
        self.dpo3 = DailyPricingObjectFactory(
            service_environment=self.se1
        )

        for dpo in models.DailyPricingObject.objects.all():
            for su, value in zip(self.service_usage_types, [10, 20]):
                models.DailyUsage.objects.create(
                    daily_pricing_object=dpo,
                    service_environment=dpo.service_environment,
                    date=self.today,
                    value=value,
                    type=su,
                )

    def test_distribute_costs_with_excluded_services(self):
        self._init_one()
        usage_orig = PricingServicePlugin._get_usages_per_pricing_object
        total_orig = PricingServicePlugin._get_total_usage
        with mock.patch('ralph_scrooge.plugins.cost.pricing_service.PricingServiceBasePlugin._get_usages_per_pricing_object') as usage_mock:  # noqa
            with mock.patch('ralph_scrooge.plugins.cost.pricing_service.PricingServiceBasePlugin._get_total_usage') as total_mock:  # noqa
                usage_mock.side_effect = usage_orig
                total_mock.side_effect = total_orig
                PricingServicePlugin._distribute_costs(
                    self.today,
                    pricing_service=self.ps1,
                    costs_hierarchy={},
                    service_usage_types=self.ps1.serviceusagetypes_set.all(),
                    excluded_services=set([
                        self.se4.service,
                        self.se1.service,
                        self.se2.service,
                    ])
                )

                total_mock.assert_any_call(
                    usage_type=self.service_usage_types[0],
                    date=self.today,
                    excluded_services=set([
                        self.se4.service,
                        self.se1.service,
                        self.se2.service,
                        self.se3.service,
                    ])
                )
                total_mock.assert_any_call(
                    usage_type=self.service_usage_types[1],
                    date=self.today,
                    excluded_services=set([
                        self.se4.service,
                        self.se1.service,
                        self.se2.service,
                    ])
                )
                usage_mock.assert_any_call(
                    usage_type=self.service_usage_types[0],
                    date=self.today,
                    excluded_services=set([
                        self.se4.service,
                        self.se1.service,
                        self.se2.service,
                        self.se3.service,
                    ]),
                )
                usage_mock.assert_any_call(
                    usage_type=self.service_usage_types[1],
                    date=self.today,
                    excluded_services=set([
                        self.se4.service,
                        self.se1.service,
                        self.se2.service,
                    ]),
                )

    def test_pricing_dependent_services(self):
        """
        Call costs for PS1, which dependent on PS2, which dependent of PS3.
        Check if all dependencies (and )
        """
        self._init()

        def dependent_services(self1, date, exclude=None):
            if self1 == self.ps1:
                return [self.ps2]
            elif self1 == self.ps2:
                return [self.ps3]
            return []

        # get_dependent_services_mock.side_effect = dependent_services
        with mock.patch.object(models.service.PricingService, 'get_dependent_services', dependent_services):  # noqa
            distribute_costs_orig = PricingServicePlugin._distribute_costs
            with mock.patch('ralph_scrooge.plugins.cost.pricing_service.PricingServiceBasePlugin._distribute_costs') as distribute_costs_mock:  # noqa
                distribute_costs_mock.side_effect = distribute_costs_orig
                PricingServicePlugin.costs(
                    pricing_service=self.ps1,
                    date=self.today,
                    service_environments=models.ServiceEnvironment.objects.all(),  # noqa
                    forecast=False,
                    pricing_services_calculated=None,
                )
                calls = [
                    mock.call(
                        self.today,  # date
                        self.ps3,  # pricing service
                        {self.ps3.id: (0, {})},  # costs - not important here
                        self.ps3.serviceusagetypes_set.all(),  # percentage
                        excluded_services=set([
                            # from ps3
                            self.se5.service,
                        ])
                    ),
                    mock.call(
                        self.today,
                        self.ps2,
                        {self.ps2.id: (0, {})},
                        self.ps2.serviceusagetypes_set.all(),
                        excluded_services=set([
                            # from ps2
                            self.other_se[1].service,
                            self.se3.service,
                            self.se4.service,
                        ])
                    ),
                    mock.call(
                        self.today,
                        self.ps1,
                        {self.ps1.id: (0, {})},
                        self.ps1.serviceusagetypes_set.all(),
                        excluded_services=set([
                            # from ps1
                            self.other_se[0].service,
                            self.se1.service,
                            self.se2.service,
                        ])
                    ),
                ]

                self.assertEquals(
                    len(calls),
                    len(distribute_costs_mock.call_args_list)
                )
                # comparing strings, because of django query sets in params
                for expected_call, actual_call in zip(
                    calls,
                    distribute_costs_mock.call_args_list
                ):
                    self.assertEquals(str(expected_call), str(actual_call))


class TestPricingServiceDiffCharging(TestCase):
    def setUp(self):
        self.today = date(2014, 11, 10)

        self.service_environments = ServiceEnvironmentFactory.create_batch(5)
        self.pricing_service1 = PricingServiceFactory()

        fixed_price = (
            models.PricingServicePlugin.pricing_service_fixed_price_plugin
        )
        self.pricing_service2 = PricingServiceFactory(plugin_type=fixed_price)
        self.pricing_service2.charge_diff_to_real_costs = self.pricing_service1
        self.pricing_service2.save()

        self.pricing_service3 = PricingServiceFactory(plugin_type=fixed_price)
        self.pricing_service3.charge_diff_to_real_costs = self.pricing_service1
        self.pricing_service3.save()

    @mock.patch('ralph_scrooge.plugins.cost.pricing_service.PricingServiceBasePlugin.total_cost')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.pricing_service_fixed_price.PricingServiceFixedPricePlugin.total_cost')  # noqa
    def test_get_service_charging_by_diffs(self, fixed_total_mock, total_mock):
        def total_cost(pricing_service, *args, **kwargs):
            if pricing_service == self.pricing_service2:
                val = D(100)
            else:
                val = D(1000)
            return {pricing_service.id: (val, {})}

        def fixed_total_cost(pricing_service, *args, **kwargs):
            if pricing_service == self.pricing_service2:
                val = D(1000)
            else:
                val = D(100)
            return {pricing_service.id: (val, {})}

        total_mock.side_effect = total_cost
        fixed_total_mock.side_effect = fixed_total_cost
        result = PricingServicePlugin._get_service_charging_by_diffs(
            pricing_service=self.pricing_service1,
            date=self.today,
            forecast=False,
        )
        self.assertEquals(result, {
            self.pricing_service2.id: (-900, {}),
            self.pricing_service3.id: (900, {}),
        })
        calls = [
            mock.call(
                date=self.today,
                pricing_service=x,
                for_all_service_environments=True,
                forecast=False,
            ) for x in (self.pricing_service2, self.pricing_service3)
        ]
        total_mock.assert_has_calls(calls, any_order=True)
        fixed_total_mock.assert_has_calls(calls, any_order=True)

    @mock.patch('ralph_scrooge.plugins.cost.pricing_service.PricingServiceBasePlugin.total_cost')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.pricing_service_fixed_price.PricingServiceFixedPricePlugin.total_cost')  # noqa
    def test_get_service_charging_by_diffs_error(
        self,
        fixed_total_mock,
        total_mock
    ):
        def total_cost(pricing_service, *args, **kwargs):
            if pricing_service == self.pricing_service2:
                return {pricing_service.id: (100, {})}
            raise KeyError()

        def fixed_total_cost(pricing_service, *args, **kwargs):
            if pricing_service == self.pricing_service2:
                return {pricing_service.id: (100, {})}
            raise AttributeError()

        total_mock.side_effect = total_cost
        fixed_total_mock.side_effect = fixed_total_cost
        result = PricingServicePlugin._get_service_charging_by_diffs(
            pricing_service=self.pricing_service1,
            date=self.today,
            forecast=False,
        )
        self.assertEquals(result, {
            self.pricing_service2.id: (0, {}),
        })

    @mock.patch('ralph_scrooge.plugins.cost.pricing_service.PricingServiceBasePlugin.total_cost')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.pricing_service_fixed_price.PricingServiceFixedPricePlugin.total_cost')  # noqa
    def test_get_pricing_service_costs(self, fixed_total_mock, total_mock):
        def total_cost(pricing_service, *args, **kwargs):
            if pricing_service == self.pricing_service2:
                val = D(100)
            else:
                val = D(1000)
            return {pricing_service.id: (val, {})}

        def fixed_total_cost(pricing_service, *args, **kwargs):
            if pricing_service == self.pricing_service2:
                val = D(1000)
            else:
                val = D(100)
            return {pricing_service.id: (val, {})}

        total_mock.side_effect = total_cost
        fixed_total_mock.side_effect = fixed_total_cost
        result = PricingServicePlugin._get_pricing_service_costs(
            pricing_service=self.pricing_service1,
            date=self.today,
            forecast=False,
        )
        self.assertEquals(result, {
            self.pricing_service1.id: (0, {
                self.pricing_service2.id: (-900, {}),
                self.pricing_service3.id: (900, {}),
            })
        })

    @mock.patch('ralph_scrooge.plugins.cost.pricing_service.PricingServiceBasePlugin._get_service_charging_by_diffs')  # noqa
    @mock.patch('ralph_scrooge.plugins.cost.pricing_service.PricingServiceBasePlugin._get_dependent_services_cost')  # noqa
    def test_get_pricing_service_costs_when_diff_key_exist(
        self,
        dependent_costs_mock,
        diff_costs_mock
    ):
        self.usage_type1 = UsageTypeFactory()

        def dependent_costs(*args, **kwargs):
            return {
                self.pricing_service2.id: (100, {
                    self.usage_type1.id: (100, {}),
                }),
                self.pricing_service3.id: (300, {
                    self.usage_type1.id: (100, {}),
                }),
            }

        def diff_costs(pricing_service, *args, **kwargs):
            return {
                self.pricing_service2.id: (200, {}),
            }

        dependent_costs_mock.side_effect = dependent_costs
        diff_costs_mock.side_effect = diff_costs
        result = PricingServicePlugin._get_pricing_service_costs(
            pricing_service=self.pricing_service1,
            date=self.today,
            forecast=False,
        )
        self.assertEquals(result, {
            self.pricing_service1.id: (600, {
                self.pricing_service2.id: (300, {}),
                self.pricing_service3.id: (300, {
                    self.usage_type1.id: (100, {}),
                }),
            })
        })


class TestPricingServiceFixedPricePlugin(ScroogeTestCase):
    def setUp(self):
        self.maxDiff = None
        self.today = date(2013, 10, 10)
        self.start = date(2013, 10, 1)
        self.end = date(2013, 10, 30)

        fixed_price = (
            models.PricingServicePlugin.pricing_service_fixed_price_plugin
        )
        self.pricing_service1 = PricingServiceFactory(plugin_type=fixed_price)

        self.service_environments = ServiceEnvironmentFactory.create_batch(
            2,
            service__pricing_service=self.pricing_service1,
        )
        self.service_environments.append(ServiceEnvironmentFactory())

        self.service_usage_types = UsageTypeFactory.create_batch(
            2,
            usage_type='SU',
        )
        self.sut1 = models.ServiceUsageTypes.objects.create(
            usage_type=self.service_usage_types[0],
            pricing_service=self.pricing_service1,
            start=self.start,
            end=self.end,
            percent=100,
        )
        self.sut2 = models.ServiceUsageTypes.objects.create(
            usage_type=self.service_usage_types[1],
            pricing_service=self.pricing_service1,
            start=self.start,
            end=self.end,
            percent=100,
        )

        self.se1_dpo = DailyPricingObjectFactory.create_batch(
            2,
            service_environment=self.service_environments[0]
        )
        self.se2_dpo = DailyPricingObjectFactory.create_batch(
            2,
            service_environment=self.service_environments[1]
        )
        self.se3_dpo = DailyPricingObjectFactory.create_batch(
            2,
            service_environment=self.service_environments[2]
        )

        models.UsagePrice(
            type=self.service_usage_types[0],
            price=10,
            forecast_price=20,
            start=self.start,
            end=self.end,
        ).save()
        models.UsagePrice(
            type=self.service_usage_types[1],
            price=20,
            forecast_price=40,
            start=self.start,
            end=self.end,
        ).save()

        days = rrule.rrule(rrule.DAILY, dtstart=self.start, until=self.end)
        for day in days:
            for dpo in models.DailyPricingObject.objects.all():
                DailyUsageFactory(
                    date=day,
                    daily_pricing_object=dpo,
                    service_environment=dpo.service_environment,
                    value=10,
                    type=self.service_usage_types[0],
                )
                DailyUsageFactory(
                    date=day,
                    daily_pricing_object=dpo,
                    service_environment=dpo.service_environment,
                    value=5,
                    type=self.service_usage_types[1],
                )

    def test_get_fixed_prices_costs(self):
        result = PricingServiceFixedPricePlugin.costs(
            pricing_service=self.pricing_service1,
            date=self.today,
            service_environments=self.service_environments[:2],
        )

        def _get_single(dpo):
            return {
                'cost': D('200'),
                'pricing_object_id': dpo.pricing_object.id,
                'type_id': self.pricing_service1.id,
                '_children': [
                    {
                        'cost': D('100'),
                        'pricing_object_id': dpo.pricing_object.id,
                        'type_id': self.service_usage_types[0].id,
                        'value': 10.0
                    },
                    {
                        'cost': D('100'),
                        'pricing_object_id': dpo.pricing_object.id,
                        'type_id': self.service_usage_types[1].id,
                        'value': 5.0
                    }
                ],
            }
        self.assertNestedDictsEqual(result, {
            self.service_environments[0].id: [
                _get_single(self.se1_dpo[0]),
                _get_single(self.se1_dpo[1]),
            ],
            self.service_environments[1].id: [
                _get_single(self.se2_dpo[0]),
                _get_single(self.se2_dpo[1]),
            ]
        })

    def test_get_total_cost(self):
        result = PricingServiceFixedPricePlugin.total_cost(
            pricing_service=self.pricing_service1,
            date=self.today,
            service_environments=self.service_environments[:2]
        )
        self.assertEqual(result, {
            self.pricing_service1.id: [D('800'), {
                self.service_usage_types[0].id: [D('400'), {}],
                self.service_usage_types[1].id: [D('400'), {}],
            }]
        })

    @mock.patch('ralph_scrooge.plugins.cost.pricing_service.PricingServiceBasePlugin._get_pricing_service_costs')  # noqa
    def test_get_pricing_service_real_costs_diff(
        self,
        pricing_service_costs_mock,
    ):
        ps2 = PricingServiceFactory()
        self.pricing_service1.charge_diff_to_real_costs = ps2
        self.pricing_service1.save()

        pricing_service_costs_mock.return_value = {
            self.pricing_service1.id: (D(100), {
                self.service_usage_types[0].id: (D(50), {}),
                self.service_usage_types[1].id: (D(50), {}),
            })
        }

        result = PricingServicePlugin._get_service_charging_by_diffs(
            ps2,
            date=self.today,
            forecast=False,
        )
        self.assertEqual(result, {
            self.pricing_service1.id: (D(-1100), {})  # 100 - 1200
        })
