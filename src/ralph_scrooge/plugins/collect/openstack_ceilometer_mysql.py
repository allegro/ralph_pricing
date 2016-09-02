# -*- coding: utf-8 -*-
"""
Plugin for OpenStack Ceilometer instance usages.

Collect data from OpenStack Ceilometer DB (sample table) and save it into
Scrooge DB.
Collected data is total number of hours instances were running on single day
(grouped by tenant id (project_id) and instance type (meter_id)).
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings

from ralph_scrooge.plugins import plugin
from ralph_scrooge.plugins.collect._openstack_base import OpenStackBasePlugin


class CeilometerMysqlPlugin(OpenStackBasePlugin):
    plugin_name = 'OpenStack Ceilometer'
    metric_tmpl = 'openstack.ceilometer.{}'
    metric_with_prefix_tmpl = 'openstack.ceilometer.{}.{}'
    # query get number of rows each project occur in table and divide it by 6
    # (ceilometer save usages every ~10 minutes) which should give total
    # number of hours instances (under single project) with single type were
    # running
    query = """
    SELECT
        sample.project_id,
        count(sample.id) / 6 AS count,
        meter.name AS flavor
    FROM sample
        left join meter on sample.meter_id = meter.id
    WHERE
        meter.name like "instance:%%"
        and timestamp < {to_ts} and timestamp > {from_ts}
        and cast(timestamp as unsigned) = timestamp
    GROUP BY sample.meter_id, sample.project_id
    """


@plugin.register(chain='scrooge', requires=['service', 'tenant'])
def openstack_ceilometer_mysql(today, **kwargs):
    ceilometer = CeilometerMysqlPlugin()
    new, total = ceilometer.run_plugin(
        settings.OPENSTACK_CEILOMETER,
        today,
        **kwargs
    )
    return True, 'Ceilometer usages: {} new, {} total'.format(new, total)
