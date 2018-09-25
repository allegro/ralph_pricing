# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date, timedelta
from unittest import skip

from ralph_scrooge import models
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.plugins.report.information import Information
from ralph_scrooge.tests.utils.factory import (
    ProfitCenterFactory,
    ServiceEnvironmentFactory,
    BusinessLineFactory)


class TestInformationPlugin(ScroogeTestCase):
    def setUp(self):
        self.bl1 = BusinessLineFactory()
        self.bl2 = BusinessLineFactory()

        self.pc1 = ProfitCenterFactory()
        self.pc2 = ProfitCenterFactory()

        self.report_start = date.today()
        self.report_end = self.report_start + timedelta(days=1)
        self.service_environment1 = ServiceEnvironmentFactory(
            service__profit_center=self.pc1,
            service__business_line=self.bl1,
        )
        self.service_environment2 = ServiceEnvironmentFactory(
            service__profit_center=self.pc2,
            service__business_line=self.bl2,
        )
        self.service_environments = models.ServiceEnvironment.objects.all()

        # change profit center and business line to test history
        self.service_environment1.service.profit_center = self.pc2
        self.service_environment1.service.business_line = self.bl2
        self.service_environment1.service.save()
        self.maxDiff = None

    @skip("(xor-xor) Skipped due to problems with ralph3_* plugins")
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
                    self.bl1.name,
                    self.bl2.name,
                )),
                'id': self.service_environment1.id,
                'service': self.service_environment1.service.name,
                'service_uid': self.service_environment1.service.ci_uid,
                'environment': self.service_environment1.environment.name,
            },
            self.service_environment2.id: {
                'profit_center': ' - '.join((
                    self.pc2.name,
                    self.pc2.description
                )),
                'business_line': self.bl2.name,
                'id': self.service_environment2.id,
                'service': self.service_environment2.service.name,
                'service_uid': self.service_environment2.service.ci_uid,
                'environment': self.service_environment2.environment.name,
            },
        })
