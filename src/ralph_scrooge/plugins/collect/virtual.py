# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph.util import plugin, api_scrooge
from ralph_scrooge.models import (
    AssetInfo,
    DailyAssetInfo,
    DailyUsage,
    UsageType,
    PRICING_OBJECT_TYPES,
    ServiceEnvironment,
    VirtualInfo,
)


logger = logging.getLogger(__name__)


class ServiceUidCannotBeNoneError(Exception):
    """
    Raise this exception when incomming data have no service ci uid
    """
    pass


class EnvironmentCannotBeNoneError(Exception):
    """
    Raise this exception when incomming data have no environment
    """
    pass


class DeviceIdCannotBeNoneError(Exception):
    """
    Raise this exception when incomming data have no environment
    """
    pass


def update_virtual_usage(
    hypervisor,
    service_environment,
    usage_type,
    data,
    date,
    value,
):
    """
    Update single virtual device. Create daily usage and virtual info objects

    :param object hypervisor: DailyAssetInfo object
    :param object service_environment: ServiceEnvironment object
    :param object usage_type: UsageType object
    :param dict data: Dict with data from ralph
    :param datetime date: Date for which daily objects will create
    :param float value: count of usage
    """
    try:
        virtual_info = VirtualInfo.objects.get(
            device_id=data['device_id'],
        )
    except VirtualInfo.DoesNotExist:
        virtual_info = VirtualInfo(
            device_id=data['device_id'],
            type_id=PRICING_OBJECT_TYPES.VIRTUAL,
        )
    virtual_info.service_environment = service_environment
    virtual_info.name = data['name']
    virtual_info.save()
    daily_virtual_info = virtual_info.get_daily_pricing_object(date)
    daily_virtual_info.hypervisor = hypervisor
    daily_virtual_info.save()

    usage, usage_created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        daily_pricing_object=daily_virtual_info,
        service_environment=service_environment,
    )
    usage.value = value
    usage.save()


def update(data, usages, date):
    """
    Check if everything is correct and run update_virtual_usage

    :param dict usages: dict with UsageType objects
    :param dict data: Dict with data from ralph
    :param datetime date: Date for which daily objects will create
    """
    if data.get('device_id') is None:
        raise DeviceIdCannotBeNoneError()
    if data.get('service_id') is None:
        raise ServiceUidCannotBeNoneError()
    elif data.get('environment_id') is None:
        raise EnvironmentCannotBeNoneError()
    else:
        service_environment = ServiceEnvironment.objects.get(
            service__ci_id=data.get('service_id'),
            environment__ci_id=data.get('environment_id'),
        )

    hypervisor = None
    if data.get('hypervisor_id') is not None:
        asset_info = AssetInfo.objects.get(
            device_id=data.get('hypervisor_id'),
        )
        hypervisor = DailyAssetInfo.objects.get(
            asset_info=asset_info,
            date=date,
        )
    else:
        logger.warning(
            'For device {0} hypervisor is none'.format(
                data['device_id'],
            ),
        )

    for key, usage in usages.iteritems():
        update_virtual_usage(
            hypervisor,
            service_environment,
            usage,
            data,
            date,
            data.get(key),
        )


def get_or_create_usages(usage_names):
    """
    Creates virtual usage types

    :returns dict: Dict with usage types
    :rtype dict:
    """
    cpu_usage, created = UsageType.objects.get_or_create(
        symbol=usage_names['virtual_cores'].replace(' ', '_').lower(),
        defaults=dict(
            name=usage_names['virtual_cores'],
            average=True,
        ),
    )
    cpu_usage.save()

    memory_usage, created = UsageType.objects.get_or_create(
        symbol=usage_names['virtual_memory'].replace(' ', '_').lower(),
        defaults=dict(
            name=usage_names['virtual_memory'],
            average=True,
        ),
    )
    memory_usage.save()

    disk_usage, created = UsageType.objects.get_or_create(
        symbol=usage_names['virtual_disk'].replace(' ', '_').lower(),
        defaults=dict(
            name=usage_names['virtual_disk'],
            average=True,
        ),
    )
    disk_usage.save()

    usages = {
        'virtual_cores': cpu_usage,
        'virtual_memory': memory_usage,
        'virtual_disk': disk_usage,
    }
    return usages


# virtual usages requires assets plugin to get proper devices
@plugin.register(chain='scrooge', requires=['asset'])
def virtual(**kwargs):
    """Updates the virtual usages from Ralph."""

    date = kwargs['today']
    # key in dict is group name (which is propagated to usages names)
    # value is list of services uids (in group)
    updated = total = 0
    for group_name, services in settings.VIRTUAL_SERVICES.items():
        usage_names = {
            'virtual_cores': '{0} Virtual CPU cores'.format(group_name),
            'virtual_memory': '{0} Virtual memory MB'.format(group_name),
            'virtual_disk': '{0} Virtual disk MB'.format(group_name),
        }
        usages = get_or_create_usages(usage_names)
        for service_uid in services:
            for data in api_scrooge.get_virtual_usages(service_uid):
                total += 1
                try:
                    update(data, usages, date)
                    updated += 1
                except AssetInfo.DoesNotExist:
                    logger.error(
                        'AssetInfo with device id {0} does not exist'.format(
                            data['hypervisor_id'],
                        ),
                    )
                except DailyAssetInfo.DoesNotExist:
                    logger.error('DailyAssetInfo does not exist')
                except ServiceEnvironment.DoesNotExist:
                    logger.error(
                        'Service {0} does not exist'.format(
                            data['service_id'],
                        ),
                    )
                except EnvironmentCannotBeNoneError:
                    logger.warning(
                        'For device {0} environment is none'.format(
                            data['device_id'],
                        ),
                    )
                except ServiceUidCannotBeNoneError:
                    logger.warning(
                        'For device {0} service ci uid is none'.format(
                            data['device_id'],
                        ),
                    )
                except DeviceIdCannotBeNoneError:
                    logger.warning('Device id cannot be None')
            logger.info('`Service {0} done '.format(service_uid))

    return True, 'Virtual: {0} new, {1} updated, {2} total'.format(
        None,
        updated,
        total,
    )
