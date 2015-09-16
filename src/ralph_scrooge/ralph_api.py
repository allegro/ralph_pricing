# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def get_virtual_usages(parent_service_uid=None):
    """Yields dicts reporting the number of virtual cores, memory and disk."""
    return []

    # devices = Device.objects.filter(
    #     model__type=DeviceType.virtual_server
    # ).select_related('model')
    # if parent_service_uid:
    #     devices = devices.filter(
    #         parent__service__uid=parent_service_uid,
    #     )
    # for device in devices:
    #     cores = device.get_core_count()
    #     memory = device.memory_set.aggregate(db.Sum('size'))['size__sum']
    #     disk = device.storage_set.aggregate(db.Sum('size'))['size__sum']
    #     shares_size = sum(
    #         mount.get_size()
    #         for mount in device.disksharemount_set.all()
    #     )
    #     for system in device.operatingsystem_set.all():
    #         if not disk:
    #             disk = max((system.storage or 0) - shares_size, 0)
    #         if not cores:
    #             cores = system.cores_count
    #         if not memory:
    #             memory = system.memory
    #     yield {
    #         'name': device.name,
    #         'device_id': device.id,
    #         'venture_id': device.venture_id,
    #         'service_id': device.service_id,
    #         'environment_id': device.device_environment_id,
    #         'hypervisor_id': device.parent_id,
    #         'virtual_cores': cores or 0,
    #         'virtual_memory': memory or 0,
    #         'virtual_disk': disk or 0,
    #         'model_id': device.model_id,
    #         'model_name': device.model.name,
    #     }


def get_shares(service_uid=None, include_virtual=True):
    """
    Yields dicts reporting the storage shares mounts.

    :param service_uid: if passed, only share mounts from shares with
        storage device in this service will be returned
    :param include_virtual: if False, virtual share mounts will be excluded
        from result
    """
    return []

    # shares_mounts = DiskShareMount.objects.select_related(
    #     'share',
    # )
    # if not include_virtual:
    #     shares_mounts = shares_mounts.filter(is_virtual=False)
    # if service_uid:
    #     shares_mounts = shares_mounts.filter(
    #         share__device__service__uid=service_uid,
    #     )
    # for mount in shares_mounts:
    #     yield {
    #         'storage_device_id': mount.share.device_id,
    #         'mount_device_id': mount.device_id,
    #         'label': mount.share.label,
    #         'size': mount.get_size(),
    #     }


# def get_ip_info(ipaddress):
#     """Returns device information by IP address"""
#     result = {}
#     try:
#         ip = IPAddress.objects.select_related().get(address=ipaddress)
#     except IPAddress.DoesNotExist:
#         pass
#     else:
#         if ip.venture is not None:
#             result['venture_id'] = ip.venture.id
#         if ip.device is not None:
#             result['device_id'] = ip.device.id
#             if ip.device.venture is not None:
#                 result['venture_id'] = ip.device.venture.id
#     return result


def get_ip_addresses(only_public=False):
    """Yileds available IP addresses"""
    return []
    # ips = IPAddress.objects.filter(is_public=only_public)
    # return {ip.address: ip.venture.id if ip.venture else None for ip in ips}


def get_fc_cards():
    return []
    # for fc in FibreChannel.objects.filter(device__deleted=False).values(
    #     'id',
    #     'device_id'
    # ):
    #     yield {
    #         'id': fc['id'],
    #         'device_id': fc['device_id'],
    #     }


# class get_environments(Getter):
#     Model = DeviceEnvironment
#     fields = [
#         ('ci_id', 'id'),
#         ('ci_uid', 'uid'),
#         'name'
#     ]
def get_environments():
    return []


def get_openstack_tenants(model_name=None):
    return []
    # tenants = Device.objects.filter(
    #     sn__startswith='openstack',
    #     model__type=DeviceType.cloud_server
    # )
    # if model_name:
    #     tenants = tenants.filter(model__name=model_name)
    # for tenant in tenants:
    #     yield {
    #         'device_id': tenant.id,
    #         'tenant_id': tenant.sn[len('openstack-'):],
    #         'service_id': tenant.service_id,
    #         'environment_id': tenant.device_environment_id,
    #         'name': tenant.name,
    #         'model_id': tenant.model_id,
    #         'model_name': tenant.model.name,
    #         'remarks': tenant.remarks,
    #     }


