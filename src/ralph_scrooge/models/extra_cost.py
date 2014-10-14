# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models as db
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.models.base import BaseUsage, BaseUsageType

PRICE_DIGITS = 16
PRICE_PLACES = 6


class ExtraCostType(BaseUsage):
    """
    Contains all type of extra costs like license or call center.
    """
    class Meta:
        verbose_name = _("extra cost type")
        verbose_name_plural = _("extra cost types")
        app_label = 'ralph_scrooge'

    def save(self, *args, **kwargs):
        self.type = BaseUsageType.extra_cost
        super(ExtraCostType, self).save(*args, **kwargs)


class ExtraCost(db.Model):
    """
    Contains information about cost of extra cost types per venture.
    This is a static value without any time interval becouse this
    value (cost) is accumulate each day by collect plugin in
    DailyExtraCost model.
    """
    extra_cost_type = db.ForeignKey(ExtraCostType, verbose_name=_("type"))
    cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("cost"),
        null=False,
        blank=False,
    )
    forecast_cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        default=0.00,
        verbose_name=_("forecast cost"),
    )
    service_environment = db.ForeignKey(
        'ServiceEnvironment',
        related_name='extra_costs',
        verbose_name=_("service environment"),
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
    remarks = db.TextField(
        verbose_name=_("Remarks"),
        help_text=_("Additional information."),
        blank=True,
        default="",
    )

    class Meta:
        verbose_name = _("Extra cost")
        verbose_name_plural = _("Extra costs")
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{} - {}'.format(
            self.service_environment,
            self.extra_cost_type,
        )


class DynamicExtraCostType(BaseUsage):
    excluded_services = db.ManyToManyField(
        'Service',
        verbose_name=_("Excluded services"),
        related_name='excluded_from_dynamic_usage_types',
        help_text=_(
            'Services excluded from cost distribution (besides usage '
            'type excluded services)'
        ),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Dynamic extra cost")
        verbose_name_plural = _("Dynamic extra costs")
        app_label = 'ralph_scrooge'

    def save(self, *args, **kwargs):
        self.type = BaseUsageType.dynamic_extra_cost
        super(DynamicExtraCostType, self).save(*args, **kwargs)


class DynamicExtraCostDivision(db.Model):
    dynamic_extra_cost_type = db.ForeignKey(
        DynamicExtraCostType,
        verbose_name=_("type"),
        related_name='division',
    )
    usage_type = db.ForeignKey(
        'UsageType',
        verbose_name=_("usage type"),
        related_name="dynamic_extra_cost_division",
        limit_choices_to=db.Q(usage_type='SU') | db.Q(symbol='depreciation'),
    )
    percent = db.FloatField(
        validators=[
            MaxValueValidator(100.0),
            MinValueValidator(0.0)
        ],
        verbose_name=_("percent"),
        default=100,
    )

    class Meta:
        verbose_name = _("Dynamic extra cost division")
        verbose_name_plural = _("Dynamic extra cost divisions")
        app_label = 'ralph_scrooge'


class DynamicExtraCost(db.Model):
    """
    Contains all information about dynamic extra costs.
    """
    dynamic_extra_cost_type = db.ForeignKey(
        DynamicExtraCostType,
        verbose_name=_("type"),
        related_name='costs',
    )
    cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("cost"),
        null=False,
        blank=False,
    )
    forecast_cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        default=0.00,
        verbose_name=_("forecast cost"),
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

    class Meta:
        verbose_name = _("Dynamic extra cost")
        verbose_name_plural = _("Dynamic extra costs")
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{} ({}-{})'.format(
            self.extra_cost_type,
            self.start,
            self.end,
        )
