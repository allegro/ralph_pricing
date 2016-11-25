# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import random

import factory
from django.contrib.auth import get_user_model
from factory import (
    fuzzy,
    Iterator,
    LazyAttribute,
    Sequence,
    SubFactory,
)
from factory.django import DjangoModelFactory

from ralph_scrooge import models

MIN_FACTORY_DATE = datetime.date(2014, 7, 1)
MAX_FACTORY_DATE = datetime.date(2014, 7, 31)


# TODO(mkurek): bump factory-boy to newest version
class WarehouseFactory(DjangoModelFactory):
    FACTORY_FOR = models.Warehouse

    name = Sequence(lambda n: 'Name_{0}'.format(n))
    id_from_assets = Sequence(lambda n: n)
    ralph3_id = Sequence(lambda n: n)


class UserFactory(DjangoModelFactory):
    FACTORY_FOR = get_user_model()
    username = Sequence(lambda n: 'user_{0}'.format(n))
    first_name = Sequence(lambda n: 'John {0}'.format(n))
    last_name = Sequence(lambda n: 'Snow {0}'.format(n))


class Ralph3UserFactory(DjangoModelFactory):
    # TODO(xor-xor): This factory shouldn't be used to create more than
    # 6 users, otherwise you'll get an IntegrityError. But this will be
    # ironed-out once we switch to Ralph 3 exclusively.
    FACTORY_FOR = get_user_model()
    first_name = Iterator([
        'James', 'Michael', 'Robert', 'Maria', 'David', 'Andrew',
    ])
    last_name = Iterator([
        'Smith', 'Wilson', 'Thomas', 'Roberts', 'Johnson', 'Williams',
    ])
    username = LazyAttribute(
        lambda u: '{}_{}'.format(u.first_name, u.last_name).lower()
    )


@factory.sequence
def get_ralph3_user(n):
    return Ralph3UserFactory()


class BusinessLineFactory(DjangoModelFactory):
    FACTORY_FOR = models.BusinessLine

    name = Sequence(lambda n: 'Business Line%s' % n)
    ci_id = Sequence(lambda n: n)
    ralph3_id = Sequence(lambda n: n)
    ci_uid = Sequence(lambda n: n)


class ProfitCenterFactory(DjangoModelFactory):
    FACTORY_FOR = models.ProfitCenter

    name = Sequence(lambda n: 'Profit Center%s' % n)
    description = Sequence(lambda n: 'Profit Center%s description' % n)
    ci_id = Sequence(lambda n: n)
    ralph3_id = Sequence(lambda n: n)
    ci_uid = Sequence(lambda n: n)
    business_line = SubFactory(BusinessLineFactory)


class ServiceFactory(DjangoModelFactory):
    FACTORY_FOR = models.Service

    name = Sequence(lambda n: 'Service%s' % n)
    symbol = Sequence(lambda n: 'service_%s' % n)
    ci_id = Sequence(lambda n: n)
    ralph3_id = Sequence(lambda n: n)
    ci_uid = Sequence(lambda n: 'uid-{}'.format(n))
    profit_center = SubFactory(ProfitCenterFactory)


class EnvironmentFactory(DjangoModelFactory):
    FACTORY_FOR = models.Environment

    name = Sequence(lambda n: 'Environment%s' % n)
    ci_id = Sequence(lambda n: n)
    ralph3_id = Sequence(lambda n: n)
    ci_uid = Sequence(lambda n: 'uid-{}'.format(n))


class ServiceEnvironmentFactory(DjangoModelFactory):
    FACTORY_FOR = models.ServiceEnvironment

    service = SubFactory(ServiceFactory)
    environment = SubFactory(EnvironmentFactory)


class BaseUsageFactory(DjangoModelFactory):
    FACTORY_FOR = models.BaseUsage

    type = models.BaseUsageType.usage_type


class DailyCostFactory(DjangoModelFactory):
    FACTORY_FOR = models.DailyCost

    service_environment = SubFactory(ServiceEnvironmentFactory)
    type = SubFactory(BaseUsageFactory)
    path = Sequence(lambda n: n)


class UsageTypeFactory(DjangoModelFactory):
    FACTORY_FOR = models.UsageType
    FACTORY_DJANGO_GET_OR_CREATE = ['symbol']

    name = Sequence(lambda n: 'UsageType%s' % n)
    symbol = Sequence(lambda n: 'ut%s' % n)


