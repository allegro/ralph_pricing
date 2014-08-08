# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.common.models import (
    EditorTrackable,
    Named,
    TimeTrackable,
)

from ralph_scrooge.models._history import (
    IntervalHistoricalRecords,
    ModelDiffMixin,
)


class BusinessLine(Named):
    ci_uid = db.CharField(
        unique=True,
        null=False,
        blank=False,
        verbose_name='CMDB CI UID',
        max_length=100,
    )

    class Meta:
        app_label = 'ralph_scrooge'


class Service(ModelDiffMixin, EditorTrackable, TimeTrackable):
    name = db.CharField(
        verbose_name=_("name"),
        max_length=256,
    )
    business_line = db.ForeignKey(
        BusinessLine,
        null=True,
        blank=True,
        related_name='services',
    )
    ci_uid = db.CharField(
        unique=True,
        null=False,
        blank=False,
        verbose_name='CMDB CI UID',
        max_length=100,
    )
    ownership = db.ManyToManyField(
        'Owner',
        through='ServiceOwnership',
        related_name='services'
    )
    history = IntervalHistoricalRecords()

    class Meta:
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return self.name

    def get_plugin_name(self):
        if self.use_universal_plugin:
            return 'service_plugin'
        return self.symbol or self.name.lower().replace(' ', '_')


class PricingService(Named):
    use_universal_plugin = db.BooleanField(
        verbose_name=_("Use universal plugin"),
        default=True,
    )
    services = db.ManyToManyField(
        'Service',
        verbose_name=_("Services"),
        related_name='pricing_services',
        help_text=_('Services used to calculate costs of Pricing Service'),
        blank=False,
        null=False,
    )
    usage_types = db.ManyToManyField(
        'UsageType',
        through='ServiceUsageTypes',
        related_name='services',
    )
    excluded_services = db.ManyToManyField(
        'Service',
        verbose_name=_("Excluded services"),
        related_name='excluded_from_pricing_services',
        help_text=_(
            'Services excluded from cost distribution (besides usage '
            'type excluded services)'
        ),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("pricing service")
        verbose_name_plural = _("pricing services")
        app_label = 'ralph_scrooge'


class ServiceUsageTypes(db.Model):
    usage_type = db.ForeignKey(
        'UsageType',
        verbose_name=_("Usage type"),
        related_name="service_division",
        limit_choices_to={
            'type': 'SU',
        },
    )
    pricing_service = db.ForeignKey(
        PricingService,
        verbose_name=_("Pricing Service"),
    )
    start = db.DateField()
    end = db.DateField()
    percent = db.FloatField(
        validators=[
            MaxValueValidator(100.0),
            MinValueValidator(0.0)
        ]
    )

    class Meta:
        verbose_name = _("service usage type")
        verbose_name_plural = _("service usage types")
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{}/{} ({} - {})'.format(
            self.pricing_service,
            self.usage_type,
            self.start,
            self.end,
        )
