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
        self.profit_center1 = ProfitCenterFactory()
        self.profit_center2 = ProfitCenterFactory()

        self.report_start = date.today()
        self.report_end = self.report_start + timedelta(days=1)
        self.service_environment1 = ServiceEnvironmentFactory(
            service__profit_center=self.profit_center1
        )
        self.service_environment2 = ServiceEnvironmentFactory(
            service__profit_center=self.profit_center2
        )
        self.service_environments = models.ServiceEnvironment.objects.all()

        self.service_environment1.service.profit_center = self.profit_center2
        self.service_environment1.service.save()

    def test_costs(self):
        result = Information(
            service_environments=self.service_environments,
            start=self.report_start,
            end=self.report_end,
        )
        self.assertEquals(result, {
            self.service_environment1.id: {
                'profit_center': ' / '.join((
                    self.profit_center1.name,
                    self.profit_center2.name
                )),
                'service_id': self.service_environment1.service.ci_uid,
                'service': self.service_environment1.service.name,
                'environment': self.service_environment1.environment.name,
            },
            self.service_environment2.id: {
                'profit_center': self.profit_center2.name,
                'service_id': self.service_environment2.service.ci_uid,
                'service': self.service_environment2.service.name,
                'environment': self.service_environment2.environment.name,
            },
        })
