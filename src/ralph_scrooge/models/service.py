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


class Service(ModelDiffMixin, Named, EditorTrackable, TimeTrackable):
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
    usage_types = db.ManyToManyField(
        'UsageType',
        through='ServiceUsageTypes',
        related_name='services',
    )
    use_universal_plugin = db.BooleanField(
        verbose_name=_("Use universal plugin"),
        default=True,
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


class ServiceUsageTypes(db.Model):
    usage_type = db.ForeignKey(
        'UsageType',
        verbose_name=_("Usage type"),
        related_name="service_division",
        limit_choices_to={
            'type': 'SU',
        },
    )
    service = db.ForeignKey(
        Service,
        verbose_name=_("Service"),
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
            self.service,
            self.usage_type,
            self.start,
            self.end,
        )
