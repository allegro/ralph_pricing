# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date, timedelta

from django.test import TestCase

from ralph_scrooge import models
from ralph_scrooge.plugins.report.information import Information
from ralph_scrooge.tests.utils.factory import (
    ProfitCenterFactory,
    ServiceEnvironmentFactory,
)


class TestInformationPlugin(TestCase):
    def setUp(self):
        self.pc1 = ProfitCenterFactory()
        self.pc2 = ProfitCenterFactory()

        self.report_start = date.today()
        self.report_end = self.report_start + timedelta(days=1)
        self.service_environment1 = ServiceEnvironmentFactory(
            service__profit_center=self.pc1
        )
        self.service_environment2 = ServiceEnvironmentFactory(
            service__profit_center=self.pc2
        )
        self.service_environments = models.ServiceEnvironment.objects.all()

        self.service_environment1.service.profit_center = self.pc2
        self.service_environment1.service.save()
        self.maxDiff = None

    def test_costs(self):
        result = Information(
            service_environments=self.service_environments,
            start=self.report_start,
            end=self.report_end,
        )
        self.assertEquals(result, {
            self.service_environment1.id: {
                'profit_center': ' / '.join((
                    ' - '.join((self.pc1.name, self.pc1.description)),
                    ' - '.join((self.pc2.name, self.pc2.description)),
                )),
                'business_line': ' / '.join((
                    self.pc1.business_line.name,
                    self.pc2.business_line.name,
                )),
                'id': self.service_environment1.id,
                'service': self.service_environment1.service.name,
                'environment': self.service_environment1.environment.name,
            },
            self.service_environment2.id: {
                'profit_center': ' - '.join((
                    self.pc2.name,
                    self.pc2.description
                )),
                'business_line': self.pc2.business_line.name,
                'id': self.service_environment2.id,
                'service': self.service_environment2.service.name,
                'environment': self.service_environment2.environment.name,
            },
        })
