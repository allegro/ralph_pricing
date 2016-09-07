# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph.util import plugin
from ralph_scrooge.models import (
    AssetInfo,
    DailyAssetInfo,
    DailyUsage,
    PRICING_OBJECT_TYPES,
    PricingObjectModel,
    ServiceEnvironment,
    UsageType,
    VirtualInfo,
)
from ralph_scrooge.plugins.collect._exceptions import (
    UnknownServiceEnvironmentNotConfiguredError
)
from ralph_scrooge.plugins.collect.utils import get_from_ralph

logger = logging.getLogger(__name__)


def update_virtual_usage(
    daily_virtual_info,
    service_environment,
    usage_type,
    date,
    value,
):
    """
    Creates daily usage of virtual resources.

    :param DailyVirtualInfo daily_virtual_info: daily virtual info
    :param ServiceEnvironment service_environment: ServiceEnvironment object
    :param UsageType usage_type: UsageType object
    :param datetime.date date: processing date
    :param float value: used resources (ex. cores count, memory size etc)
    """
    usage, usage_created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        daily_pricing_object=daily_virtual_info,
        defaults=dict(
            service_environment=service_environment,
        ),
    )
    usage.service_environment = service_environment
    usage.value = value
    usage.save()
    return usage


def get_or_create_model(group_name, data):
    """
    Returns appropriate Pricing Object Model for group_name and Ralph device
    model.
    """
    if not data['type']:
        logger.warning('Type not set for VM {}'.format(data['__str__']))
        return None
    # TODO(mkurek): use update_or_create after migration to Django>=1.7
    model = PricingObjectModel.objects.get_or_create(
        model_id=data['type']['id'],
        type_id=PRICING_OBJECT_TYPES.VIRTUAL,
        defaults=dict(
            name=data['type']['name'],
        )
    )[0]
    model.name = data['type']['name']
    model.save()
    return model


def update_virtual_info(group_name, data, date, service_environment):
    """
    Updates VirtualInfo and creates DailyVirtualInfo object.
    """
    hypervisor = None
    if data.get('hypervisor') is not None:
        # TODO: use id field instead of url (need to implement it in Ralph3)
        hypervisor_id = data['hypervisor']['url'].rstrip('/').rpartition('/')[2]
        try:
            hypervisor = DailyAssetInfo.objects.get(
                asset_info__ralph3_asset_id=hypervisor_id,
                date=date,
            )
        except (AssetInfo.DoesNotExist, DailyAssetInfo.DoesNotExist):
            logger.error('Hypervisor {} not found for VM {}'.format(
                hypervisor_id, data['__str__'],
            ))
    else:
        logger.warning(
            'Empty hypervisor for VM {}'.format(data['__str__'])
        )

    created = False
    try:
        virtual_info = VirtualInfo.objects.get(
            ralph3_id=data['id'],
        )
    except VirtualInfo.DoesNotExist:
        virtual_info = VirtualInfo(
            ralph3_id=data['id'],
            type_id=PRICING_OBJECT_TYPES.VIRTUAL,
        )
        created = True
    virtual_info.service_environment = service_environment
    virtual_info.name = data['hostname']
    virtual_info.model = get_or_create_model(group_name, data)
    virtual_info.save()
    daily_virtual_info = virtual_info.get_daily_pricing_object(date)
    daily_virtual_info.hypervisor = hypervisor
    daily_virtual_info.save()
    return daily_virtual_info, created


