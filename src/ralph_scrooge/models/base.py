# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from django.utils.translation import ugettext_lazy as _


class BaseUsage(db.Model):
    name = db.CharField(verbose_name=_("name"), max_length=255, unique=True)

    class Meta:
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return self.name
