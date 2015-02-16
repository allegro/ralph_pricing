# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from django.utils.translation import ugettext_lazy as _

from lck.django.common.models import WithConcurrentGetOrCreate

from ralph_scrooge.models._tree import MultiPathNode

PRICE_DIGITS = 16
PRICE_PLACES = 6


class DailyCostManager(db.Manager):
    def get_query_set(self):
        return super(DailyCostManager, self).get_query_set().filter(depth=0)


class DailyCost(MultiPathNode):
    _path_field = 'type_id'
    objects = DailyCostManager()
    objects_tree = db.Manager()

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
        db_index=True,
    )
    type = db.ForeignKey(
        'BaseUsage',
        null=False,
        blank=False,
        related_name='daily_costs',
        verbose_name=_('type'),
        db_index=True,
    )
    warehouse = db.ForeignKey(
        'Warehouse',
        null=True,
        blank=True,
        related_name='daily_costs',
        verbose_name=_('warehouse'),
    )
    value = db.FloatField(verbose_name=_("value"), default=0)
    cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        default=0,
        verbose_name=_("cost"),
    )
    forecast = db.BooleanField(
        verbose_name=_('forecast'),
        default=False,
        db_index=True,
    )
    date = db.DateField(
        verbose_name=_('date'),
        db_index=True,
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

    @classmethod
    def _are_params_valid(self, params):
        if 'cost' in params:
            return params['cost'] > 0
        return True


class CostDateStatus(WithConcurrentGetOrCreate, db.Model):
    date = db.DateField(
        verbose_name=_('date'),
        unique=True,
    )
    calculated = db.BooleanField(
        verbose_name=_("calculated"),
        default=False,
        editable=False,
    )
    forecast_calculated = db.BooleanField(
        verbose_name=_("forecast calculated"),
        default=False,
        editable=False,
    )
    accepted = db.BooleanField(
        verbose_name=_("accepted"),
        default=False,
        editable=False,
    )
    forecast_accepted = db.BooleanField(
        verbose_name=_("forecast accepted"),
        default=False,
        editable=False,
    )

    class Meta:
        verbose_name = _("cost date status")
        verbose_name_plural = _("costs date status")
        app_label = 'ralph_scrooge'
