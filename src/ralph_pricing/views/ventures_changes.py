# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db import connection
from django.utils.translation import ugettext_lazy as _

from ralph_pricing.views.reports import Report
from ralph_pricing.forms import DevicesVenturesChangesForm


logger = logging.getLogger(__name__)


MYSQL_DAY_SUB = lambda col: 'DATE_SUB({}, INTERVAL 1 DAY)'.format(col)
SQLITE_DAY_SUB = lambda col: "DATE({}, '-1 days')".format(col)


class VenturesChanges(Report):
    template_name = 'ralph_pricing/ventures_daily_usages.html'
    Form = DevicesVenturesChangesForm
    section = 'ventures-changes'
    report_name = _('Ventures Changes Report')
    allow_statement = False

    @classmethod
    def _get_data(cls, start, end, venture=None):
        venture_id = venture.id if venture is not None else None
        query = """
            SELECT dev.sn, dev.barcode, dev.name, dd1.date,
                   v2.name as before_change, v1.name as after_change
            FROM ralph_pricing_dailydevice AS dd1
                JOIN ralph_pricing_dailydevice AS dd2
                JOIN ralph_pricing_venture AS v1
                JOIN ralph_pricing_venture AS v2
                JOIN ralph_pricing_device AS dev
            WHERE dd1.pricing_device_id = dd2.pricing_device_id
                AND dd2.date = {dates_sub}
                AND dd1.date >= '{start}'
                AND dd1.date <= '{end}'
                AND dd1.pricing_venture_id != dd2.pricing_venture_id
                AND v1.id = dd1.pricing_venture_id
                AND v2.id = dd2.pricing_venture_id
                AND dev.id = dd1.pricing_device_id
                AND dev.asset_id IS NOT NULL
        """
        if venture is not None:
            query += """
                AND (
                    dd1.pricing_venture_id = {venture_id}
                    OR dd2.pricing_venture_id = {venture_id}
                )
            """
        query += """
        ORDER BY dd1.date, before_change, after_change
        """
        cursor = connection.cursor()
        if cursor.db.settings_dict['ENGINE'].split('.')[-1] == 'sqlite3':
            dates_sub = SQLITE_DAY_SUB('dd1.date')
        else:
            dates_sub = MYSQL_DAY_SUB('dd1.date')
        cursor.execute(query.format(**locals()))
        return map(list, cursor.fetchall())

    @classmethod
    def get_data(
        cls,
        start,
        end,
        venture=None,
        **kwargs
    ):
        """
        Main method. Create a full report for daily usages by ventures.
        Process of creating report consists of two parts. First of them is
        collecting all required data. Second step is preparing data to render
        in html.

        :returns tuple: percent of progress and report data
        :rtype tuple:
        """
        logger.info(
            "Generating venture changes report from {0} to {1}".format(
                start,
                end,
            )
        )
        yield 100, cls._get_data(start, end, venture)

    @classmethod
    def get_header(cls, start, end, venture, **kwargs):
        """
        Return all headers for daily usages report.

        :returns list: Complete collection of headers for report
        :rtype list:
        """
        logger.debug("Getting headers for report")
        header = [
            [
                _('SN'),
                _('Barcode'),
                _('Device name'),
                _('Change date'),
                _('Venture before change'),
                _('Venture after change'),
            ],
        ]
        return header
