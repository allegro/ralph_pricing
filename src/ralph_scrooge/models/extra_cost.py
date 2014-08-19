# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.choices import Choices

from ralph_scrooge.models.base import BaseUsage

PRICE_DIGITS = 16
PRICE_PLACES = 6


class ExtraCostType(db.Model):
    """
    Contains all type of extra costs like license or call center.
    """
    name = db.CharField(verbose_name=_("name"), max_length=255, unique=True)

    class Meta:
        verbose_name = _("extra cost type")
        verbose_name_plural = _("extra cost types")
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return self.name


class ExtraCostChoices(Choices):
    _ = Choices.Choice
    daily_imprint = _('Daily imprint')
    time_period_cost = _('Time period cost')


class ExtraCost(BaseUsage):
    """
    Contains information about cost of extra cost types per venture.
    This is a static value without any time interval becouse this
    value (cost) is accumulate each day by collect plugin in
    DailyExtraCost model.
    """
    type = db.ForeignKey(ExtraCostType, verbose_name=_("type"))
    monthly_cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("monthly cost"),
        null=False,
        blank=False,
    )
    service_environment = db.ForeignKey(
        'ServiceEnvironment',
        related_name='extra_costs'
    )
    pricing_object = db.ForeignKey(
        'PricingObject',
        verbose_name=_("Pricing Object"),
        null=True,
        blank=True,
        default=None,
    )
    start = db.DateField(
        verbose_name=_("start time"),
        null=True,
        blank=True,
        default=None,
    )
    end = db.DateField(
        verbose_name=_("end time"),
        null=True,
        blank=True,
        default=None,
    )
    mode = db.CharField(
        verbose_name=_("Extra cost mode"),
        choices=ExtraCostChoices(),
        blank=False,
        null=False,
        max_length=30,
    )

    class Meta:
        verbose_name = _("Extra cost")
        verbose_name_plural = _("Extra costs")
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{} - {}'.format(
            self.service,
            self.type,
        )


class DailyExtraCost(db.Model):
    """
    DailyExtraCost model contains cost per venture for each day.
    """
    date = db.DateField()
    service_environment = db.ForeignKey(
        'ServiceEnvironment',
        related_name='daily_extra_costs'
    )
    daily_pricing_object = db.ForeignKey(
        'DailyPricingObject',
        verbose_name=_("Daily pricing object"),
        null=True,
        blank=True,
        default=None,
    )
    value = db.FloatField(verbose_name=_("value"), default=0)
    type = db.ForeignKey(ExtraCostType, verbose_name=_("type"))
    remarks = db.TextField(
        verbose_name=_("Remarks"),
        help_text=_("Additional information."),
        blank=True,
        default="",
    )

    class Meta:
        verbose_name = _("daily extra costs")
        verbose_name_plural = _("daily extra costs")
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{0} {1} ({2}) {3}'.format(
            self.service,
            self.type,
            self.date,
            self.value,
        )
