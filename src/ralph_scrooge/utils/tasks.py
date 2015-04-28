#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from datetime import date
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.db import connection

logger = logging.getLogger(__name__)


def create_dailycosts_partitions():
    """
    Create missing partitions for dailycost table (for 2 months ahead).

    Should be executed periodically (at least once a month).
    """
    today = date.today()
    current = today.replace(day=1)
    current += relativedelta(months=2)
    partitions_dates = {}
    while current >= date(2014, 10, 1):
        key = current.strftime("p_%Y%m%d")
        val = current.strftime("%Y-%m-%d")
        partitions_dates[key] = val
        current -= relativedelta(months=1)

    sql = """
        SELECT
            partition_name
        FROM INFORMATION_SCHEMA.PARTITIONS
        WHERE
            table_schema=%s AND
            table_name='ralph_scrooge_dailycost' AND
            partition_name<>'p_max'
        ORDER BY partition_name ASC
    """
    cursor = connection.cursor()
    cursor.execute(sql, [settings.DATABASES['default']['NAME']])
    current_partitions = []
    for row in cursor.fetchall():
        current_partitions.append(row[0])
    sql_parts = []
    for partition_name, partition_date in sorted(
        partitions_dates.items(),
        key=lambda x: x[0]
    ):
        if partition_name not in current_partitions:
            logger.info('Creating partition {}'.format(partition_name))
            sql_parts.append("""
PARTITION %s VALUES LESS THAN (TO_DAYS('%s')) (
    SUBPARTITION %s_0, SUBPARTITION %s_1
)""" % (partition_name, partition_date, partition_name, partition_name))
    if not sql_parts:
        logger.info('No need to add new partitions')
        return
    sql_parts.append(
        """
PARTITION p_max VALUES LESS THAN (MAXVALUE) (
    SUBPARTITION p_max_0, SUBPARTITION p_max_1
)""")
    sql = """
ALTER TABLE ralph_scrooge_dailycost REORGANIZE PARTITION p_max INTO (%s)
""" % (",".join(sql_parts))
    cursor.execute(sql)
