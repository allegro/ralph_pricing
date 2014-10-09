# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from dateutil import rrule

from ralph_scrooge import models
from ralph_scrooge.tests.utils.factory import (
    DailyUsageFactory,
    DailyPricingObjectFactory,
    ExtraCostTypeFactory,
    PricingServiceFactory,
    ServiceEnvironmentFactory,
    TeamFactory,
    UsageTypeFactory,
)
from ralph_scrooge.utils.common import AttributeDict


def usages_generator(start, end, self=None):
    if self is None:
        self = AttributeDict(
            start=start,
            end=end,
        )

    # base usages
    self.base_usage_type = UsageTypeFactory(
        usage_type='BU',
        by_cost=True,
        is_manually_type=True,
    )

    # regular usage
    self.regular_usage_type = UsageTypeFactory(
        usage_type='RU',
        by_cost=False,
        is_manually_type=True,
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
        service_environment=self.service_environments[0],
        date=start,
    )
    self.se2_dpo = DailyPricingObjectFactory.create_batch(
        2,
        service_environment=self.service_environments[1],
        date=start,
    )
    # in pricing service 2
    self.se3_dpo = DailyPricingObjectFactory.create_batch(
        2,
        service_environment=self.service_environments[2],
        date=start,
    )
    # use pricing service 1
    self.se4_dpo = DailyPricingObjectFactory.create_batch(
        2,
        service_environment=self.service_environments[3],
        date=start,
    )
    self.se5_dpo = DailyPricingObjectFactory.create_batch(
        2,
        service_environment=self.service_environments[4],
        date=start,
    )
    # use pricing service 2 (besides se1_dpo and se2_dpo)
    self.se6_dpo = DailyPricingObjectFactory.create_batch(
        2,
        service_environment=self.service_environments[5],
        date=start,
    )
    # other
    self.se7_dpo = DailyPricingObjectFactory.create_batch(
        2,
        service_environment=self.service_environments[5],
        date=start,
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

    return self