def get_blade_servers():
    return []
    # for blade_server in Device.objects.filter(
    #     model__type=DeviceType.blade_server,
    # ):
    #     yield {
    #         'device_id': blade_server.id,
    #     }


# class get_vips(Getter):
#     Model = LoadBalancerVirtualServer

#     fields = [
#         ('vip_id', 'id'),
#         'name',
#         ('ip_address', 'address__address'),
#         ('type_id', 'load_balancer_type_id'),
#         ('type', 'load_balancer_type__name'),
#         'service_id',
#         ('environment_id', 'device_environment_id'),
#         'device_id',
#         'port',
#     ]

#     def __init__(self, parent_service_uid=None, load_balancer_type=None):
#         self.parent_service_uid = parent_service_uid
#         self.load_balancer_type = load_balancer_type

#     def get_queryset(self):
#         result = super(get_vips, self).get_queryset()
#         if self.parent_service_uid:
#             result = result.filter(
#                 device__service__uid=self.parent_service_uid
#             )
#         if self.load_balancer_type:
#             result = result.filter(
#                 load_balancer_type__name=self.load_balancer_type
#             )
#         return result
def get_vips():
    return []


# class get_databases(Getter):
#     Model = Database

#     fields = [
#         ('database_id', 'id'),
#         'name',
#         ('type_id', 'database_type_id'),
#         ('type', 'database_type__name'),
#         'service_id',
#         ('environment_id', 'device_environment_id'),
#         'parent_device_id',
#     ]

#     def __init__(self, parent_service_uid=None, database_type=None):
#         self.parent_service_uid = parent_service_uid
#         self.database_type = database_type

#     def get_queryset(self):
#         result = super(get_databases, self).get_queryset()
#         if self.parent_service_uid:
#             result = result.filter(
#                 parent_device__service__uid=self.parent_service_uid
#             )
#         if self.database_type:
#             result = result.filter(
#                 database_type__name=self.database_type
#             )
#         return result
def get_databases():
    return []


# CMDB
# class get_business_lines(Getter):
#     """
#     Returns Business Lines from CMDB (CIs with type Business Line)
#     """
#     Model = CI

#     @property  # When testing the table won't exist during import
#     def filters(self):
#         return {'type': CIType.objects.get(name='BusinessLine')}

#     fields = [
#         ('ci_id', 'id'),
#         ('ci_uid', 'uid'),
#         'name',
#     ]
def get_business_lines():
    return []


def get_profit_centers():
    """
    Returns Profit Centers from CMDB (CIs with type Profit Center)
    """
    return []
    # profit_center_type = CIType.objects.get(name='ProfitCenter')
    # business_line_type = CIType.objects.get(name='BusinessLine')
    # for profit_center in CI.objects.filter(type=profit_center_type):
    #     try:
    #         description = profit_center.ciattributevalue_set.get(
    #             attribute__name='description'
    #         ).value
    #     except CIAttributeValue.DoesNotExist:
    #         description = None
    #     business_line = profit_center.child.filter(
    #         parent__type=business_line_type
    #     ).values_list('parent__id', flat=True)
    #     yield {
    #         'ci_id': profit_center.id,
    #         'ci_uid': profit_center.uid,
    #         'name': profit_center.name,
    #         'description': description,
    #         'business_line': business_line[0] if business_line else None,
    #     }


# class get_owners(Getter):
#     """
#     Returns CIOwners from CMDB
#     """
#     Model = CIOwner
#     fields = ['id', 'profile_id']
def get_owners():
    return []


