# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.forms import ServicesUsagesReportForm
from ralph_scrooge.report.report_services_usages import ServicesUsagesReport
from ralph_scrooge.views.base_report import BaseReport


logger = logging.getLogger(__name__)


class ServicesUsagesReportView(BaseReport):
    """
    Report with usages of resources (usage types) by service environments
    per days
    """
    template_name = 'ralph_scrooge/report_services_usages.html'
    Form = ServicesUsagesReportForm
    section = 'services-usages-report'
    report_name = _('Services Usages Report')
    submodule_name = 'services-usages-report'
    allow_statement = False   # temporary
    report = ServicesUsagesReport()
