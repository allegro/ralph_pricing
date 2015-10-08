# -*- coding: utf-8 -*-
"""
Plugin for OpenStack Cinder Volumes usages.

Collect data from OpenStack Cinder DB and save it into Scrooge DB. Collected
data is number of GBs tenant used in single day (when volume is used for part
of the day, it's size is decreased proportionally).

If you want to charge tenant for usage of volume but volume size is not
relevant add volume type name to OPENSTACK_CINDER_VOLUMES_DONT_CHARGE_FOR_SIZE
in your settings file.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph.util import plugin
from ralph_scrooge.plugins.collect._openstack_base import OpenStackBasePlugin

logger = logging.getLogger(__name__)


class CinderVolumesPlugin(OpenStackBasePlugin):
    plugin_name = 'OpenStack Cinder volumes'
    metric_tmpl = 'openstack.volume.{}'
    metric_with_prefix_tmpl = metric_tmpl + '.{}'
    query = """
    SELECT
        volumes.id,
        volumes.display_name,
        volumes.project_id,
        TIME_TO_SEC(TIMEDIFF(
            CAST(LEAST(IFNULL(
                volumes.deleted_at,
                '{to_ts}'
            ), '{to_ts}') as DATETIME),
            CAST(GREATEST(volumes.created_at, '{from_ts}') as DATETIME)
        )) * volumes.size / (60.0 * 60) AS 'usage',
        volumes.host AS 'volume_host',
        volume_types.name AS 'metric_name'
    FROM
        volumes
    LEFT JOIN volume_types ON volumes.volume_type_id = volume_types.id
    WHERE
        volumes.created_at <= '{to_ts}' and
        (volumes.deleted_at IS NULL OR volumes.deleted_at >= '{from_ts}')
    """

    def get_usages(self, *args, **kwargs):
        result = super(CinderVolumesPlugin, self).get_usages(*args, **kwargs)
        for (
            volume_id, volume_display_name, tenant_id, value, volume_host,
            volume_type_name
        ) in result:
            # Volume type is fetched from volume_types table or from hostname
            # of volumes.host if volume type is NULL
            if not volume_type_name and volume_host:
                volume_type_name = volume_host.split('@')[-1]
            # cannot assign any volume type - skip this volume
            if not volume_type_name:
                logger.warning(
                    'Volume type not found for volume {}'.format(volume_id)
                )
                continue
            if volume_type_name in settings.OPENSTACK_CINDER_VOLUMES_DONT_CHARGE_FOR_SIZE:  # noqa
                value = 1.0
            yield (
                tenant_id,
                value,
                volume_type_name,
                '{}: {}'.format(volume_id, volume_display_name)
            )

    def _format_date(self, d):
        return d


@plugin.register(chain='scrooge', requires=['service', 'tenant'])
def openstack_cinder_volumes_mysql(today, **kwargs):
    cinder_volumes = CinderVolumesPlugin()
    new, total = cinder_volumes.run_plugin(
        settings.OPENSTACK_CINDER_VOLUMES,
        today,
        **kwargs
    )
    return True, 'Cinder volumes usages: {} new, {} total'.format(new, total)