def get_services(only_calculated_in_scrooge=False):
    """
    Returns Services (CIs with type Service) with additional information like
    owners, business line etc.
    """
    return []
    # service_type = CIType.objects.get(name='Service')
    # profit_center_type = CIType.objects.get(name='ProfitCenter')
    # environment_type = CIType.objects.get(name='Environment')
    # for service in CI.objects.filter(
    #     type=service_type
    # ).select_related('relations'):
    #     try:
    #         calculate_in_scrooge = service.ciattributevalue_set.get(
    #             attribute_id=7
    #         ).value
    #     except CIAttributeValue.DoesNotExist:
    #         calculate_in_scrooge = False
    #     if only_calculated_in_scrooge and not calculate_in_scrooge:
    #         continue

    #     profit_center = service.child.filter(
    #         parent__type=profit_center_type
    #     ).values_list('parent__id', flat=True)
    #     # TODO: verify relation
    #     environments = service.parent.filter(
    #         child__type=environment_type,
    #     )
    #     try:
    #         symbol = service.ciattributevalue_set.get(
    #             attribute__name='symbol'
    #         ).value
    #     except CIAttributeValue.DoesNotExist:
    #         symbol = None
    #     yield {
    #         'ci_id': service.id,
    #         'ci_uid': service.uid,
    #         'name': service.name,
    #         'symbol': symbol,
    #         'profit_center': profit_center[0] if profit_center else None,
    #         'business_owners': list(service.business_owners.values_list(
    #             'id',
    #             flat=True,
    #         )),
    #         'technical_owners': list(service.technical_owners.values_list(
    #             'id',
    #             flat=True,
    #         )),
    #         'environments': [e.child.id for e in environments]
    #     }


def get_warehouses():
    """Yields dicts describing all warehouses"""
    return []
    # for warehouse in DataCenter.objects.all():
    #     yield {
    #         'warehouse_id': warehouse.id,
    #         'warehouse_name': warehouse.name,
    #     }


def get_models():
    return []
    # for model in AssetModel.objects.filter(
    #     type__in=AssetType.DC.choices
    # ).select_related('manufacturer', 'category'):
    #     yield {
    #         'model_id': model.id,
    #         'name': model.name,
    #         'manufacturer': (
    #             model.manufacturer.name if model.manufacturer else None
    #         ),
    #         'category': model.category.name if model.category else None,
    #     }


def get_assets(date):
    """Yields dicts describing all assets"""
    return []
    # for asset in Asset.objects_dc.filter(
    #     Q(invoice_date=None) | Q(invoice_date__lte=date),
    #     part_info=None,
    # ).select_related('model', 'device_info'):
    #     if not asset.device_info_id:
    #         logger.error('Asset {0} has no device'.format(asset.id))
    #         continue
    #     if not asset.service_id:
    #         logger.error('Asset {0} has no service'.format(asset.id))
    #         continue
    #     if not asset.device_environment_id:
    #         logger.error('Asset {0} has no environment'.format(asset.id))
    #         continue
    #     if asset.is_liquidated(date):
    #         logger.info("Skipping asset {} - it's liquidated")
    #         continue
    #     device_info = asset.device_info
    #     hostname = None
    #     ralph_device = None
    #     if device_info:
    #         ralph_device = device_info.get_ralph_device()
    #         if ralph_device:
    #             hostname = ralph_device.name
    #     try:
    #         data_center_id = asset.device_info.data_center_id
    #     except AttributeError:
    #         data_center_id = None

    #     yield {
    #         'asset_id': asset.id,
    #         'device_id': ralph_device.id if ralph_device else None,
    #         'asset_name': hostname,
    #         'service_id': asset.service_id,
    #         'environment_id': asset.device_environment_id,
    #         'sn': asset.sn,
    #         'barcode': asset.barcode,
    #         'warehouse_id': data_center_id,
    #         'cores_count': asset.cores_count,
    #         'power_consumption': asset.model.power_consumption,
    #         'collocation': asset.model.height_of_device,
    #         'depreciation_rate': asset.deprecation_rate,
    #         'is_depreciated': asset.is_deprecated(date=date),
    #         'price': asset.price,
    #         'model_id': asset.model_id,
    #     }


# class get_supports(DatedGetter):
#     """Gets data for DC supports."""

#     Model = Support
#     begin_field = 'date_from'
#     end_field = 'date_to'

#     filters = {'asset_type': AssetType.data_center, 'price__gt': 0}
#     fields = [
#         ('support_id', 'id'),
#         'name',
#         'price',
#         'date_from',
#         'date_to',
#         ('assets', (lambda support: [
#             asset.id for asset in support.assets.all()
#         ]))
#     ]
def get_supports():
    return []


# class get_licences(DatedGetter):
#     """Gets data for DC licences."""

#     Model = Licence
#     begin_field = 'invoice_date'
#     end_field = 'valid_thru'

#     filters = {'asset_type': AssetType.data_center}

#     fields = [
#         ('software_category', 'software_category__name'),
#         'price',
#         'invoice_date',
#         'valid_thru',
#         ('assets', (lambda licence: [
#             asset.id for asset in licence.assets.all()
#         ]))
#     ]
def get_licences():
    return []
