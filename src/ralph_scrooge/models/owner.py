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


class Owner(TimeTrackable):
    cmdb_id = db.IntegerField(
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("id from cmdb"),
    )
    first_name = db.CharField(
        max_length=5,
        verbose_name=_("first name"),
    )
    last_name = db.CharField(
        max_length=100,
        verbose_name=_("last name"),
    )
    email = db.EmailField(
        unique=True,
        null=True,
        verbose_name=_("email"),
    )
    sAMAccountName = db.CharField(
        max_length=256,
        blank=True,
        verbose_name=_("sam account name"),
    )

    class Meta:
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return ' '.join([self.first_name, self.last_name])


class ServiceOwnership(db.Model):
    service = db.ForeignKey(
        'Service',
        verbose_name=_("service"),
    )
    owner = db.ForeignKey(
        Owner,
        verbose_name=_("owner"),
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
