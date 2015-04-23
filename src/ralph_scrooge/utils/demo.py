# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from dateutil import rrule
import datetime
import random

from dateutil.relativedelta import relativedelta
from django.core.management import call_command

from ralph.util.demo import DemoData, register
from ralph_scrooge.models.pricing_object import VIPInfo
from ralph_scrooge.models.usage import UsagePrice
from ralph_scrooge.models.service import (
    Service,
    ServiceEnvironment,
    ServiceUsageTypes,
)
from ralph_scrooge.models.extra_cost import (
    ExtraCostType,
    DynamicExtraCost,
    DynamicExtraCostDivision,
)
from ralph_scrooge.models.team import TeamServiceEnvironmentPercent
from ralph_scrooge.models.usage import UsageType, DailyUsage
from ralph_scrooge.models.cost import CostDateStatus
from ralph_scrooge.models.warehouse import Warehouse
from ralph_scrooge.plugins.cost.collector import Collector
from ralph_scrooge.tests.utils.factory import (
    DynamicExtraCostTypeFactory,
    ExtraCostFactory,
    ExtraCostTypeFactory,
    PricingServiceFactory,
    TeamCostFactory,
    TeamFactory,
    UsageTypeFactory,
)


today = datetime.date.today()
month_ago = today - relativedelta(months=1)
days = [d.date() for d in rrule.rrule(
    rrule.DAILY,
    dtstart=month_ago,
    until=today
)]


@register
class ServicesEnvsDemo(DemoData):
    name = 'scrooge_services_envs'
    title = 'Services Envs'
    required = [
        'assets_dc_assets',
        'assets_licences',
        'assets_supports',
        'business_line',
        'databases',
        'device_racks',
        'discovery_dc',
        'envs',
        'networks',
        'network_envs',
        'relations',
        'services',
        'tenants',
        'vips',
        'virtual',
    ]

    def generate_data(self, data):
        for day in days:
            call_command(
                'scrooge_sync', today=day.strftime('%Y-%m-%d')
            )


@register
class ExtraCostTypeDemo(DemoData):
    name = 'scrooge_extra_cost_type'
    title = 'Extra cost type'

    def generate_data(self, data):
        return {
            'support': ExtraCostType.objects.get(name='Support'),
            'other': ExtraCostType.objects.get(name='Other'),
            'maintenance': ExtraCostTypeFactory(name='Maintenance'),
        }


@register
class ExtraCostDemo(DemoData):
    name = 'scrooge_extra_cost'
    title = 'Extra cost'
    required = ['scrooge_extra_cost_type']

    def generate_data(self, data):
        for i, se in enumerate(ServiceEnvironment.objects.all()):
            ExtraCostFactory(
                extra_cost_type=data['scrooge_extra_cost_type']['maintenance'],
                service_environment=se,
                start=month_ago,
                end=today,
                cost=100 * i,
            )
        return {}


@register
class DynamicExtraCostDemo(DemoData):
    name = 'scrooge_dynamic_extra_cost'
    title = 'Dynamic extra cost'

    def generate_data(self, data):
        insurance = DynamicExtraCostTypeFactory(name='Insurance')
        DynamicExtraCostDivision.objects.create(
            dynamic_extra_cost_type=insurance,
            usage_type=UsageType.objects.get(name='Depreciation'),
            percent=100,
        )
        DynamicExtraCost.objects.create(
            dynamic_extra_cost_type=insurance,
            cost=10000,
            forecast_cost=10000,
            start=month_ago,
            end=today,
        )
        return {
            'insurance': insurance
        }


@register
class TeamsDemo(DemoData):
    name = 'scrooge_teams'
    title = 'Teams'

    def generate_data(self, data):
        dev = TeamFactory(name='Developers')
        tc = TeamCostFactory(team=dev, start=month_ago, end=today, cost=50000)
        percent = [10, 20, 40, 10]
        for p, se in zip(percent, ServiceEnvironment.objects.all()[:4]):
            TeamServiceEnvironmentPercent.objects.create(
                team_cost=tc,
                service_environment=se,
                percent=p
            )
        return {
            'developers': dev,
        }


@register
class UsageTypeDemo(DemoData):
    name = 'scrooge_usage_type'
    title = 'Usage type'

    def generate_data(self, data):
        return {
            'outcoming': UsageTypeFactory(name='Outcoming traffic', type='SU'),
            'incoming': UsageTypeFactory(name='Incoming traffic', type='SU'),
        }


@register
class PricingServiceDemo(DemoData):
    name = 'scrooge_pricing_service'
    title = 'Pricing service'
    required = ['scrooge_usage_type', 'scrooge_services_envs']

    def generate_data(self, data):
        service = Service.objects.get(name='Load balancing')
        pricing_service = PricingServiceFactory(name='Load balancing')
        for usage_type in data['scrooge_usage_type'].itervalues():
            ServiceUsageTypes.objects.create(
                usage_type=usage_type,
                pricing_service=pricing_service,
                percent=50,
            )
        service.pricing_service = pricing_service
        service.save()
        return {
            'load_balancing': pricing_service,
        }


@register
class FakedUsageDemo(DemoData):
    name = 'scrooge_faked_usage'
    required = ['scrooge_usage_type']

    def generate_data(self, data):
        for vip_info in VIPInfo.objects.all():
            for delta in xrange(10):
                faked_today = today - datetime.timedelta(days=delta)
                daily_pricing = vip_info.get_daily_pricing_object(faked_today)
                for usage_type in data['scrooge_usage_type'].values():
                    DailyUsage.objects.create(
                        daily_pricing_object=daily_pricing,
                        service_environment=daily_pricing.service_environment,
                        value=random.randint(50000, 900000),
                        type=usage_type,
                        date=faked_today,
                    )
        usage_types = UsageType.objects.filter(
            name__in=['Collocation', 'Power consumption']
        )
        for usage_type in usage_types:
            usage_type.is_manually_type = True
            usage_type.save()
            for wh in Warehouse.objects.all():
                value = random.randint(2000, 10000)
                UsagePrice.objects.create(
                    start=month_ago, end=today, cost=value,
                    forecast_cost=value, type=usage_type, warehouse=wh,
                )


@register
class FakedCalcDemo(DemoData):
    name = 'scrooge_faked_calc'
    required = [
        'scrooge_dynamic_extra_cost',
        'scrooge_extra_cost',
        'scrooge_faked_usage',
        'scrooge_pricing_service',
        'scrooge_usage_type',
        'scrooge_teams',
    ]

    def generate_data(self, data):
        Warehouse.objects.all().update(show_in_report=True)
        for day in days:
            call_command(
                'scrooge_sync', today=day.strftime('%Y-%m-%d')
            )
        collector = Collector()
        forecast = False
        for day in days:
            costs = collector.process(day, forecast)
            processed = collector._create_daily_costs(day, costs, forecast)
            collector.save_period_costs(day, day, forecast, processed)

        CostDateStatus.objects.all().update(accepted=True)
