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

SQL_DAY_SUB = {
    'sqlite3': lambda col: "DATE({}, '-1 days')".format(col),
    'mysql': lambda col: "DATE_SUB({}, INTERVAL 1 DAY)".format(col),
    'postgresql_psycopg2': lambda col: "{} - INTERVAL '1 day'".format(col),
    'oracle': lambda col: "{} - 1".format(col),
}


class VenturesChanges(Report):
    """
    Report with listing of devices ventures changes. Contains basic information
    about change such as device info (sn, barcode, name), change date and
    ventures (before and after change).
    """
    template_name = 'ralph_pricing/ventures_daily_usages.html'
    Form = DevicesVenturesChangesForm
    section = 'ventures-changes'
    report_name = _('Ventures Changes Report')
    allow_statement = False

    @classmethod
    def get_data(
        cls,
        start,
        end,
        venture=None,
        use_subventures=True,
        **kwargs
    ):
        """
        Main method. Create a full report for devices ventures changes. Notice
        that this method is a generator. Returns devices ventures changes
        based on daily devices imprints.

        :returns tuple: percent of progress and report data
        :rtype tuple:
        """
        logger.info(
            "Generating venture changes report ({0}-{1}, venture: {2}".format(
                start,
                end,
                venture,
            )
        )

        ventures = None
        if venture:
            ventures = [venture.id]
            if use_subventures:
                ventures += [v.id for v in venture.get_descendants()]

        # query explanation:
        # join dailydevice table with self in such way, that joined record's
        # date is one day sooner than original record - then filter only rows
        # that have different venture in two following days
        # after filtering, join ventures and device to get device info and
        # ventures names
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
        if ventures is not None:
            ventures_set = ', '.join(map(str, ventures))
            query += """
                AND (
                    dd1.pricing_venture_id IN ({ventures_set})
                    OR dd2.pricing_venture_id IN ({ventures_set})
                )
            """
        query += """
        ORDER BY dd1.date, before_change, after_change;
        """
        cursor = connection.cursor()
        # all db engines has differ way of days subtraction syntax
        db_engine = cursor.db.settings_dict['ENGINE'].split('.')[-1]
        dates_sub = SQL_DAY_SUB[db_engine]('dd1.date')
        cursor.execute(query.format(**locals()))
        yield 100, map(list, cursor.fetchall())

    @classmethod
    def get_header(cls, start, end, venture, **kwargs):
        """
        Return all headers for ventures changes report.

        :returns list: Complete collection of headers for report
        :rtype list:
        """
        logger.debug("Getting headers for ventures changes report")
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
