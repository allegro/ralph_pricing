# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from decimal import Decimal as D

from django.conf import settings
from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from dj.choices import _ChoicesMeta
from lck.django.choices import Choices
from lck.django.common.models import (
    EditorTrackable,
    TimeTrackable,
)


PRICE_DIGITS = 16
PRICE_PLACES = 6


class PricingObjectTypeMeta(_ChoicesMeta):
    """
    Metaclass which allows to define additional Pricing Object Types, without
    breaking original ids. Additional pricing object types should be added to
    settings as dictionary, with field name as key and function returning
    choice as value (function is a workaround to not break original choices
    ids).
    """
    def __new__(meta, classname, bases, classDict):
        additional_choices = settings.ADDITIONAL_PRICING_OBJECT_TYPES
        for choice_name, choice_func in additional_choices.items():
            classDict[choice_name] = choice_func()
        return super(PricingObjectTypeMeta, meta).__new__(
            meta,
            classname,
            bases,
            classDict
        )


class PricingObjectType(Choices):
    __metaclass__ = PricingObjectTypeMeta
    _ = Choices.Choice
    asset = _("Asset")
    virtual = _("Virtual")
    tenant = _("OpenStack Tenant")
    ip_address = _("IP Address")
    # dummy type to use in service environments where there is no real
    # pricing object; there should be only one pricing object with dummy type
    # for each service environment
    dummy = _('-', id=254)
    # unknown type to use, when could not determine type of pricing object;
    # unknown pricing objects type could be modified in admin panel to select
    # proper type
    unknown = _('Unknown', id=255)


class PricingObject(TimeTrackable, EditorTrackable):
    name = db.CharField(
        max_length=200,
        null=True,
        blank=True,
        default=None,
    )
    type = db.PositiveIntegerField(
        verbose_name=_("type"), choices=PricingObjectType(),
    )
    remarks = db.TextField(
        verbose_name=_("Remarks"),
        help_text=_("Additional information."),
        blank=True,
        default="",
    )
    service_environment = db.ForeignKey(
        'ServiceEnvironment',
        related_name='pricing_objects'
    )

    class Meta:
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{} ({})'.format(
            self.name,
            PricingObjectType.name_from_id(self.type),
        )

    # TODO: AssetInfo / VirtualInfo should be required if PricingObject has
    # asset or virtual type

    def get_daily_pricing_object(self, date):
        try:
            return self.daily_pricing_objects.get(date=date)
        except DailyPricingObject.DoesNotExist:
            return DailyPricingObject.objects.create(
                pricing_object=self,
                date=date,
                service_environment=self.service_environment,
            )


class DailyPricingObject(db.Model):
    date = db.DateField(null=False, blank=False)
    pricing_object = db.ForeignKey(
        PricingObject,
        null=False,
        blank=False,
        related_name='daily_pricing_objects',
    )
    service_environment = db.ForeignKey(
        'ServiceEnvironment',
        related_name='daily_pricing_objects'
    )

    class Meta:
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{} ({})'.format(self.pricing_object, self.date)


class AssetInfo(PricingObject):
    sn = db.CharField(max_length=200, null=True, blank=True, unique=True)
    barcode = db.CharField(max_length=200, null=True, blank=True, unique=True)
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
    warehouse = db.ForeignKey('Warehouse')

    class Meta:
        app_label = 'ralph_scrooge'


class DailyAssetInfo(DailyPricingObject):
    asset_info = db.ForeignKey(
        AssetInfo,
    )
    depreciation_rate = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("Depreciation rate"),
        default=0,
    )
    is_depreciated = db.BooleanField(
        default=False,
        verbose_name=_("Is depreciated"),
    )
    price = db.DecimalField(
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
        related_name='daily_virtuals',
        null=True,
        blank=True,
    )
    virtual_info = db.ForeignKey(
        VirtualInfo,
        related_name='daily_virtuals',
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
    )

    class Meta:
        app_label = 'ralph_scrooge'


class DailyTenantInfo(DailyPricingObject):
    tenant_info = db.ForeignKey(
        TenantInfo,
        related_name='daily_tenant',
    )
    enabled = db.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name=_("enabled"),
    )

    class Meta:
        app_label = 'ralph_scrooge'
