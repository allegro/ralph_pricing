# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models as db
from django.utils.translation import ugettext_lazy as _

from dj.choices import Choices


class ScroogeUser(AbstractUser):

    pass

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        app_label = 'ralph_scrooge'


class OwnershipType(Choices):
    _ = Choices.Choice

    technical = _("Technical owner")
    business = _("Business owner")


class ServiceOwnership(db.Model):
    service = db.ForeignKey(
        'Service',
        verbose_name=_("service"),
        null=False,
        blank=False,
    )
    owner = db.ForeignKey(
        ScroogeUser,
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
        ScroogeUser,
        verbose_name=_("manager"),
        null=False,
        blank=False,
    )

    class Meta:
        app_label = 'ralph_scrooge'
        unique_together = ('manager', 'team')

    def __unicode__(self):
        return '{} / {}'.format(self.team, self.manager)
