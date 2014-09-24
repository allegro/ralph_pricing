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
    dynamic_extra_cost = _("Dynamic extra cost")


class BaseUsage(Named):
    symbol = db.CharField(
        verbose_name=_("symbol"),
        max_length=255,
        default="",
        blank=True,
    )
    type = db.PositiveIntegerField(
        verbose_name=_("type"),
        choices=BaseUsageType(),
        editable=False,
    )
    divide_by = db.IntegerField(
        verbose_name=_("Divide by"),
        help_text=_(
            "Divide value by 10 to the power of entered value. Ex. with "
            "divide by = 3 and value = 1 000 000, presented value is 1 000."
        ),
        default=0,
    )
    rounding = db.IntegerField(
        verbose_name=("Value rounding"),
        help_text=_("Decimal places"),
        default=0,
    )

    class Meta:
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return self.name