class PricingObjectModelFactory(DjangoModelFactory):
    FACTORY_FOR = models.PricingObjectModel

    type_id = 1
    model_id = Sequence(lambda n: n)
    ralph3_model_id = Sequence(lambda n: n)
    name = Sequence(lambda n: 'Model %s' % n)


class PricingObjectFactory(DjangoModelFactory):
    FACTORY_FOR = models.PricingObject

    type_id = 1
    service_environment = SubFactory(ServiceEnvironmentFactory)
    name = Sequence(lambda n: 'Pricing Object%s' % n)
    model = SubFactory(PricingObjectModelFactory)


class IPInfoFactory(PricingObjectFactory):
    FACTORY_FOR = models.IPInfo


class DailyPricingObjectFactory(DjangoModelFactory):
    FACTORY_FOR = models.DailyPricingObject

    date = datetime.date.today()
    pricing_object = SubFactory(PricingObjectFactory)
    service_environment = SubFactory(ServiceEnvironmentFactory)


class TenantInfoFactory(PricingObjectFactory):
    FACTORY_FOR = models.TenantInfo

    tenant_id = Sequence(lambda n: n)
    ralph3_tenant_id = Sequence(lambda n: n)
    type_id = models.PRICING_OBJECT_TYPES.TENANT


class DailyTenantInfoFactory(DailyPricingObjectFactory):
    FACTORY_FOR = models.DailyTenantInfo

    tenant_info = SubFactory(TenantInfoFactory)
    enabled = True


class DailyUsageFactory(DjangoModelFactory):
    FACTORY_FOR = models.DailyUsage

    date = datetime.date.today()
    service_environment = SubFactory(ServiceEnvironmentFactory)
    daily_pricing_object = SubFactory(DailyPricingObjectFactory)
    value = fuzzy.FuzzyDecimal(0, 1000)
    warehouse = SubFactory(WarehouseFactory)
    type = SubFactory(UsageTypeFactory)


class AssetInfoFactory(PricingObjectFactory):
    FACTORY_FOR = models.AssetInfo

    device_id = Sequence(lambda n: n)
    sn = Sequence(lambda n: n)
    barcode = Sequence(lambda n: n)
    asset_id = Sequence(lambda n: n)
    ralph3_asset_id = Sequence(lambda n: n)
    warehouse = SubFactory(WarehouseFactory)


class VIPInfoFactory(PricingObjectFactory):
    FACTORY_FOR = models.VIPInfo

    vip_id = Sequence(lambda n: n)
    ip_info = SubFactory(PricingObjectFactory)
    type_id = models.PRICING_OBJECT_TYPES.VIP
    port = 80
    load_balancer = SubFactory(AssetInfoFactory)


class DailyVIPFactory(DailyPricingObjectFactory):
    FACTORY_FOR = models.DailyVIPInfo

    vip_info = SubFactory(VIPInfoFactory)
    ip_info = SubFactory(PricingObjectFactory)


class VirtualInfoFactory(PricingObjectFactory):
    FACTORY_FOR = models.VirtualInfo

    name = Sequence(lambda n: "name_{0}".format(n))
    device_id = Sequence(lambda n: n)


class DailyAssetInfoFactory(DailyPricingObjectFactory):
    FACTORY_FOR = models.DailyAssetInfo

    asset_info = SubFactory(AssetInfoFactory)
    depreciation_rate = fuzzy.FuzzyDecimal(0, 50)
    is_depreciated = fuzzy.FuzzyAttribute(lambda: random.random() < 0.5)
    price = fuzzy.FuzzyDecimal(0, 1000)
    date = fuzzy.FuzzyDate(MIN_FACTORY_DATE, MAX_FACTORY_DATE)


class DailyVirtualInfoFactory(DailyPricingObjectFactory):
    FACTORY_FOR = models.DailyVirtualInfo

    virtual_info = SubFactory(VirtualInfoFactory)
    hypervisor = SubFactory(DailyAssetInfoFactory)


class OpenstackUsageTypeFactory(UsageTypeFactory):
    symbol = Sequence(lambda n: 'openstack.instance%d' % n)


