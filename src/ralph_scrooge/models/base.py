# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from dj.choices import Choices
# from dj.common.models import Named


class Named(db.Model):
    """Describes an abstract model with a unique ``name`` field."""
    name = db.CharField(_('name'), max_length=255, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    class NonUnique(db.Model):
        """Describes an abstract model with a non-unique ``name`` field."""
        name = db.CharField(verbose_name=_("name"), max_length=75)

        class Meta:
            abstract = True

        def __str__(self):
            return self.name


class TimeTrackable(db.Model):
    created = db.DateTimeField(
        verbose_name=_('date created'),
        auto_now=True,
    )
    modified = db.DateTimeField(
        verbose_name=_('last modified'),
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('-modified', '-created',)


class BaseUsageType(Choices):
    _ = Choices.Choice
    usage_type = _("Usage Type")
    team = _("Team")
    extra_cost = _("Extra Cost")
    pricing_service = _("Pricing Service")
    dynamic_extra_cost = _("Dynamic extra cost")


class BaseUsageManager(db.Manager):
    def get_query_set(self):
        return super(BaseUsageManager, self).get_query_set().filter(
            active=True,
        )


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

    def __unicode__(self):
        return self.name
