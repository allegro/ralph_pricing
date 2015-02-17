# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.choices import Choices
from lck.django.common.models import (
    EditorTrackable,
    Named,
    TimeTrackable,
)

from ralph_scrooge.models._history import (
    IntervalHistoricalRecords,
    ModelDiffMixin,
)
from ralph_scrooge.models.base import BaseUsage, BaseUsageType
from ralph_scrooge.models.usage import DailyUsage
from ralph_scrooge.models.pricing_object import PRICING_OBJECT_TYPES


class BusinessLine(Named.NonUnique):
    ci_id = db.IntegerField(
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("id from cmdb"),
    )
    ci_uid = db.CharField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_("uid from cmdb"),
    )

    class Meta:
        app_label = 'ralph_scrooge'


class ProfitCenter(Named.NonUnique):
    ci_id = db.IntegerField(
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("id from cmdb"),
    )
    ci_uid = db.CharField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_("uid from cmdb"),
    )
    business_line = db.ForeignKey(
        BusinessLine,
        null=False,
        blank=False,
        default=1,
        related_name='profit_centers',
        verbose_name=_('business line'),
    )
    description = db.TextField(null=True, default=None)

    class Meta:
        app_label = 'ralph_scrooge'


class Environment(Named.NonUnique):
    ci_id = db.IntegerField(
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("id from cmdb"),
    )
    ci_uid = db.CharField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_("uid from cmdb"),
    )

    class Meta:
        app_label = 'ralph_scrooge'
        ordering = ['name']


class Service(ModelDiffMixin, EditorTrackable, TimeTrackable):
    ci_id = db.IntegerField(
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("id from cmdb"),
    )
    ci_uid = db.CharField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_("uid from cmdb"),
    )
    name = db.CharField(
        verbose_name=_("name"),
        max_length=256,
    )
    symbol = db.CharField(
        verbose_name=_('symbol'),
        max_length=256,
        null=True,
        blank=True,
    )
    profit_center = db.ForeignKey(
        ProfitCenter,
        null=False,
        blank=False,
        default=1,
        related_name='services',
        verbose_name=_('profit center'),
    )
    ownership = db.ManyToManyField(
        'Owner',
        through='ServiceOwnership',
        related_name='services',
        verbose_name=_("ownership"),
    )
    environments = db.ManyToManyField(
        Environment,
        through='ServiceEnvironment',
        related_name='services',
        verbose_name=_("environments"),
    )
    pricing_service = db.ForeignKey(
        'PricingService',
        related_name='services',
        null=True,
        blank=True,
        verbose_name=_("pricing service"),
    )
    history = IntervalHistoricalRecords(
        verbose_name=_("history"),
    )
    manually_allocate_costs = db.BooleanField(
        verbose_name=_("Manually Allocate Costs"),
        default=False,
    )

    class Meta:
        app_label = 'ralph_scrooge'
        ordering = ['name']

    def __unicode__(self):
        return self.name


class PricingServicePlugin(Choices):
    _ = Choices.Choice
    pricing_service_plugin = _("universal")
    pricing_service_fixed_price_plugin = _("fixed price")


