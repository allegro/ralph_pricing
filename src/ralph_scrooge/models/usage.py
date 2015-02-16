# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models as db
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.models.base import BaseUsage, BaseUsageType

PRICE_DIGITS = 16
PRICE_PLACES = 6


class UsageType(BaseUsage):
    """
    Model contains usage types
    """
    average = db.BooleanField(
        verbose_name=_("Average the values over multiple days"),
        default=False,
    )
    show_value_percentage = db.BooleanField(
        verbose_name=_("Show percentage of value"),
        default=False,
    )
    by_warehouse = db.BooleanField(
        verbose_name=_("Usage type is by warehouse"),
        default=False,
    )
    is_manually_type = db.BooleanField(
        verbose_name=_("Cost or price for usage is entered manually"),
        default=False,
    )
    by_cost = db.BooleanField(
        verbose_name=_("Given value is a cost"),
        default=False,
    )
    show_in_services_report = db.BooleanField(
        verbose_name=_("Display usage type in services report"),
        default=True,
    )
    show_in_devices_report = db.BooleanField(
        verbose_name=_("Display usage type in devices report"),
        default=False,
    )
    order = db.IntegerField(
        verbose_name=_("Display order"),
        default=0,
    )
    TYPE_CHOICES = (
        ('BU', _("Base usage type")),
        ('RU', _("Regular usage type")),
        ('SU', _("Service usage type")),
    )
    usage_type = db.CharField(
        verbose_name=_("Type"),
        max_length=2,
        choices=TYPE_CHOICES,
        default='SU',
    )
    excluded_services = db.ManyToManyField(
        'Service',
        verbose_name=_("Excluded services"),
        related_name='excluded_usage_types',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("usage type")
        verbose_name_plural = _("usage types")
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.type = BaseUsageType.usage_type
        super(UsageType, self).save(*args, **kwargs)

    def get_plugin_name(self):
        return 'usage_type_plugin'

    @property
    def excluded_services_environments(self):
        from ralph_scrooge.models import ServiceEnvironment
        return ServiceEnvironment.objects.filter(
            service__in=self.excluded_services.all()
        )


class UsagePrice(db.Model):
    """
    Model contains usages price information
    """
    type = db.ForeignKey(UsageType, verbose_name=_("type"))
    price = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("price"),
        default=0,
    )
    forecast_price = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("forecast price"),
        default=0,
    )
    cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        default=0.00,
        verbose_name=_("cost"),
    )
    forecast_cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        default=0.00,
        verbose_name=_("forecast cost"),
    )
    start = db.DateField()
    end = db.DateField()
    warehouse = db.ForeignKey(
        'Warehouse',
        null=True,
        blank=True,
        on_delete=db.PROTECT,
        verbose_name=_("warehouse"),
    )

    class Meta:
        verbose_name = _("usage price")
        verbose_name_plural = _("usage prices")
        app_label = 'ralph_scrooge'
        ordering = ('type', '-start')

    def __unicode__(self):
        if self.type and self.type.by_warehouse:
            return '{}-{} ({}-{})'.format(
                self.warehouse,
                self.type,
                self.start,
                self.end,
            )
        return '{} ({}-{})'.format(
            self.type,
            self.start,
            self.end,
        )

    def clean(self):
        if self.type.by_warehouse and not self.warehouse:
            raise ValidationError('Warehouse is required')


class DailyUsage(db.Model):
    """
    DailyUsage model contains daily usage information for each
    usage
    """
    date = db.DateField()
    service_environment = db.ForeignKey(
        'ServiceEnvironment',
        related_name='daily_usages',
        verbose_name=_("service environment"),
    )
    daily_pricing_object = db.ForeignKey(
        'DailyPricingObject',
        verbose_name=_("Pricing Object"),
        null=False,
        blank=False,
    )
    value = db.FloatField(verbose_name=_("value"), default=0)
    type = db.ForeignKey(UsageType, verbose_name=_("daily_usages"))
    warehouse = db.ForeignKey(
        'Warehouse',
        null=False,
        blank=False,
        on_delete=db.PROTECT,
        default=1,
        verbose_name=_("warehouse"),
    )
    remarks = db.TextField(
        verbose_name=_("Remarks"),
        help_text=_("Additional information."),
        blank=True,
        default="",
    )

    class Meta:
        verbose_name = _("daily usage")
        verbose_name_plural = _("daily usages")
        app_label = 'ralph_scrooge'
        # TODO: after migration to Django>=1.5 add index_together on
        # type_id, date and warehouse_id (see migration 0019 for details)

    def __unicode__(self):
        return '{0}/{1} ({2}) {3}'.format(
            self.daily_pricing_object,
            self.type,
            self.date,
            self.value,
        )