class OpenstackDailyUsageTypeFactory(DailyUsageFactory):
    type = SubFactory(OpenstackUsageTypeFactory)


class ExtraCostTypeFactory(DjangoModelFactory):
    FACTORY_FOR = models.ExtraCostType

    name = Sequence(lambda n: 'Extra_Cost_type_%s' % n)


class ExtraCostFactory(DjangoModelFactory):
    FACTORY_FOR = models.ExtraCost

    extra_cost_type = SubFactory(ExtraCostTypeFactory)
    cost = 3100
    service_environment = SubFactory(ServiceEnvironmentFactory)
    start = datetime.date.today()
    end = datetime.date.today()


class SupportCostFactory(DjangoModelFactory):
    FACTORY_FOR = models.SupportCost

    extra_cost_type = SubFactory(ExtraCostTypeFactory)
    cost = 100
    start = datetime.date.today()
    end = datetime.date.today()
    support_id = Sequence(lambda n: n)
    pricing_object = SubFactory(PricingObjectFactory)


class DynamicExtraCostTypeFactory(DjangoModelFactory):
    FACTORY_FOR = models.DynamicExtraCostType

    name = Sequence(lambda n: 'Dynamic Extra Cost type %s' % n)


class DynamicExtraCostFactory(DjangoModelFactory):
    FACTORY_FOR = models.DynamicExtraCost

    dynamic_extra_cost_type = SubFactory(DynamicExtraCostTypeFactory)
    cost = 100
    forecast_cost = 200
    start = datetime.date.today()
    end = datetime.date.today()


class DynamicExtraCostDivisionFactory(DjangoModelFactory):
    FACTORY_FOR = models.DynamicExtraCostDivision

    dynamic_extra_cost_type = SubFactory(DynamicExtraCostTypeFactory)
    usage_type = SubFactory(UsageTypeFactory)
    percent = 50


class TeamFactory(DjangoModelFactory):
    FACTORY_FOR = models.Team

    name = Sequence(lambda n: 'Team %s' % n)
    show_percent_column = False
    billing_type = models.TeamBillingType.time


class TeamCostFactory(DjangoModelFactory):
    FACTORY_FOR = models.TeamCost

    team = SubFactory(TeamFactory)
    start = datetime.date.today()
    end = datetime.date.today()
    members_count = fuzzy.FuzzyInteger(10, 30)
    cost = fuzzy.FuzzyDecimal(100, 1000)
    forecast_cost = fuzzy.FuzzyDecimal(100, 1000)


class TeamServiceEnvironmentPercentFactory(DjangoModelFactory):
    FACTORY_FOR = models.TeamServiceEnvironmentPercent

    team_cost = SubFactory(TeamCostFactory)
    service_environment = SubFactory(ServiceEnvironmentFactory)
    percent = fuzzy.FuzzyDecimal(0, 100)


class PricingServiceFactory(DjangoModelFactory):
    FACTORY_FOR = models.PricingService

    name = Sequence(lambda n: 'Pricing Service %s' % n)
    symbol = Sequence(lambda n: 'ps%s' % n)


class CostDateStatusFactory(DjangoModelFactory):
    FACTORY_FOR = models.CostDateStatus

    date = datetime.date.today()


class ServiceUsageTypesFactory(DjangoModelFactory):
    FACTORY_FOR = models.ServiceUsageTypes

    usage_type = SubFactory(UsageTypeFactory)
    pricing_service = SubFactory(PricingServiceFactory)


class UsagePriceFactory(DjangoModelFactory):
    FACTORY_FOR = models.UsagePrice

    type = SubFactory(UsageTypeFactory)
    start = datetime.date(2014, 10, 1)
    end = datetime.date(2014, 10, 31)


class DatabaseInfoFactory(PricingObjectFactory):
    FACTORY_FOR = models.DatabaseInfo
    type_id = models.PRICING_OBJECT_TYPES.DATABASE

    database_id = Sequence(lambda n: n)
    parent_device = SubFactory(AssetInfoFactory)


class DailyDatabaseInfoFactory(DailyPricingObjectFactory):
    FACTORY_FOR = models.DailyDatabaseInfo

    database_info = SubFactory(DatabaseInfoFactory)
    parent_device = SubFactory(DailyAssetInfoFactory)
