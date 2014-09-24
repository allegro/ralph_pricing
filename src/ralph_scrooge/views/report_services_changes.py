# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.forms import ServicesChangesReportForm
from ralph_scrooge.report.report_services_changes import ServicesChangesReport
from ralph_scrooge.views.base_report import BaseReport


logger = logging.getLogger(__name__)


class ServicesChangesReportView(BaseReport):
    """
    Reports for services
    """
    template_name = 'ralph_scrooge/report_services_changes.html'
    Form = ServicesChangesReportForm
    section = 'services-changes-report'
    report_name = _('Services Changes Report')
    submodule_name = 'services-changes-report'
    allow_statement = False   # temporary
    report = ServicesChangesReport()

    def _format_header(self):
        """
        Format header to make tuple of (text, options dict) for each cell.
        """
        result = {}
        for pricing_object_type, rows in self.header.iteritems():
            pot_result = []
            for row in rows:
                output_row = []
                for col in row:
                    if not isinstance(col, (tuple, list)):
                        col = (col, {})
                    output_row.append(col)
                pot_result.append(output_row)
            result[pricing_object_type] = pot_result
        self.header = result
