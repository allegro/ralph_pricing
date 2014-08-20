# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.choices import Choices
from lck.django.common.models import Named


class BaseUsageType(Choices):
    _ = Choices.Choice
    usage_type = _("Usage Type")
    team = _("Team")
    extra_cost = _("Extra Cost")
    pricing_service = _("Pricing Service")


class BaseUsage(Named):
    type = db.PositiveIntegerField(
        verbose_name=_("type"),
        choices=BaseUsageType(),
        editable=False,
    )

    class Meta:
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{} - {}'.format(self.type, self.name)
