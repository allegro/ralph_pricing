# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db import connection
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.models import PRICING_OBJECT_TYPES
from ralph_scrooge.report.base_report import BaseReport


logger = logging.getLogger(__name__)

SQL_DAY_SUB = {
    'sqlite3': lambda col: "DATE({}, '-1 days')".format(col),
    'mysql': lambda col: "DATE_SUB({}, INTERVAL 1 DAY)".format(col),
    'postgresql_psycopg2': lambda col: "{} - INTERVAL '1 day'".format(col),
    'oracle': lambda col: "{} - 1".format(col),
}

ADDITIONAL_DATA = {
    # TODO: add asset model
    PRICING_OBJECT_TYPES.ASSET: {
        'fields': ['ai.barcode', 'ai.sn', 'ai.asset_id'],
        'joins': [
            'JOIN ralph_scrooge_assetinfo AS ai',
        ],
        'joins_conditions': [
            'AND po.id = ai.pricingobject_ptr_id',
        ],
    }
}
ADDITIONAL_HEADERS = {
    PRICING_OBJECT_TYPES.ASSET: [
        _('Barcode'),
        _('SN'),
        _('Asset ID'),
    ],
}


class ServicesChangesReport(BaseReport):
    """
    Report with listing of pricing objects services changes. Contains basic
    information about change such as pricing object info (name in general,
    detailed information for specific pricing object types (ex. sn, barcode for
    asset)), change date and services / environments (before and after change).
    """
    @classmethod
    def _get_types(self):
        types = PRICING_OBJECT_TYPES.__choices__[:]
        types.remove(PRICING_OBJECT_TYPES.DUMMY)
        return types

    @classmethod
    def get_data(
        cls,
        start,
        end,
        service=None,
        **kwargs
    ):
        """
        Main method. Create a full report for devices services changes. Notice
        that this method is a generator. Returns devices services changes
        based on daily pricing objects imprints.

        Report data format:
        {
            pricing_object_type: [
                (
                    id,
                    name,
                    ... (additional fields),
                    change date,
                    service before,
                    environment before,
                    service after,
                    environment after,
                ),
                ...
            ],
            pricing_object_type: [ ... ],
        }

        :returns tuple: percent of progress and report data
        :rtype tuple:
        """
        logger.info(
            "Generating venture changes report ({0}-{1}, service: {2}".format(
                start,
                end,
                service,
            )
        )

        service_environments = None
        if service:
            service_environments = [
                se.id for se in service.environments_services.all()
            ]
        # query explanation:
        # join dailydevice table with self in such way, that joined record's
        # date is one day sooner than original record - then filter only rows
        # that have different venture in two following days
        # after filtering, join ventures and device to get device info and
        # ventures names
        query = """
            SELECT
                po.id,
                po.name,
                {additional_fields}
                dpo1.date,
                s2.name as service_before_change,
                e2.name as environment_before_change,
                s1.name as service_after_change,
                e1.name as environment_after_change
            FROM ralph_scrooge_dailypricingobject AS dpo1
                JOIN ralph_scrooge_dailypricingobject AS dpo2
                JOIN ralph_scrooge_serviceenvironment AS se1
                JOIN ralph_scrooge_serviceenvironment AS se2
                JOIN ralph_scrooge_service AS s1
                JOIN ralph_scrooge_service AS s2
                JOIN ralph_scrooge_environment AS e1
                JOIN ralph_scrooge_environment AS e2
                JOIN ralph_scrooge_pricingobject AS po
                {additional_joins}
            ON dpo1.pricing_object_id = dpo2.pricing_object_id
                AND dpo1.service_environment_id = se1.id
                AND dpo2.service_environment_id = se2.id
                AND dpo1.pricing_object_id = po.id
                AND se1.service_id = s1.id
                AND se2.service_id = s2.id
                AND se1.environment_id = e1.id
                AND se2.environment_id = e2.id
                {additional_joins_conditions}
            WHERE dpo2.date = {dates_sub}
                AND dpo1.date >= '{start}'
                AND dpo1.date <= '{end}'
                AND dpo1.service_environment_id != dpo2.service_environment_id
                AND po.type_id = {pricing_object_type_id}
        """
        if service_environments is not None:
            service_environments_set = ','.join(map(str, service_environments))
            query += """
                AND (
                    dpo1.service_environment_id IN ({service_environments_set})
                    OR
                    dpo2.service_environment_id IN ({service_environments_set})
                )
            """
        query += """
        ORDER BY dpo1.date, service_before_change, service_after_change;
        """
        cursor = connection.cursor()
        # all db engines has differ way of days subtraction syntax
        db_engine = cursor.db.settings_dict['ENGINE'].split('.')[-1]
        dates_sub = SQL_DAY_SUB[db_engine]('dpo1.date')
        result = {}

        progress = 0
        types = cls._get_types()
        for pricing_object_type in types:
            additional = ADDITIONAL_DATA.get(pricing_object_type, {})
            additional_fields = ','.join(additional.get('fields', []))
            if additional_fields:
                additional_fields += ','
            additional_joins = '\n'.join(additional.get('joins', []))
            additional_joins_conditions = '\n'.join(additional.get(
                'joins_conditions',
                []
            ))
            pricing_object_type_id = pricing_object_type.id
            q = query.format(**locals())
            cursor.execute(q)
            result[pricing_object_type] = list(cursor.fetchall())
            progress += 100.0 / len(types)
            yield progress, result
        if progress < 100:
            yield 100, result

    @classmethod
    def get_header(cls, **kwargs):
        """
        Return all headers for services changes report. For each of pricing
        object types (except dummy) returns list of columns headers. Some
        pricing object types requires additional headers (and fields), ex.
        assets, some types are using default headers (without additional
        columns).

        :returns dict: Complete collection of headers for report
        :rtype dict:
        """
        logger.debug("Getting headers for ventures changes report")
        types = cls._get_types()
        default = [
            _('ID'),
            _('Name'),
            # PLACE FOR ADDITIONAL HEADERS
            _('Change date'),
            _('Service before change'),
            _('Environment before change'),
            _('Service after change'),
            _('Environment after change'),
        ]
        header = {}
        for pricing_object_type in types:
            additional = ADDITIONAL_HEADERS.get(pricing_object_type, [])
            tmp = default
            if additional:
                tmp = default[:]
                tmp[2:2] = additional  # insert after name, before date
            header[pricing_object_type] = [tmp]
        return header
