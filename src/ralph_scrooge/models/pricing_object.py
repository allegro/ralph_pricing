# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ipaddress
from decimal import Decimal as D

from django.core.exceptions import ValidationError
from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from dj.choices import Choices

from ralph_scrooge.utils.models import EditorTrackable, TimeTrackable

PRICE_DIGITS = 16
PRICE_PLACES = 6


class PricingObjectType(db.Model):
    name = db.CharField(
        verbose_name=_('name'),
        null=False,
        blank=False,
        max_length=50,
        unique=True,
    )
    color = db.CharField(
        verbose_name=_('color'),
        null=True,
        blank=True,
        max_length=30,
        unique=True,
    )
    icon_class = db.CharField(
        verbose_name=_('icon class'),
        default='fa-tasks',
        max_length=30,
        help_text=mark_safe('Please visit http://fortawesome.github.io/Font-Awesome/icons/ for more information.')  # noqa
    )

    class Meta:
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return self.name


class PRICING_OBJECT_TYPES(Choices):
    _ = Choices.Choice

    ASSET = _("Asset")
    VIRTUAL = _("Virtual")
    TENANT = _("OpenStack Tenant")
    IP_ADDRESS = _("IP Address")
    VIP = _("VIP")
    DATABASE = _("Database")
    # dummy type to use in service environments where there is no real
    # pricing object; there should be only one pricing object with dummy type
    # for each service environment
    DUMMY = _('-', id=254)
    # unknown type to use, when could not determine type of pricing object;
    # unknown pricing objects type could be modified in admin panel to select
    # proper type
    UNKNOWN = _('Unknown', id=255)


class PricingObjectModel(db.Model):
    model_id = db.IntegerField(
        verbose_name=_("model id"),
        null=True,
        blank=True,
    )
    ralph3_model_id = db.IntegerField(
        verbose_name=_("model id (Ralph 3)"),
        null=True,
        blank=True,
    )
    name = db.CharField(
        verbose_name=_("model name"),
        max_length=100,
    )
    manufacturer = db.CharField(
        verbose_name=_("manufacturer"),
        max_length=100,
        blank=True,
        null=True,
    )
    category = db.CharField(
        verbose_name=_("category"),
        max_length=100,
        blank=True,
        null=True,
    )
    type = db.ForeignKey(
        'PricingObjectType',
        verbose_name=_("type"),
        related_name='pricing_object_models',
        default=PRICING_OBJECT_TYPES.UNKNOWN.id,
    )

    class Meta:
        app_label = 'ralph_scrooge'
        ordering = ['manufacturer', 'name']
        unique_together = ('model_id', 'type')

    def __unicode__(self):
        return '{} - {}'.format(self.manufacturer, self.name)


class PricingObject(TimeTrackable, EditorTrackable):
    """
    Pricing object base class. Inherited by specified objects, such as asset,
    ip address, virtual etc.

    Pricing object type is defined by type attribute or by model type (not
    every pricing object will have model defined, ex. ip address or unknown).
    """
    name = db.CharField(
        verbose_name=_("name"),
        max_length=200,
        null=True,
        blank=True,
        default=None,
    )
    type = db.ForeignKey(
        'PricingObjectType',
        verbose_name=_("type"),
        related_name='pricing_objects',
        default=PRICING_OBJECT_TYPES.UNKNOWN.id,
    )
    model = db.ForeignKey(
        'PricingObjectModel',
        verbose_name=_('model'),
        related_name='pricing_objects',
        null=True,
        blank=True,
    )
    remarks = db.TextField(
        verbose_name=_("Remarks"),
        help_text=_("Additional information."),
        blank=True,
        default="",
    )
    service_environment = db.ForeignKey(
        'ServiceEnvironment',
        verbose_name=_("service environment"),
        related_name='pricing_objects',
    )

    class Meta:
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{} ({})'.format(
            self.name,
            self.type.name,
        )

    # TODO: AssetInfo / VirtualInfo should be required if PricingObject has
    # asset or virtual type

    def get_daily_pricing_object(self, date):
        return self.daily_pricing_objects.get_or_create(
            date=date,
            defaults=dict(
                service_environment=self.service_environment,
                pricing_object=self,
            )
        )[0]

    def save(self, *args, **kwargs):
        # TODO: check if model type is the same as object type
        return super(PricingObject, self).save(*args, **kwargs)


