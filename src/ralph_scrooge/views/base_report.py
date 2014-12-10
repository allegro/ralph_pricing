# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import logging

from bob.csvutil import make_csv_response
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.views.base import Base

logger = logging.getLogger(__name__)


def currency(value):
    """Formats currency as string according to the settings."""

    return '{:,.2f} {}'.format(value or 0, settings.CURRENCY).replace(',', ' ')


def format_csv_header(header):
    """
    Format csv header rows. Insert empty cells to show rowspan and colspan.
    """
    result = []
    for row in header:
        output_row = []
        for col in row:
            output_row.append(col[0])
            for colspan in range((col[1].get('colspan') or 1) - 1):
                output_row.append('')
        result.append(output_row)
    # rowspans
    for row_num, row in enumerate(header):
        i = 0
        for col in row:
            if 'rowspan' in col[1]:
                for rowspan in range(1, (col[1]['rowspan'] or 1)):
                    result[row_num + rowspan].insert(i, '')
            i += col[1].get('colspan', 1)
    return result


class BaseReport(Base):
    """
    A base class for the reports. Override ``template_name``, ``Form``,
    ``section``, ``get_header`` and ``get_data`` in the specific reports.

    Make sure that ``get_header`` and ``get_data`` are static methods.
    """
    template_name = None
    Form = None
    initial = None
    section = ''
    report_name = ''
    currency = 'PLN'
    allow_statement = True
    allow_csv_download = True
    report = None
    refresh_time = 10  # time to refresh page to check for result (in seconds)

    def __init__(self, *args, **kwargs):
        super(BaseReport, self).__init__(*args, **kwargs)
        self.data = []
        self.header = []
        self.form = None
        self.progress = 0
        self.got_query = False

    def get(self, *args, **kwargs):
        get = self.request.GET
        if get:
            self.form = self.Form(get)
            self.got_query = True
        else:
            self.form = self.Form(initial=self.initial)
        if self.form.is_valid():
            if 'clear' in get:
                self.progress = 0
                self.got_query = False
                self._clear_cache(**self.form.cleaned_data)
                messages.success(
                    self.request, "Cache cleared for this report.",
                )
            else:
                self.progress, result = self.run_on_worker(
                    **self.form.cleaned_data
                )
                if result:
                    self.header, self.data = result
                    self._format_header()

                self.progress = round(self.progress, 0)
                if self.progress == 100:
                    if get.get('format', '').lower() == 'csv':
                        self.header = format_csv_header(self.header)
                        return make_csv_response(
                            itertools.chain(self.header, self.data),
                            '{}.csv'.format(self.section),
                        )
                else:
                    messages.warning(
                        self.request,
                        _("Please wait for the report "
                          "to finish calculating."),
                    )
        return super(BaseReport, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BaseReport, self).get_context_data(**kwargs)
        context.update({
            'progress': self.progress,
            'data': self.data,
            'header': self.header,
            'section': self.section,
            'report_name': self.report_name,
            'form': self.form,
            'got_query': self.got_query,
            'allow_statement': self.allow_statement,
            'allow_csv_download': self.allow_csv_download,
            'refresh_time': self.refresh_time
        })
        return context

    def _format_header(self):
        """
        Format header to make tuple of (text, options dict) for each cell.
        """
        result = []
        for row in self.header:
            output_row = []
            for col in row:
                if not isinstance(col, (tuple, list)):
                    col = (col, {})
                output_row.append(col)
            result.append(output_row)
        self.header = result

    def run_on_worker(self, **kwargs):
        return self.report.run_on_worker(**kwargs)

    def _clear_cache(self, **kwargs):
        return self.report._clear_cache(**kwargs)
