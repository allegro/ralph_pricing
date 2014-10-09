# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import random

import factory
from django.contrib.auth.models import User
from factory import (
    fuzzy,
    Sequence,
    SubFactory,
)
from factory.django import DjangoModelFactory

from ralph_scrooge import models

MIN_FACTORY_DATE = datetime.date(2014, 7, 1)
MAX_FACTORY_DATE = datetime.date(2014, 7, 31)


class WarehouseFactory(DjangoModelFactory):
    FACTORY_FOR = models.Warehouse

    name = Sequence(lambda n: 'Name_{0}'.format(n))
    id_from_assets = Sequence(lambda n: n)


class ServiceFactory(DjangoModelFactory):
    FACTORY_FOR = models.Service

    name = Sequence(lambda n: 'Service%s' % n)
    symbol = Sequence(lambda n: 'service_%s' % n)
    ci_id = Sequence(lambda n: n)
    ci_uid = Sequence(lambda n: 'uid-{}'.format(n))


class EnvironmentFactory(DjangoModelFactory):
    FACTORY_FOR = models.Environment

    name = Sequence(lambda n: 'Environment%s' % n)
    ci_id = Sequence(lambda n: n)
    ci_uid = Sequence(lambda n: 'uid-{}'.format(n))


class ServiceEnvironmentFactory(DjangoModelFactory):
    FACTORY_FOR = models.ServiceEnvironment

    service = SubFactory(ServiceFactory)
    environment = SubFactory(EnvironmentFactory)


class UsageTypeFactory(DjangoModelFactory):
    FACTORY_FOR = models.UsageType

    name = Sequence(lambda n: 'UsageType%s' % n)
    symbol = Sequence(lambda n: 'ut%s' % n)


class PricingObjectFactory(DjangoModelFactory):
    FACTORY_FOR = models.PricingObject

    type = 1
    service_environment = SubFactory(ServiceEnvironmentFactory)
    name = Sequence(lambda n: 'Pricing Object%s' % n)


class DailyPricingObjectFactory(DjangoModelFactory):
    FACTORY_FOR = models.DailyPricingObject

    date = datetime.date.today()
    pricing_object = SubFactory(PricingObjectFactory)
    service_environment = SubFactory(ServiceEnvironmentFactory)


class AssetModelFactory(DjangoModelFactory):
    FACTORY_FOR = models.AssetModel

    model_id = Sequence(lambda n: n)
    name = Sequence(lambda n: 'Asset Model #%s' % n)
    manufacturer = Sequence(lambda n: 'Manufacturer #%s' % n)
    category = Sequence(lambda n: 'Category #%s' % n)


class AssetInfoFactory(PricingObjectFactory):
    FACTORY_FOR = models.AssetInfo

    device_id = Sequence(lambda n: n)
    sn = Sequence(lambda n: n)
    barcode = Sequence(lambda n: n)
    asset_id = Sequence(lambda n: n)
    warehouse = SubFactory(WarehouseFactory)
    model = SubFactory(AssetModelFactory)


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


class UserFactory(DjangoModelFactory):
    FACTORY_FOR = User
    username = Sequence(lambda n: 'user_{0}'.format(n))
    first_name = Sequence(lambda n: 'John {0}'.format(n))
    last_name = Sequence(lambda n: 'Snow {0}'.format(n))


@factory.sequence
def get_profile(n):
    """Due to strange logic in lck.django we can't use subfactories to create
    profiles."""
    user = UserFactory()
    user.save()
    return user.profile


class OwnerFactory(DjangoModelFactory):
    FACTORY_FOR = models.Owner

    cmdb_id = Sequence(lambda n: n)
    profile = get_profile


class BusinessLineFactory(DjangoModelFactory):
    FACTORY_FOR = models.BusinessLine

    name = Sequence(lambda n: 'Business Line%s' % n)
    ci_id = Sequence(lambda n: n)
    ci_uid = Sequence(lambda n: n)


class ProfitCenterFactory(DjangoModelFactory):
    FACTORY_FOR = models.ProfitCenter

    name = Sequence(lambda n: 'Profit Center%s' % n)
    description = Sequence(lambda n: 'Profit Center%s description' % n)
    ci_id = Sequence(lambda n: n)
    ci_uid = Sequence(lambda n: n)
    business_line = SubFactory(BusinessLineFactory)


class TenantGroupFactory(DjangoModelFactory):
    FACTORY_FOR = models.TenantGroup

    group_id = Sequence(lambda n: n)
    name = Sequence(lambda n: 'Tenant Group #%s' % n)


class TenantInfoFactory(PricingObjectFactory):
    FACTORY_FOR = models.TenantInfo

    tenant_id = Sequence(lambda n: n)
    group = SubFactory(TenantGroupFactory)


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
    pricing_object = SubFactory(PricingObjectFactory)
    start = datetime.date.today()
    end = datetime.date.today()


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
    show_in_report = True
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

    team = SubFactory(TeamFactory)
    service_environment = SubFactory(ServiceEnvironmentFactory)
    percent = fuzzy.FuzzyDecimal(0, 100)


class PricingServiceFactory(DjangoModelFactory):
    FACTORY_FOR = models.PricingService

    name = Sequence(lambda n: 'Pricing Service %s' % n)
    symbol = Sequence(lambda n: 'ps%s' % n)
    use_universal_plugin = True


class CostDateStatusFactory(DjangoModelFactory):
    FACTORY_FOR = models.CostDateStatus

    date = datetime.date.today()