class IPInfo(PricingObject):

    number = db.DecimalField(
        verbose_name=_('IP address'),
        help_text=_('Presented as int.'),
        editable=False,
        unique=True,
        max_digits=39,
        decimal_places=0,
        default=None,
    )

    class Meta(PricingObject.Meta):
        app_label = 'ralph_scrooge'

    def save(self, *args, **kwargs):
        try:
            self.number = int(ipaddress.ip_address(self.name))
        except (ipaddress.AddressValueError, ValueError):
            raise ValidationError(_('Is not a valid IP address'))
        super(IPInfo, self).save(*args, **kwargs)


class DailyPricingObject(db.Model):
    date = db.DateField(
        verbose_name=_("date"),
        null=False,
        blank=False,
    )
    pricing_object = db.ForeignKey(
        PricingObject,
        verbose_name=_("pricing object"),
        related_name='daily_pricing_objects',
        null=False,
        blank=False,
    )
    service_environment = db.ForeignKey(
        'ServiceEnvironment',
        verbose_name=_("service environment"),
        related_name='daily_pricing_objects',
    )

    class Meta:
        app_label = 'ralph_scrooge'
        unique_together = ('pricing_object', 'date')
        # TODO: after migration to Django>=1.5 add index_together on
        # date, service_environment_id (see migration 0019 for details)

    def __unicode__(self):
        return '{} ({})'.format(self.pricing_object, self.date)


class AssetInfo(PricingObject):
    sn = db.CharField(
        verbose_name=_("serial number"),
        max_length=200,
        null=True,
        blank=True,
        unique=True,
    )
    barcode = db.CharField(
        verbose_name=_("barcode"),
        max_length=200,
        null=True,
        blank=True,
        unique=True,
    )
    device_id = db.IntegerField(
        verbose_name=_("device id"),
        unique=True,
        null=True,
        blank=True,
        default=None,
    )
    asset_id = db.IntegerField(
        verbose_name=_("asset id"),
        unique=True,
        null=True,
        blank=True,
    )
    ralph3_asset_id = db.IntegerField(
        verbose_name=_("asset id (Ralph 3)"),
        unique=True,
        null=True,
        blank=True,
    )
    warehouse = db.ForeignKey(
        'Warehouse',
        verbose_name=_("warehouse"),
    )

    class Meta:
        app_label = 'ralph_scrooge'

    def get_daily_pricing_object(self, date):
        return self.dailyassetinfo_set.get_or_create(
            date=date,
            defaults=dict(
                pricing_object=self,
                asset_info=self,
                service_environment=self.service_environment,
            )
        )[0]


class DailyAssetInfo(DailyPricingObject):
    asset_info = db.ForeignKey(
        AssetInfo,
        verbose_name=_("asset details"),
    )
    depreciation_rate = db.DecimalField(
        verbose_name=_("Depreciation rate"),
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        default=0,
    )
    is_depreciated = db.BooleanField(
        default=False,
        verbose_name=_("Is depreciated"),
    )
    price = db.DecimalField(
        verbose_name=_("price"),
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        default=0,
    )
    daily_cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("daily cost"),
        default=0,
    )

    class Meta:
        verbose_name = _("Daily Asset info")
        verbose_name_plural = _("Daily Assets info")
        app_label = 'ralph_scrooge'

    def calc_costs(self):
        """
        Calculates daily and monthly depreciation costs
        """
        self.daily_cost = D(0)
        if not self.is_depreciated:
            self.daily_cost =\
                D(self.depreciation_rate) * D(self.price) / D(36500)

    def save(self, *args, **kwargs):
        self.calc_costs()
        super(DailyAssetInfo, self).save(*args, **kwargs)


