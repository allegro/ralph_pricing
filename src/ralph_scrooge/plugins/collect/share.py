# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph.util.api_scrooge import get_shares
from ralph.util import plugin
from ralph_scrooge.models import (
    DailyUsage,
    AssetInfo,
    UsageType,
)


logger = logging.getLogger(__name__)


class UnknownMountDeviceIdError(Exception):
    """
    Raise this exception when there is no mount device id in data
    """
    pass


class AssetInfoDoesNotExistError(Exception):
    """
    Raise this exception when asset info does not exist
    """
    pass


def update_usage(asset_info, usage_type, data, date):
    """
    Saves single DailyUsage of shares usage type.
    """
    daily_pricing_object = asset_info.get_daily_pricing_object(date=date)
    usage, created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        service_environment=asset_info.service_environment,
        daily_pricing_object=daily_pricing_object,
    )
    usage.value += data['size']
    usage.save()


def update(usage_type, data, date):
    """
    Updates single record according to information in data.
    """
    if data['mount_device_id'] is None:
        raise UnknownMountDeviceIdError()
    try:
        asset_info = AssetInfo.objects.get(
            device_id=data['mount_device_id'],
        )
    except AssetInfo.DoesNotExist:
        raise AssetInfoDoesNotExistError()

    update_usage(asset_info, usage_type, data, date)
    return True


def get_usage(usage_name):
    """
    Returns usage type for specific shares
    """
    usage_type, created = UsageType.objects.get_or_create(
        symbol=usage_name.replace(' ', '_').lower(),
        defaults=dict(
            name=usage_name,
            average=True,
        ),
    )
    return usage_type


@plugin.register(chain='scrooge', requires=['asset', 'virtual'])
def share(**kwargs):
    """Updates the disk share usages from Ralph."""

    date = kwargs['today']
    updated = total = 0

    for group_name, services in settings.SHARE_SERVICES.iteritems():
        usage_type = get_usage(
            'Disk Share {0}'.format(group_name),
        )

        logger.info('Processing group {}'.format(group_name))

        # delete all previous records
        DailyUsage.objects.filter(type=usage_type, date=date).delete()

        for service_uid in services:
            for data in get_shares(
                service_uid=service_uid,
                include_virtual=False,
            ):
                total += 1
                try:
                    update(usage_type, data, date)
                    updated += 1
                except UnknownMountDeviceIdError:
                    logger.warning(
                        '{0} - {1} is mounted nowhere'.format(
                            data['storage_device_id'],
                            data['label'],
                        ),
                    )
                except AssetInfoDoesNotExistError:
                    logger.error(
                        'AssetInfo {} not found'.format(
                            data['mount_device_id'],
                        ),
                    )
    return True, '{0} new, {1} updated, {2} total'.format(
        None,
        updated,
        total,
    )
