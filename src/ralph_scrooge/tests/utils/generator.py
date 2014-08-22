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


def usages_generator(start, end):
    # base usages
    base_usage_type = UsageTypeFactory(
        usage_type='BU',
        by_cost=True,
    )

    # regular usage
    regular_usage_type = UsageTypeFactory(
        usage_type='RU',
        by_cost=False,
    )

    # team
    team = TeamFactory()

    # extra cost
    extra_cost_type = ExtraCostTypeFactory()

    # pricing services
    pricing_service1 = PricingServiceFactory()
    pricing_service1.regular_usage_types.add(regular_usage_type)
    pricing_service1.save()

    # NOTICE THAT PRICING SERVICE 2 IS NOT CHARGED FOR REGULAR USAGE
    pricing_service2 = PricingServiceFactory()

    # services
    service_environments = ServiceEnvironmentFactory.create_batch(
        2,
        service__pricing_service=pricing_service1,
    )
    service_environments.append(ServiceEnvironmentFactory.create(
        service__pricing_service=pricing_service2,
    ))
    service_environments.extend(
        ServiceEnvironmentFactory.create_batch(3)
    )

    # pricing service usages
    service_usage_types = UsageTypeFactory.create_batch(
        3,
        usage_type='SU',
    )
    models.ServiceUsageTypes.objects.create(
        usage_type=service_usage_types[0],
        pricing_service=pricing_service1,
        start=start,
        end=end,
        percent=30,
    )
    models.ServiceUsageTypes.objects.create(
        usage_type=service_usage_types[1],
        pricing_service=pricing_service1,
        start=start,
        end=end,
        percent=70,
    )
    models.ServiceUsageTypes.objects.create(
        usage_type=service_usage_types[2],
        pricing_service=pricing_service2,
        start=start,
        end=end,
        percent=100,
    )

    # daily pricing objects
    # in pricing service 1 (& use pricing service 2)
    se1_dpo = DailyPricingObjectFactory.create_batch(
        2,
        service_environment=service_environments[0]
    )
    se2_dpo = DailyPricingObjectFactory.create_batch(
        2,
        service_environment=service_environments[1]
    )
    # in pricing service 2
    DailyPricingObjectFactory.create_batch(
        2,
        service_environment=service_environments[2]
    )
    # use pricing service 1
    se4_dpo = DailyPricingObjectFactory.create_batch(
        2,
        service_environment=service_environments[3]
    )
    se5_dpo = DailyPricingObjectFactory.create_batch(
        2,
        service_environment=service_environments[4]
    )
    # use pricing service 2 (besides se1_dpo and se2_dpo)
    se6_dpo = DailyPricingObjectFactory.create_batch(
        2,
        service_environment=service_environments[5]
    )
    # other
    DailyPricingObjectFactory.create_batch(
        2,
        service_environment=service_environments[5]
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
        type=base_usage_type,
        cost=4200,  # daily cost: 1
        forecast_cost=8400,  # daily cost: 2
        start=start,
        end=end,
    ).save()
    # regular usage type
    models.UsagePrice(
        type=regular_usage_type,
        price=10,
        forecast_price=20,
        start=start,
        end=end,
    ).save()
    days = rrule.rrule(rrule.DAILY, dtstart=start, until=end)
    for day in days:
        # TODO: fix assigning DPO with wrong date to DailyUsage
        for dpo in models.DailyPricingObject.objects.all():
            DailyUsageFactory(
                date=day,
                daily_pricing_object=dpo,
                service_environment=dpo.service_environment,
                value=10,
                type=base_usage_type,
            )
            DailyUsageFactory(
                date=day,
                daily_pricing_object=dpo,
                service_environment=dpo.service_environment,
                value=5,
                type=regular_usage_type,
            )

    # team
    team_cost = models.TeamCost(
        team=team,
        cost=300,  # daily cost: 10
        forecast_cost=600,  # daily cost: 20
        start=start,
        end=end,
    )
    team_cost.save()
    for se in service_environments[:5]:
        models.TeamServiceEnvironmentPercent(
            team_cost=team_cost,
            service_environment=se,
            percent=20,  # 2 per day per se
        ).save()

    # extra cost
    for se in service_environments[:5]:
        models.ExtraCost(
            extra_cost_type=extra_cost_type,
            start=start,
            end=end,
            service_environment=se,
            cost=3000,  # daily cost: 100
            forecast_cost=6000,  # daily cost: 200
        ).save()

    # pricing service 1 service usage types usages
    for dpo, multiplier in zip(se4_dpo + se5_dpo, [1, 1, 3, 3]):
        days = rrule.rrule(rrule.DAILY, dtstart=start, until=end)
        for day in days:
            DailyUsageFactory(
                type=service_usage_types[0],
                daily_pricing_object=dpo,
                service_environment=dpo.service_environment,
                value=10 * multiplier,
                date=day,
            )
            DailyUsageFactory(
                type=service_usage_types[1],
                daily_pricing_object=dpo,
                service_environment=dpo.service_environment,
                value=50 * multiplier,
                date=day,
            )

    # pricing service 2 service usage types usages
    for dpo in se1_dpo + se2_dpo + se6_dpo:
        days = rrule.rrule(rrule.DAILY, dtstart=start, until=end)
        for day in days:
            DailyUsageFactory(
                type=service_usage_types[2],
                daily_pricing_object=dpo,
                service_environment=dpo.service_environment,
                value=100,
                date=day,
            )