def update_virtual_server(group_name, data, usages, date, unknown_service_env):
    """
    Update infomation about single virtual server
    """
    if data.get('service_env'):
        try:
            service_environment = ServiceEnvironment.objects.get(
                service__ci_uid=data['service_env']['service_uid'],
                environment__name=data['service_env']['environment'],
            )
        except ServiceEnvironment.DoesNotExist:
            service_environment = unknown_service_env
            logger.error('Invalid service-env for VM {}: {} - {}'.format(
                data['__str__'], data['service_env']['service_uid'],
                data['service_env']['environment'],
            ))
    else:
        service_environment = unknown_service_env
        logger.error('Unknown service-env for VM {}'.format(data['__str__']))

    daily_virtual_info, created = update_virtual_info(
        group_name,
        data,
        date,
        service_environment,
    )

    # component_list is disk, memory or processors
    # value_key is for example size or cores
    for key, (usage, component_list, value_key) in usages.iteritems():
        value = sum(
            [component[value_key] for component in data[component_list]]
        )
        update_virtual_usage(
            daily_virtual_info,
            service_environment,
            usage,
            date,
            value,
        )
    return created


def get_or_create_usages(group_name):
    """
    Create virtual usage types
    """
    usage_names = {
        'virtual_cores': '{0} Virtual CPU cores'.format(group_name),
        'virtual_memory': '{0} Virtual memory MB'.format(group_name),
        'virtual_disk': '{0} Virtual disk MB'.format(group_name),
    }
    cpu_usage, created = UsageType.objects_admin.get_or_create(
        symbol=usage_names['virtual_cores'].replace(' ', '_').lower(),
        defaults=dict(
            name=usage_names['virtual_cores'],
            average=True,
        ),
    )
    cpu_usage.save()

    memory_usage, created = UsageType.objects_admin.get_or_create(
        symbol=usage_names['virtual_memory'].replace(' ', '_').lower(),
        defaults=dict(
            name=usage_names['virtual_memory'],
            average=True,
        ),
    )
    memory_usage.save()

    disk_usage, created = UsageType.objects_admin.get_or_create(
        symbol=usage_names['virtual_disk'].replace(' ', '_').lower(),
        defaults=dict(
            name=usage_names['virtual_disk'],
            average=True,
        ),
    )
    disk_usage.save()

    usages = {
        'virtual_cores': (cpu_usage, 'processors', 'cores'),
        'virtual_memory': (memory_usage, 'memory', 'size'),
        'virtual_disk': (disk_usage, 'disk', 'size'),
    }
    return usages


def get_unknown_service_env(group_name):
    service_uid, env_name = settings.UNKNOWN_SERVICES_ENVIRONMENTS.get(
        'ralph3_virtual', {}
    ).get(group_name, (None, None))
    unknown_service_env = None
    if service_uid:
        try:
            unknown_service_env = ServiceEnvironment.objects.get(
                service__ci_uid=service_uid,
                environment__name=env_name,
            )
        except ServiceEnvironment.DoesNotExist:
            pass
    if not unknown_service_env:
        raise UnknownServiceEnvironmentNotConfiguredError()
    return unknown_service_env


# virtual usages requires assets plugin to get hypervisors
@plugin.register(chain='scrooge', requires=['ralph3_asset'])
def ralph3_virtual(**kwargs):
    """Updates the virtual usages from Ralph."""

    date = kwargs['today']
    # key in dict is group name (which is propagated to usages names)
    # value is list of services uids (in group)
    created = total = updated = 0
    for group_name, services in settings.VIRTUAL_SERVICES.items():
        try:
            unknown_service_env = get_unknown_service_env(group_name)
        except UnknownServiceEnvironmentNotConfiguredError:
            logger.error(
                'Unknown service-env not configured for "{}"'.format(
                    group_name
                )
            )
            continue
        usages = get_or_create_usages(group_name)
        for service_uid in services:
            for vm in get_from_ralph(
                'virtual-servers', logger,
                query='hypervisor_service={}'.format(service_uid)
            ):
                total += 1
                try:
                    if update_virtual_server(
                        group_name, vm, usages, date, unknown_service_env
                    ):
                        created += 1
                    else:
                        updated += 1
                except:
                    logger.exception(
                        'Exception during processing VM: {}'.format(
                            vm['__str__']
                        )
                    )
            logger.info('`Service {0} done '.format(service_uid))

    return True, 'Virtual: {0} new, {1} updated, {2} errors, {3} total'.format(
        created, updated, total - (created + updated), total,
    )
