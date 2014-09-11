# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import json
import logging

from bob.csvutil import make_csv_response
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _


from ralph_scrooge.models import Statement
from ralph_scrooge.views._worker_view import WorkerView
from ralph_scrooge.views.base import Base

logger = logging.getLogger(__name__)

CACHE_NAME = 'reports_pricing'
if CACHE_NAME not in settings.CACHES:
    CACHE_NAME = 'default'
QUEUE_NAME = 'reports_pricing'
if QUEUE_NAME not in settings.RQ_QUEUES:
    QUEUE_NAME = None
TIMEOUT = getattr(settings, 'PRICING_REPORTS_TIMEOUT', 4 * 3600)  # 4 hours


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


class BaseReport(WorkerView, Base):
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

                if self.progress == 100:
                    self._format_header()
                    if get.get('format', '').lower() == 'csv':
                        self.header = format_csv_header(self.header)
                        return make_csv_response(
                            itertools.chain(self.header, self.data),
                            '{}.csv'.format(self.section),
                        )
                    if (self.allow_statement
                       and get.get('format', '').lower() == 'statement'):
                        self._format_statement_header()
                        self._create_statement()
                else:
                    messages.warning(
                        self.request,
                        _("Please wait for the report "
                          "to finish calculating."),
                    )
        return super(BaseReport, self).get(*args, **kwargs)

    def _format_statement_header(self):
        """
        Format statement header rows.
        """
        self.header = self._convert_fields_to(
            self.header,
            lambda x: (unicode(x[0]), x[1]),
        )
        self.data = self._convert_fields_to(self.data, unicode)

    def _create_statement(self):
        """
        Create statement from current report. Distinguishes different params.
        """
        usage_type, created = Statement.objects.get_or_create(
            start=self.form.cleaned_data['start'],
            end=self.form.cleaned_data['end'],
            forecast=self.form.cleaned_data.get('forecast', False),
            is_active=self.form.cleaned_data.get('is_active', False),
            defaults=dict(
                header=json.dumps(self.header),
                data=json.dumps(self.data),
            )
        )
        if created:
            messages.info(
                self.request,
                _("Statement has been created!"),
            )
        else:
            messages.error(
                self.request,
                _("Statement for this report already exist!"),
            )

    def _convert_fields_to(self, data, unicode_func):
        """
        Convert each of fields to another format by using given function

        :param list data: list of dicts or lists. For example headers
        :param function unicode_func: function to converting each field
        :returns list: The same list as in beginning with converted fields
        :rtype list:
        """
        for i, row in enumerate(data):
            for k, field in enumerate(row):
                data[i][k] = unicode_func(field)
        return data

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

    @classmethod
    def run(cls, **kwargs):
        header = cls.get_header(**kwargs)
        for progress, data in cls.get_data(**kwargs):
            yield progress, (header, data)
        if progress < 100:
            yield 100, (header, data)

    @staticmethod
    def get_data(**kwargs):
        """
        Override this static method to provide data for the report.
        It gets called with the form's data as arguments.
        Make sure it's a static method.
        """
        return []

    @staticmethod
    def get_header(**kwargs):
        """
        Override this static method to provide header for the report.
        It gets called with the form's data as arguments.
        Make sure it's a static method. Result should be list of list, where
        each (sub)list is row in header.
        """
        return []
