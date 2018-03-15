# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from decimal import Decimal as D

from django.db import models as db
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.models.pricing_object import (
    PRICE_DIGITS,
    PRICE_PLACES,
    DailyPricingObject,
    PricingObject
)


class BackOfficeAssetInfo(PricingObject):
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
    ralph3_asset_id = db.IntegerField(
        verbose_name=_("asset id (Ralph 3)"),
        unique=True,
        null=True,
        blank=True,
    )

    def get_daily_pricing_object(self, date):
        return self.daily_info_set.get_or_create(
            date=date,
            defaults=dict(
                pricing_object=self,
                asset_info=self,
                service_environment=self.service_environment,
            )
        )[0]


class DailyBackOfficeAssetInfo(DailyPricingObject):
    asset_info = db.ForeignKey(
        BackOfficeAssetInfo,
        related_name="daily_info_set",
        verbose_name=_("daily asset details"),
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
        verbose_name = _("Daily Back Office Asset info")
        verbose_name_plural = _("Daily Back Office Assets info")
        app_label = 'ralph_scrooge'

    def calc_costs(self):
        """
        Calculates daily cost
        """
        self.daily_cost = D(0)
        if not self.is_depreciated:
            self.daily_cost =\
                D(self.depreciation_rate) * D(self.price) / D(36500)

    def save(self, *args, **kwargs):
        self.calc_costs()
        super(DailyBackOfficeAssetInfo, self).save(*args, **kwargs)
