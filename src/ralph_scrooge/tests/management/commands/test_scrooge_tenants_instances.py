# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date

from django.test import TestCase

from ralph_scrooge.management.commands.scrooge_tenants_instances import (
    Command
)
from ralph_scrooge.models import PRICING_OBJECT_TYPES
from ralph_scrooge.tests.utils.factory import (
    DailyTenantInfoFactory,
    DailyUsageFactory,
    UsageTypeFactory,
)


class TestScroogeTenantsInstances(TestCase):
    def setUp(self):
        self.today = date(2014, 11, 12)
        self.yesterday = date(2014, 11, 11)
        self.daily_tenants = DailyTenantInfoFactory.create_batch(
            2,
            pricing_object__type_id=PRICING_OBJECT_TYPES.TENANT,
            pricing_object__model__type_id=PRICING_OBJECT_TYPES.TENANT,
            date=self.today,
        )
        self.daily_tenant2 = DailyTenantInfoFactory(
            pricing_object__type_id=PRICING_OBJECT_TYPES.TENANT,
            pricing_object__model__type_id=PRICING_OBJECT_TYPES.TENANT,
            date=self.yesterday,
        )
        self.openstack_usage1 = UsageTypeFactory(name='openstack.flavor1')
        self.openstack_usage2 = UsageTypeFactory(name='openstack.flavor2')
        DailyUsageFactory(
            daily_pricing_object=self.daily_tenants[0],
            service_environment=self.daily_tenants[0].service_environment,
            type=self.openstack_usage1,
            date=self.today,
            value=24,
        )
        DailyUsageFactory(
            daily_pricing_object=self.daily_tenants[0],
            service_environment=self.daily_tenants[0].service_environment,
            type=self.openstack_usage2,
            date=self.today,
            value=40,
        )
        DailyUsageFactory(
            daily_pricing_object=self.daily_tenants[1],
            service_environment=self.daily_tenants[1].service_environment,
            type=self.openstack_usage1,
            date=self.today,
            value=40,
        )
        DailyUsageFactory(
            daily_pricing_object=self.daily_tenant2,
            service_environment=self.daily_tenant2.service_environment,
            type=self.openstack_usage2,
            date=self.yesterday,
            value=40,
        )

        self.command = Command()

    def test_command(self):
        result = self.command.get_data(today=self.today)
        self.assertEquals(result, [
            [
                self.daily_tenants[0].service_environment.service.name,
                self.daily_tenants[0].service_environment.environment.name,
                self.daily_tenants[0].pricing_object.name,
                self.daily_tenants[0].pricing_object.model.name,
                self.openstack_usage1.name,
                1,
            ],
            [
                self.daily_tenants[0].service_environment.service.name,
                self.daily_tenants[0].service_environment.environment.name,
                self.daily_tenants[0].pricing_object.name,
                self.daily_tenants[0].pricing_object.model.name,
                self.openstack_usage2.name,
                2,
            ],
            [
                self.daily_tenants[1].service_environment.service.name,
                self.daily_tenants[1].service_environment.environment.name,
                self.daily_tenants[1].pricing_object.name,
                self.daily_tenants[1].pricing_object.model.name,
                self.openstack_usage1.name,
                2,
            ],
        ])
