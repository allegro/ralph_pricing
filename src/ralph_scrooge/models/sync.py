# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.common.models import TimeTrackable


class SyncStatus(TimeTrackable):
    date = db.DateField()
    plugin = db.CharField(
        null=False,
        blank=False,
        max_length=100,
        verbose_name=_("plugin name"),
    )
    success = db.BooleanField(
        verbose_name=_("status"),
        default=False,
    )
    remarks = db.TextField(
        verbose_name=_("remarks"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("sync status")
        verbose_name_plural = _("sync statuses")
        unique_together = ('date', 'plugin')
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{}/{} : {}'.format(
            self.date,
            self.plugin,
            _('Success') if self.success else _('Failed'),
        )