class VirtualInfo(PricingObject):
    device_id = db.IntegerField(
        unique=True, null=True, verbose_name=_("Ralph device ID")
    )
    ralph3_id = db.IntegerField(unique=True, null=True, blank=True)

    class Meta:
        app_label = 'ralph_scrooge'

    def get_daily_pricing_object(self, date):
        return self.daily_virtuals.get_or_create(
            date=date,
            defaults=dict(
                pricing_object=self,
                virtual_info=self,
                service_environment=self.service_environment,
            )
        )[0]


class DailyVirtualInfo(DailyPricingObject):
    hypervisor = db.ForeignKey(
        DailyAssetInfo,
        verbose_name=_("hypervisor"),
        related_name='daily_virtuals',
        null=True,
        blank=True,
    )
    virtual_info = db.ForeignKey(
        VirtualInfo,
        related_name='daily_virtuals',
        verbose_name=_("virtual details"),
    )

    class Meta:
        app_label = 'ralph_scrooge'


class TenantInfo(PricingObject):
    tenant_id = db.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("OpenStack Tenant ID"),
        unique=True,
    )
    ralph3_tenant_id = db.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("OpenStack Tenant ID (Ralph 3)"),
        unique=True,
    )
    device_id = db.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('device id'),
    )

    class Meta:
        app_label = 'ralph_scrooge'

    def get_daily_pricing_object(self, date):
        return self.daily_tenants.get_or_create(
            date=date,
            defaults=dict(
                pricing_object=self,
                tenant_info=self,
                service_environment=self.service_environment,
            )
        )[0]


class DailyTenantInfo(DailyPricingObject):
    tenant_info = db.ForeignKey(
        TenantInfo,
        related_name='daily_tenants',
        verbose_name=_("tenant details"),
    )
    enabled = db.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name=_("enabled"),
    )

    class Meta:
        app_label = 'ralph_scrooge'


class VIPInfo(PricingObject):
    vip_id = db.IntegerField(
        unique=True, null=True, verbose_name=_("Ralph VIP ID")
    )
    external_id = db.IntegerField(
        unique=True, null=True, verbose_name=_("VIP ID from external system")
    )
    ip_info = db.ForeignKey(
        PricingObject,
        related_name='vip',
        verbose_name=_("ip address"),
    )
    port = db.PositiveIntegerField(verbose_name=_("port"))
    load_balancer = db.ForeignKey(
        PricingObject,
        null=True,
        blank=True,
        related_name='vips',
        verbose_name=_('load balancer')
    )

    class Meta:
        app_label = 'ralph_scrooge'

    def get_daily_pricing_object(self, date):
        return self.daily_vips.get_or_create(
            date=date,
            defaults=dict(
                pricing_object=self,
                vip_info=self,
                service_environment=self.service_environment,
                ip_info=self.ip_info,
            )
        )[0]


class DailyVIPInfo(DailyPricingObject):
    vip_info = db.ForeignKey(
        VIPInfo,
        related_name='daily_vips',
        verbose_name=_("VIP details"),
    )
    ip_info = db.ForeignKey(
        PricingObject,
        related_name='ip_daily_vips',
        verbose_name=_("IP details"),
    )

    class Meta:
        app_label = 'ralph_scrooge'


class DatabaseInfo(PricingObject):
    database_id = db.IntegerField(
        unique=True,
        verbose_name=_("Ralph database ID")
    )
    parent_device = db.ForeignKey(
        AssetInfo,
        verbose_name=_("parent device"),
        related_name='databases',
        null=True,
        blank=True,
    )

    class Meta:
        app_label = 'ralph_scrooge'

    def get_daily_pricing_object(self, date):
        return self.daily_databases.get_or_create(
            date=date,
            defaults=dict(
                pricing_object=self,
                database_info=self,
                service_environment=self.service_environment,
            )
        )[0]


class DailyDatabaseInfo(DailyPricingObject):
    parent_device = db.ForeignKey(
        DailyAssetInfo,
        verbose_name=_("parent device"),
        related_name='daily_databases',
        null=True,
        blank=True,
    )
    database_info = db.ForeignKey(
        DatabaseInfo,
        related_name='daily_databases',
        verbose_name=_("database details"),
    )

    class Meta:
        app_label = 'ralph_scrooge'
