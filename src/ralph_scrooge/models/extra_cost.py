# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.choices import Choices

from ralph_scrooge.models.base import BaseUsage, BaseUsageType

PRICE_DIGITS = 16
PRICE_PLACES = 6


class ExtraCostType(BaseUsage):
    """
    Contains all type of extra costs like license or call center.
    """
    class Meta:
        verbose_name = _("extra cost type")
        verbose_name_plural = _("extra cost types")
        app_label = 'ralph_scrooge'

    def save(self, *args, **kwargs):
        self.type = BaseUsageType.extra_cost
        super(ExtraCostType, self).save(*args, **kwargs)


class ExtraCost(db.Model):
    """
    Contains information about cost of extra cost types per venture.
    This is a static value without any time interval becouse this
    value (cost) is accumulate each day by collect plugin in
    DailyExtraCost model.
    """
    extra_cost_type = db.ForeignKey(ExtraCostType, verbose_name=_("type"))
    cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("cost"),
        null=False,
        blank=False,
    )
    service_environment = db.ForeignKey(
        'ServiceEnvironment',
        related_name='extra_costs'
        verbose_name=_("service environment"),
    )
    start = db.DateField(
        verbose_name=_("start time"),
        null=True,
        blank=True,
        default=None,
    )
    end = db.DateField(
        verbose_name=_("end time"),
        null=True,
        blank=True,
        default=None,
    )

    class Meta:
        verbose_name = _("Extra cost")
        verbose_name_plural = _("Extra costs")
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{} - {}'.format(
            self.service_environment,
            self.extra_cost_type,
        )
