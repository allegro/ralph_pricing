# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.common.models import TimeTrackable
from lck.django.choices import Choices


class OwnershipType(Choices):
    _ = Choices.Choice

    technical = _("Technical owner")
    business = _("Business owner")


class OwnerManager(db.Manager):
    def get_query_set(self):
        return super(OwnerManager, self).get_query_set().select_related(
            'profile',
            'profile__user'
        )


class Owner(TimeTrackable):
    objects = OwnerManager()
    objects_raw = db.Manager()

    cmdb_id = db.IntegerField(
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("id from cmdb"),
    )
    profile = db.OneToOneField(
        'account.Profile',
        verbose_name=_("profile"),
        null=False,
        blank=False,
    )

    class Meta:
        app_label = 'ralph_scrooge'
        ordering = ['profile__nick']

    def __unicode__(self):
        return ' '.join([
            self.profile.user.first_name,
            self.profile.user.last_name
        ])


class ServiceOwnership(db.Model):
    service = db.ForeignKey(
        'Service',
        verbose_name=_("service"),
        null=False,
        blank=False,
    )
    owner = db.ForeignKey(
        Owner,
        verbose_name=_("owner"),
        null=False,
        blank=False,
    )
    type = db.PositiveIntegerField(
        null=False,
        blank=False,
        default=1,
        choices=OwnershipType(),
        verbose_name=_("Type"),
    )

    class Meta:
        app_label = 'ralph_scrooge'
        unique_together = ('owner', 'service', 'type')

    def __unicode__(self):
        return '{} / {}'.format(self.service, self.owner)


class TeamManager(db.Model):
    team = db.ForeignKey(
        'Team',
        verbose_name=_("team"),
        null=False,
        blank=False,
    )
    manager = db.ForeignKey(
        Owner,
        verbose_name=_("manager"),
        null=False,
        blank=False,
    )

    class Meta:
        app_label = 'ralph_scrooge'
        unique_together = ('manager', 'team')

    def __unicode__(self):
        return '{} / {}'.format(self.team, self.manager)
