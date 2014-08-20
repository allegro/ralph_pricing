# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.models._tree import MultiPathNode

PRICE_DIGITS = 16
PRICE_PLACES = 6


class DailyCost(MultiPathNode):
    _path_field = 'type_id'

    pricing_object = db.ForeignKey(
        'PricingObject',
        null=True,
        blank=True,
        related_name='daily_costs',
        verbose_name=_('pricing object'),
    )
    service_environment = db.ForeignKey(
        'ServiceEnvironment',
        null=False,
        blank=False,
        related_name='daily_costs',
        verbose_name=_('service environment'),
    )
    type = db.ForeignKey(
        'BaseUsage',
        null=False,
        blank=False,
        related_name='daily_costs',
        verbose_name=_('type'),
    )
    warehouse = db.ForeignKey(
        'Warehouse',
        null=True,
        blank=True,
        related_name='daily_costs',
        verbose_name=_('warehouse'),
    )
    value = db.FloatField(verbose_name=_("value"), default=0)
    percent = db.FloatField(verbose_name=_('percent'), default=0)
    cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        default=0,
        verbose_name=_("cost"),
    )
    forecast = db.BooleanField(default=False)
    verified = db.BooleanField(
        verbose_name=_("verified"),
        default=False,
        editable=False,
    )
    date = db.DateField(
        verbose_name=_('date')
    )

    class Meta:
        verbose_name = _("daily cost")
        verbose_name_plural = _("daily costs")
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{} - {} ({})'.format(
            self.service_environment,
            self.type,
            self.date,
        )
