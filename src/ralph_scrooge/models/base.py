# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from dj.choices import Choices

from ralph_scrooge.utils.models import Named


class BaseUsageType(Choices):
    _ = Choices.Choice
    usage_type = _("Usage Type")
    team = _("Team")
    extra_cost = _("Extra Cost")
    pricing_service = _("Pricing Service")
    dynamic_extra_cost = _("Dynamic extra cost")


class BaseUsageManager(db.Manager):
    def get_queryset(self):
        return super(BaseUsageManager, self).get_queryset().filter(
            active=True,
        )


@python_2_unicode_compatible
class BaseUsage(Named):
    active = db.BooleanField(
        verbose_name=_('active'),
        default=True,
        help_text=_(
            "If inactive, this type won't take part in costs calculation"
        ),
        null=False,
        blank=False,
    )
    symbol = db.CharField(
        verbose_name=_("symbol"),
        max_length=255,
        default="",
        blank=True,
        editable=False,
        help_text=_(
            '(Usually) slug of the name of the usage. Used (mostly) in API to'
            ' specify type of the usage.'
        ),
        unique=True,
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

    objects_admin = db.Manager()
    objects = BaseUsageManager()

    class Meta:
        app_label = 'ralph_scrooge'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # if symbol is empty, fill it by slugifying the name
        if not self.symbol:
            self.symbol = slugify(self.name)
        return super(BaseUsage, self).save(*args, **kwargs)
