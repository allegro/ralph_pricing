# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.views.base_report import BaseReport
from ralph_scrooge.forms import ServicesCostsReportForm
from ralph_scrooge.report.report_services_costs import ServicesCostsReport


logger = logging.getLogger(__name__)


class ServicesCostsReportView(BaseReport):
    """
    Reports for services
    """
    template_name = 'ralph_scrooge/report_services_costs.html'
    Form = ServicesCostsReportForm
    section = 'services-costs-report'
    report_name = _('Services Costs Report')
    submodule_name = 'services-costs-report'
    allow_statement = False   # temporary
    report = ServicesCostsReport()
