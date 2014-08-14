# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import random

from factory import (
    fuzzy,
    lazy_attribute,
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

    name = Sequence(lambda n: 'Service #%s' % n)
    ci_uid = Sequence(lambda n: n)


class EnvironmentFactory(DjangoModelFactory):
    FACTORY_FOR = models.Environment

    name = Sequence(lambda n: 'Environment #%s' % n)
    environment_id = Sequence(lambda n: n)


class ServiceEnvironmentFactory(DjangoModelFactory):
    FACTORY_FOR = models.ServiceEnvironment

    service = SubFactory(ServiceFactory)
    environment = SubFactory(EnvironmentFactory)


class UsageTypeFactory(DjangoModelFactory):
    FACTORY_FOR = models.UsageType

    name = Sequence(lambda n: 'UsageType #%s' % n)


class PricingObjectFactory(DjangoModelFactory):
    FACTORY_FOR = models.PricingObject

    type = 1
    service_environment = SubFactory(ServiceEnvironmentFactory)


class DailyPricingObjectFactory(DjangoModelFactory):
    FACTORY_FOR = models.DailyPricingObject

    date = datetime.date.today()
    pricing_object = SubFactory(PricingObjectFactory)
    service_environment = SubFactory(ServiceEnvironmentFactory)


class AssetInfoFactory(PricingObjectFactory):
    FACTORY_FOR = models.AssetInfo

    device_id = Sequence(lambda n: n)
    sn = Sequence(lambda n: n)
    barcode = Sequence(lambda n: n)
    asset_id = Sequence(lambda n: n)
    device_id = Sequence(lambda n: n)
    warehouse = SubFactory(WarehouseFactory)


class DailyAssetInfoFactory(DailyPricingObjectFactory):
    FACTORY_FOR = models.DailyAssetInfo

    asset_info = SubFactory(AssetInfoFactory)
    depreciation_rate = fuzzy.FuzzyDecimal(0, 50)
    is_depreciated = fuzzy.FuzzyAttribute(lambda: random.random() < 0.5)
    price = fuzzy.FuzzyDecimal(0, 1000)
    date = fuzzy.FuzzyDate(MIN_FACTORY_DATE, MAX_FACTORY_DATE)


class OwnerFactory(DjangoModelFactory):
    FACTORY_FOR = models.Owner

    first_name = "Scrooge"
    last_name = Sequence(lambda n: "McDuck {}".format(n))
    sAMAccountName = "qwerty"
    cmdb_id = Sequence(lambda n: n)

    @lazy_attribute
    def email(self):
        return '{}.{}@example.com'.format(self.first_name, self.last_name)


class BusinessLineFactory(DjangoModelFactory):
    FACTORY_FOR = models.BusinessLine

    name = Sequence(lambda n: 'Business Line #%s' % n)
    ci_uid = Sequence(lambda n: n)


class TenantInfoFactory(PricingObjectFactory):
    FACTORY_FOR = models.TenantInfo

    tenant_id = Sequence(lambda n: n)


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

    type = SubFactory(ExtraCostTypeFactory)
    monthly_cost = 3100
    service = SubFactory(ServiceFactory)
    pricing_object = SubFactory(PricingObjectFactory)
    start = datetime.date.today()
    end = datetime.date.today()
    mode = models.ExtraCostChoices.daily_imprint


class TeamFactory(DjangoModelFactory):
    FACTORY_FOR = models.Team

    name = Sequence(lambda n: 'Team #%s' % n)
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
