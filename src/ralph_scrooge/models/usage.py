# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.common.models import (
    EditorTrackable,
    Named,
    TimeTrackable,
)

from ralph_scrooge.models.warehouse import Warehouse


PRICE_DIGITS = 16
PRICE_PLACES = 6


class InternetProvider(
    TimeTrackable,
    EditorTrackable,
    Named
):
    class Meta:
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return self.name


class UsageType(db.Model):
    """
    Model contains usage types
    """
    name = db.CharField(verbose_name=_("name"), max_length=255, unique=True)
    symbol = db.CharField(
        verbose_name=_("symbol"),
        max_length=255,
        default="",
        blank=True,
    )
    average = db.BooleanField(
        verbose_name=_("Average the values over multiple days"),
        default=False,
    )
    show_value_percentage = db.BooleanField(
        verbose_name=_("Show percentage of value"),
        default=False,
    )
    show_price_percentage = db.BooleanField(
        verbose_name=_("Show percentage of price"),
        default=False,
    )
    by_warehouse = db.BooleanField(
        verbose_name=_("Usage type is by warehouse"),
        default=False,
    )
    by_team = db.BooleanField(
        verbose_name=_("Usage type is by team"),
        default=False,
    )
    by_internet_provider = db.BooleanField(
        verbose_name=_("Cost is given by internet provider"),
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
        verbose_name=_("Display usage type in ventures report"),
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
    divide_by = db.IntegerField(
        verbose_name=_("Divide by"),
        help_text=_(
            "Divide value by 10 to the power of entered value. Ex. with "
            "divide by = 3 and value = 1 000 000, presented value is 1 000."
        ),
        default=0,
    )
    rounding = db.IntegerField(
        verbose_name=("Value rounding"),
        help_text=_("Decimal places"),
        default=0,
    )
    TYPE_CHOICES = (
        ('BU', _("Base usage type")),
        ('RU', _("Regular usage type")),
        ('SU', _("Service usage type")),
    )
    type = db.CharField(
        verbose_name=_("Type"),
        max_length=2,
        choices=TYPE_CHOICES,
        default='RU',
    )
    use_universal_plugin = db.BooleanField(
        verbose_name=_("Use universal plugin"),
        default=True,
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

    def get_plugin_name(self):
        if self.use_universal_plugin:
            return 'usage_plugin'
        return self.symbol or self.name.lower().replace(' ', '_')


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
    )
    team = db.ForeignKey(
        'Team',
        null=True,
        blank=True,
        on_delete=db.PROTECT,
    )
    team_members_count = db.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Team members count"),
        default=0,
    )
    internet_provider = db.ForeignKey(
        InternetProvider,
        null=True,
        blank=True,
        on_delete=db.PROTECT,
        verbose_name=_("Internet Provider"),
    )

    class Meta:
        verbose_name = _("usage price")
        verbose_name_plural = _("usage prices")
        app_label = 'ralph_scrooge'

        unique_together = [
            ('warehouse', 'start', 'type'),
            ('warehouse', 'end', 'type'),
            ('team', 'start', 'type'),
            ('team', 'end', 'type'),
            ('internet_provider', 'start', 'type'),
            ('internet_provider', 'end', 'type'),
        ]
        ordering = ('type', '-start')

    def __unicode__(self):
        if self.type and self.type.by_warehouse:
            return '{}-{} ({}-{})'.format(
                self.warehouse,
                self.type,
                self.start,
                self.end,
            )
        if self.type and self.type.by_team:
            return '{}-{} ({}-{})'.format(
                self.team,
                self.type,
                self.start,
                self.end,
            )
        if self.type and self.type.by_internet_provider:
            return '{}-{} ({}-{})'.format(
                self.internet_provider,
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
        if self.type.by_internet_provider and not self.internet_provider:
            raise ValidationError('Internet Provider is required')
        if self.type.by_team and not self.team:
            raise ValidationError('Team is required')


class DailyUsage(db.Model):
    """
    DailyUsage model contains daily usage information for each
    usage
    """
    date = db.DateTimeField()
    service = db.ForeignKey(
        'Service',
        null=False,
        blank=False,
    )
    environment = db.ForeignKey(
        'Environment',
        null=False,
        blank=False,
    )
    daily_pricing_object = db.ForeignKey(
        'DailyPricingObject',
        verbose_name=_("Pricing Object"),
        null=False,
        blank=False,
    )
    value = db.FloatField(verbose_name=_("value"), default=0)
    type = db.ForeignKey(UsageType, verbose_name=_("type"))
    warehouse = db.ForeignKey(
        'Warehouse',
        null=False,
        blank=False,
        on_delete=db.PROTECT,
        default=lambda: Warehouse.objects.get(name='Default'),
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

    def __unicode__(self):
        return '{0}/{1} ({2}) {3}'.format(
            self.daily_pricing_object,
            self.type,
            self.date,
            self.value,
        )
