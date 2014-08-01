# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db

from ralph_scrooge.models._history import (
    IntervalHistoricalRecords,
    ModelDiffMixin,
)


class History(ModelDiffMixin, db.Model):
    field1 = db.IntegerField()
    field2 = db.CharField(max_length=10)
    history = IntervalHistoricalRecords()

    class Meta:
        app_label = 'ralph_scrooge'
