# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph_scrooge.utils.common import get_cache_name, get_queue_name
from ralph_scrooge.utils.worker_job import WorkerJob

logger = logging.getLogger(__name__)


def currency(value):
    """Formats currency as string according to the settings."""

    return '{:,.2f} {}'.format(value or 0, settings.CURRENCY).replace(',', ' ')


class BaseReport(WorkerJob):
    """
    A base class for the reports. Override ``template_name``, ``Form``,
    ``section``, ``get_header`` and ``get_data`` in the specific reports.

    Make sure that ``get_header`` and ``get_data`` are static methods.
    """
    currency = 'PLN'
    queue_name = get_queue_name('scrooge_report')
    cache_name = get_cache_name('scrooge_report')
    cache_section = 'scrooge_report'

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
        logger.info("Report generated")

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
