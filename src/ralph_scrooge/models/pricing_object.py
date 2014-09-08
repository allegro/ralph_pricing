# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from decimal import Decimal as D

from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.choices import Choices
from lck.django.common.models import (
    EditorTrackable,
    TimeTrackable,
)


PRICE_DIGITS = 16
PRICE_PLACES = 6


class PricingObjectType(Choices):
    _ = Choices.Choice
    asset = _("Asset")
    virtual = _("Virtual")
    tenant = _("OpenStack Tenant")
    ip_address = _("IP Address")


class PricingObject(TimeTrackable, EditorTrackable):
    name = db.CharField(
        verbose_name=_("name"),
        max_length=200,
        null=True,
        blank=True,
        default=None,
    )
    type = db.PositiveIntegerField(
        verbose_name=_("type"),
        choices=PricingObjectType(),
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
        unique_together = ('service_environment', 'type', 'name')

    def __unicode__(self):
        return '{} ({})'.format(
            self.name,
            PricingObjectType.name_from_id(self.type),
        )

    # TODO: AssetInfo / VirtualInfo should be required if PricingObject has
    # asset or virtual type


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
        unique_together = ('service_environment', 'pricing_object', 'date')

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
        null=False,
        blank=False,
    )
    warehouse = db.ForeignKey(
        'Warehouse',
        verbose_name=_("warehouse"),
    )

    class Meta:
        app_label = 'ralph_scrooge'


class DailyAssetInfo(DailyPricingObject):
    asset_info = db.ForeignKey(
        AssetInfo,
        verbose_name=_("asset defails"),
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

    class Meta:
        verbose_name = _("Daily Asset info")
        verbose_name_plural = _("Daily Assets info")
        app_label = 'ralph_scrooge'


class VirtualInfo(PricingObject):
    device_id = db.IntegerField(unique=True, verbose_name=_("Ralph device ID"))

    class Meta:
        app_label = 'ralph_scrooge'


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
        verbose_name=_("virtual defails"),
    )

    class Meta:
        app_label = 'ralph_scrooge'


class TenantInfo(PricingObject):
    tenant_id = db.CharField(
        max_length=100,
        null=False,
        blank=False,
        db_index=True,
        verbose_name=_("OpenStack Tenant ID"),
        unique=True,
    )

    class Meta:
        app_label = 'ralph_scrooge'


class DailyTenantInfo(DailyPricingObject):
    tenant_info = db.ForeignKey(
        TenantInfo,
        related_name='daily_tenant',
        verbose_name=_("tenant defails"),
    )
    enabled = db.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name=_("enabled"),
    )

    class Meta:
        app_label = 'ralph_scrooge'
