# -*- coding: utf-8 -*-
"""
Plugin for OpenStack Nova instance usages.

Collect data from OpenStack Nova DB and save it into Scrooge DB. Collected
data is total number of hours instances were running on single day (grouped
by tenant id (project_id) and instance type (instance_type_id))
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings

from ralph_scrooge.utils import plugin
from ralph_scrooge.plugins.collect._openstack_base import OpenStackBasePlugin


class NovaInstancePlugin(OpenStackBasePlugin):
    plugin_name = 'OpenStack Nova instances'
    metric_tmpl = 'openstack.nova.{}'
    metric_with_prefix_tmpl = metric_tmpl + '.{}'
    query = """
    SELECT
        instances.project_id,
        SUM(TIME_TO_SEC(TIMEDIFF(
            CAST(LEAST(IFNULL(
                instances.deleted_at,
                '{to_ts}'
            ), '{to_ts}') as DATETIME),
            CAST(GREATEST(instances.created_at, '{from_ts}') as DATETIME)
        )) / (60.0 * 60)) as work_time,
        instance_types.name AS metric_name
    FROM instances
    LEFT JOIN instance_types ON instances.instance_type_id=instance_types.id
    WHERE
        instances.created_at <= '{to_ts}' and
        (instances.deleted_at IS NULL OR instances.deleted_at >= '{from_ts}')
    GROUP BY instances.project_id, instance_type_id;
    """

    def _format_date(self, d):
        return d


@plugin.register(chain='scrooge', requires=['service', 'tenant'])
def openstack_nova_instance(today, **kwargs):
    nova_instances = NovaInstancePlugin()
    new, total = nova_instances.run_plugin(
        settings.OPENSTACK_NOVA_INSTANCES,
        today,
        **kwargs
    )
    return True, 'Nova instances usages: {} new, {} total'.format(new, total)