class PricingService(BaseUsage):
    plugin_type = db.PositiveIntegerField(
        verbose_name=_("plugin type"),
        choices=PricingServicePlugin(),
        default=PricingServicePlugin.pricing_service_plugin.id,
    )
    usage_types = db.ManyToManyField(
        'UsageType',
        through='ServiceUsageTypes',
        related_name='services',
        verbose_name=_("usage types"),
    )
    excluded_services = db.ManyToManyField(
        'Service',
        verbose_name=_("Excluded services"),
        related_name='excluded_from_pricing_services',
        help_text=_(
            'Services excluded from cost distribution (besides usage '
            'type excluded services)'
        ),
        blank=True,
        null=True,
    )
    excluded_base_usage_types = db.ManyToManyField(
        'UsageType',
        related_name='excluded_from_pricing_service',
        limit_choices_to={
            'usage_type': 'BU',
        },
        blank=True,
        null=True,
        verbose_name=_("excluded base usage types"),
    )
    regular_usage_types = db.ManyToManyField(
        'UsageType',
        related_name='pricing_services',
        limit_choices_to={
            'usage_type': 'RU',
        },
        blank=True,
        null=True,
        verbose_name=_("regular usage types"),
    )
    charge_diff_to_real_costs = db.ForeignKey(
        'PricingService',
        related_name='charged_by_diffs',
        limit_choices_to={
            'plugin_type': PricingServicePlugin.pricing_service_plugin.id,
        },
        blank=True,
        null=True,
        verbose_name=_('charge diff to real costs'),
        help_text=_(
            'if plugin type different than universal, select pricing service '
            'to charge by difference between costs calculated by plugin and '
            'real costs'
        )
    )

    class Meta:
        verbose_name = _("pricing service")
        verbose_name_plural = _("pricing services")
        app_label = 'ralph_scrooge'
        ordering = ['name']

    def save(self, *args, **kwargs):
        self.type = BaseUsageType.pricing_service
        super(PricingService, self).save(*args, **kwargs)

    @property
    def service_environments(self):
        """
        Returns all services environments related with this pricing service.
        """
        return ServiceEnvironment.objects.filter(
            service__in=self.services.all()
        )

    def get_plugin_name(self):
        """
        Returns plugin name for pricing service.
        """
        return PricingServicePlugin.name_from_id(self.plugin_type)

    def get_dependent_services(self, date, exclude=None):
        """
        Returns pricing services, which resources (usage types) are used by
        this service (for given date).
        """
        ps = PricingService.objects.filter(
            serviceusagetypes__usage_type__id__in=DailyUsage.objects.filter(
                type__usage_type='SU',
                service_environment__in=ServiceEnvironment.objects.filter(
                    service__in=self.services.all(),
                ),
                date=date,
            ).values_list('type', flat=True).distinct()
        )
        ps = ps.exclude(excluded_services__in=self.services.all())
        if exclude:
            ps = ps.exclude(id__in=[p.id for p in exclude])
        # exclude self to prevent cycle
        ps = ps.exclude(id=self.id)
        return ps.distinct()


class ServiceUsageTypes(db.Model):
    usage_type = db.ForeignKey(
        'UsageType',
        verbose_name=_("Usage type"),
        related_name="service_division",
    )
    pricing_service = db.ForeignKey(
        PricingService,
        verbose_name=_("Pricing Service"),
    )
    start = db.DateField(verbose_name=_("start"), default=date.min)
    end = db.DateField(verbose_name=_("end"), default=date.max)
    percent = db.FloatField(
        validators=[
            MaxValueValidator(100.0),
            MinValueValidator(0.0)
        ],
        verbose_name=_("percent"),
        default=100,
    )

    class Meta:
        verbose_name = _("service usage type")
        verbose_name_plural = _("service usage types")
        app_label = 'ralph_scrooge'
        unique_together = ('usage_type', 'pricing_service', 'start', 'end')

    def __unicode__(self):
        return '{}/{} ({} - {})'.format(
            self.pricing_service,
            self.usage_type,
            self.start,
            self.end,
        )


class ServiceEnvironmentRelatedManager(db.Manager):
    def get_query_set(self):
        return super(
            ServiceEnvironmentRelatedManager,
            self
        ).get_query_set().select_related('service', 'environment')


class ServiceEnvironment(db.Model):
    objects_rel = ServiceEnvironmentRelatedManager()
    objects = db.Manager()

    service = db.ForeignKey(
        Service,
        related_name="environments_services",
        verbose_name=_("service"),
    )
    environment = db.ForeignKey(
        Environment,
        related_name='services_environments',
        verbose_name=_("environment"),
    )

    class Meta:
        verbose_name = _("service environment")
        verbose_name_plural = _("service environments")
        app_label = 'ralph_scrooge'
        unique_together = ('service', 'environment')
        ordering = ['service__name', 'environment__name']

    def __unicode__(self):
        return '{} - {}'.format(self.service, self.environment)

    @property
    def dummy_pricing_object(self):
        """
        Returns dummy pricing object for service environment
        """
        return self.pricing_objects.get_or_create(
            type_id=PRICING_OBJECT_TYPES.DUMMY
        )[0]

    def save(self, *args, **kwargs):
        result = super(ServiceEnvironment, self).save(*args, **kwargs)
        # call property to create dummy pricing object if not exists
        self.dummy_pricing_object
        return result
