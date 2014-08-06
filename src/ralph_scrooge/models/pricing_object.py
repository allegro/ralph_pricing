# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from decimal import Decimal as D

from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.common.models import (
    EditorTrackable,
    TimeTrackable,
)

from lck.django.choices import Choices


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
    service = db.ForeignKey(
        'Service',
        related_name='pricing_objects'
    )

    class Meta:
        app_label = 'ralph_scrooge'

    # TODO: AssetInfo / VirtualInfo should be required if PricingObject has
    # asset or virtual type


class DailyPricingObject(db.Model):
    date = db.DateField(null=False, blank=False)
    pricing_object = db.ForeignKey(PricingObject, null=False, blank=False)
    service = db.ForeignKey('Service', related_name='daily_pricing_objects')

    class Meta:
        app_label = 'ralph_scrooge'


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
    hypervisor = db.ForeignKey(DailyAssetInfo, related_name='daily_virtuals')

    class Meta:
        app_label = 'ralph_scrooge'
