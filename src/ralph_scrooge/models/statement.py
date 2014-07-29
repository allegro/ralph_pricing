# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from django.utils.translation import ugettext_lazy as _


class Statement(db.Model):
    """
    Model contains statements
    """
    start = db.DateField()
    end = db.DateField()

    header = db.TextField(
        verbose_name=_("Report header"),
        blank=False,
        null=False,
    )

    data = db.TextField(
        verbose_name=_("Report data"),
        blank=False,
        null=False,
    )

    forecast = db.BooleanField(
        verbose_name=_("Forecast price"),
        default=0,
    )

    is_active = db.BooleanField(
        verbose_name=_("Show only active"),
        default=False,
    )

    class Meta:
        verbose_name = _("Statement")
        verbose_name_plural = _("Statement")
        unique_together = ('start', 'end', 'forecast', 'is_active')
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        string = '{} - {}'.format(self.start, self.end)
        if self.forecast or self.is_active:
            flags = ['forecast'] if self.forecast else []
            flags = flags + ['active'] if self.is_active else flags
            string = '{} ({})'.format(string, ",".join(flags))
        return string
