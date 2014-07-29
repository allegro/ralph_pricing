# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.common.models import (
    EditorTrackable,
    Named,
    TimeTrackable,
    WithConcurrentGetOrCreate,
)


PRICE_DIGITS = 16
PRICE_PLACES = 6


class Team(TimeTrackable, EditorTrackable, Named, WithConcurrentGetOrCreate):
    show_in_report = db.BooleanField(
        verbose_name=_("Show team in report"),
        default=True,
    )
    show_percent_column = db.BooleanField(
        verbose_name=_("Show percent column in report"),
        default=False,
    )
    BILLING_TYPES = (
        ('TIME', _('By time')),
        ('DEVICES_CORES', _('By devices and cores count')),
        ('DEVICES', _('By devices count')),
        ('DISTRIBUTE', _((
            'Distribute cost to other teams proportionally to '
            'team members count'
        ))),
        ('AVERAGE', _('Average'))
    )
    billing_type = db.CharField(
        verbose_name=_("Billing type"),
        max_length=15,
        choices=BILLING_TYPES,
        default='TIME',
    )
    excluded_services = db.ManyToManyField(
        'Service',
        verbose_name=_("Excluded services"),
        related_name='excluded_teams',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return self.name


class TeamDaterange(db.Model):
    team = db.ForeignKey(
        Team,
        verbose_name=_("Team"),
        related_name="dateranges",
        limit_choices_to={
            'billing_type': 'TIME',
        },
    )
    start = db.DateField()
    end = db.DateField()

    class Meta:
        verbose_name = _("Team daterange")
        verbose_name_plural = _("Teams dateranges")
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{} ({} - {})'.format(
            self.team,
            self.start,
            self.end,
        )

    def clean(self):
        if self.start > self.end:
            raise ValidationError('Start greater than start')


class TeamServicePercent(db.Model):
    team_daterange = db.ForeignKey(
        TeamDaterange,
        verbose_name=_("Team daterange"),
        related_name="percentage",
    )
    service = db.ForeignKey(
        'Service',
        limit_choices_to={
            'is_active': True,
        },
    )
    percent = db.FloatField(
        verbose_name=_("Percent"),
        validators=[
            MaxValueValidator(100.0),
            MinValueValidator(0.0)
        ]
    )

    class Meta:
        verbose_name = _("Team service percent")
        verbose_name_plural = _("Teams services percent")
        unique_together = ('team_daterange', 'service')
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{}/{} ({} - {})'.format(
            self.team_daterange.team,
            self.service,
            self.team_daterange.start,
            self.team_daterange.end,
        )
