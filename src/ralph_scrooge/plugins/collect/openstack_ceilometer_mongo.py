# -*- coding: utf-8 -*-
"""
Plugin for OpenStack Ceilometer usages using MongoDB.

Collect data from OpenStack Ceilometer and save it into Scrooge DB.
Unlike MySQL version of Scrooge Ceilometer plugin, this plugin get all usages
(cumulative, gauge and delta) from Ceilometer.

For more information about ceilometer visit:
http://docs.openstack.org/developer/ceilometer/
https://www.mirantis.com/blog/openstack-metering-using-ceilometer/
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from itertools import chain

from django.conf import settings
from pymongo import MongoClient

from ralph_scrooge.plugins import plugin_runner
from ralph_scrooge.plugins.collect.openstack_ceilometer_mysql import (
    CeilometerMysqlPlugin,
)


logger = logging.getLogger(__name__)


class CeilometerMongoPlugin(CeilometerMysqlPlugin):
    def get_usages(self, date, connection_string):
        """
        Get usages from OpenStack ceilometer using mongo client.
        """
        date_from, date_to = self._get_dates_from_to(date)
        client = MongoClient(connection_string)
        db = client.ceilometer
        cumulative_data = db.meter.aggregate([
            {
                "$match": {
                    "timestamp": {"$gt": date_from, "$lt": date_to},
                    "counter_type": "cumulative",
                }
            },
            {
                "$group": {
                    "_id": {
                        "project_id": "$project_id",
                        "counter_name": "$counter_name"
                    },
                    "counter_max": {"$max": "$counter_volume"},
                    "counter_min": {"$min": "$counter_volume"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "tenant_id": "$_id.project_id",
                    "metric_name": "$_id.counter_name",
                    "value": {
                        "$subtract": ["$counter_max", "$counter_min"]
                    },
                }
            },
        ])
        gauge_data = db.meter.aggregate([
            {
                "$match": {
                    "timestamp": {"$gt": date_from, "$lt": date_to},
                    "counter_type": "gauge",
                }
            },
            {
                "$group": {
                    "_id": {
                        "project_id": "$project_id",
                        "counter_name": "$counter_name"
                    },
                    "total": {"$sum": "$counter_volume"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "tenant_id": "$_id.project_id",
                    "metric_name": "$_id.counter_name",
                    "value": {"$divide": ["$total", 144]},
                    # 24 * 6 (openstack saves data every ~10 minutes)
                }
            },
        ])
        delta_data = db.meter.aggregate([
            {
                "$match": {
                    "timestamp": {"$gt": date_from, "$lt": date_to},
                    "counter_type": "delta",
                }
            },
            {
                "$group": {
                    "_id": {
                        "project_id": "$project_id",
                        "counter_name": "$counter_name"
                    },
                    "value": {"$sum": "$counter_volume"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "tenant_id": "$_id.project_id",
                    "metric_name": "$_id.counter_name",
                    "value": 1,
                }
            },
        ])

        return list(chain.from_iterable(map(
            lambda data: [
                    (
                        x['tenant_id'],
                        x['value'],
                        x['metric_name']
                    )
                    for x in data['result']
                    ],
            [cumulative_data, gauge_data, delta_data])
            ))


@plugin_runner.register(chain='scrooge', requires=['service', 'tenant'])
def openstack_ceilometer_mongo(today, **kwargs):
    ceilometer = CeilometerMongoPlugin()
    new, total = ceilometer.run_plugin(
        settings.OPENSTACK_CEILOMETER,
        today,
        **kwargs
    )
    return True, 'Ceilometer usages: {} new, {} total'.format(new, total)
