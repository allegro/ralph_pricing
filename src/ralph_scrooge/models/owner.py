# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from lck.django.common.models import (
    EditorTrackable,
    TimeTrackable,
)

from lck.django.choices import Choices


class OwnershipType(Choices):
    _ = Choices.Choice

    technical = _("Technical owner")
    business = _("Business owner")


class Owner(EditorTrackable, TimeTrackable):
    cmdb_id = db.IntegerField(unique=True, null=False, blank=False)
    first_name = db.CharField(max_length=50)
    last_name = db.CharField(max_length=100)
    email = db.EmailField(unique=True, null=True)
    sAMAccountName = db.CharField(max_length=256, blank=True)

    class Meta:
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return ' '.join([self.first_name, self.last_name])


class ServiceOwnership(db.Model):
    service = db.ForeignKey(
        'Service'
    )
    owner = db.ForeignKey(
        Owner,
    )
    type = db.PositiveIntegerField(null=True, choices=OwnershipType())

    class Meta:
        app_label = 'ralph_scrooge'
