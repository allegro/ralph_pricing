# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings

from ralph.util import plugin
from ralph_scrooge.plugins.collect._openstack_base import OpenStackBasePlugin


class CeilometerPlugin(OpenStackBasePlugin):
    plugin_name = 'OpenStack Ceilometer'
    metric_tmpl = 'openstack.ceilometer.{}'
    metric_with_prefix_tmpl = 'openstack.ceilometer.{}.{}'
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
def openstack_ceilometer(today, **kwargs):
    """
    Pricing plugin for openstack ceilometer.
    """
    ceilometer = CeilometerPlugin()
    new, total = ceilometer.run_plugin(
            settings.OPENSTACK_CEILOMETER,
            today,
            **kwargs
        )
    return True, 'Ceilometer usages: {} new, {} total'.format(new, total)
