# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _
from lck.django.common.admin import ModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from ralph_scrooge import models


def register(model):
    def decorator(cls):
        admin.site.register(model, cls)
        return cls
    return decorator


class UpdateReadonlyMixin(object):
    readonly_when_update = ()

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return list(self.readonly_fields) + list(self.readonly_when_update)
        return self.readonly_fields


# =============================================================================
# WAREHOUSE
# =============================================================================
@register(models.Warehouse)
class WarehouseAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# =============================================================================
# PRICING OBJECT
# =============================================================================
class PricingObjectChildInlineBase(admin.StackedInline):
    show_type = None
    exclude = [
        f.name for f in models.PricingObject._meta.fields if f.name not in (
            'id',
            'cache_version',
        )
    ]


class AssetInfoInline(UpdateReadonlyMixin, PricingObjectChildInlineBase):
    model = models.AssetInfo
    readonly_when_update = ('asset_id', )


class VirtualInfoInline(UpdateReadonlyMixin, PricingObjectChildInlineBase):
    model = models.VirtualInfo
    readonly_when_update = ('device_id', )


class TenantInfoInline(UpdateReadonlyMixin, PricingObjectChildInlineBase):
    model = models.TenantInfo
    readonly_when_update = ('tenant_id', )


class PricingObjectTypeFilter(SimpleListFilter):
    """
    Hides dummy pricing object type on filter list
    """
    title = _('type')
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        return [
            (t.id, t.name) for t in models.PricingObjectType.objects.exclude(
                id__in=[models.PRICING_OBJECT_TYPES.DUMMY]
            )
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(type_id=self.value())
        else:
            return queryset


@register(models.PricingObject)
class PricingObjectAdmin(UpdateReadonlyMixin, ModelAdmin):
    list_display = ('name', 'service', 'type', 'remarks',)
    search_fields = ('name', 'service_environment__service__name', 'remarks',)
    list_filter = (PricingObjectTypeFilter,)
    filter_exclude = ['created_by', 'modified_by']
    inlines = [AssetInfoInline, VirtualInfoInline, TenantInfoInline]
    # TODO: display inlines based on pricing object type

    def service(self, obj):
        return obj.service_environment.service

    def get_readonly_fields(self, request, obj=None):
        """
        Allows to change pricing object type when unknown
        """
        if obj and obj.type_id == models.PRICING_OBJECT_TYPES.UNKNOWN:
            self.readonly_when_update = tuple()
        else:
            self.readonly_when_update = ('type', )
        return super(PricingObjectAdmin, self).get_readonly_fields(
            request,
            obj
        )

    def queryset(self, request):
        """
        Do not display dummy pricing objects
        """
        result = super(PricingObjectAdmin, self).queryset(request)
        return result.exclude(
            type_id=models.PRICING_OBJECT_TYPES.DUMMY
        ).select_related(
            'service_environment',
            'service_environment__service',
        )


# =============================================================================
# USAGE TYPES
# =============================================================================
class UsageTypeForm(forms.ModelForm):
    class Meta:
        model = models.UsageType
        widgets = {
            'excluded_services': FilteredSelectMultiple('Service', False)
        }


class UsagePriceInline(admin.TabularInline):
    model = models.UsagePrice


@register(models.UsageType)
class UsageTypeAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [UsagePriceInline]
    form = UsageTypeForm


# =============================================================================
# EXTRA COSTS
# =============================================================================
class ExtraCostInline(admin.TabularInline):
    model = models.ExtraCost


@register(models.ExtraCostType)
class ExtraCostTypeAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [ExtraCostInline]


class DynamicExtraCostDivisionInline(admin.TabularInline):
    model = models.DynamicExtraCostDivision


class DynamicExtraCostInline(admin.TabularInline):
    model = models.DynamicExtraCost


class DynamicExtraTypeForm(forms.ModelForm):
    class Meta:
        model = models.DynamicExtraCostType
        widgets = {
            'excluded_services': FilteredSelectMultiple('Service', False)
        }


@register(models.DynamicExtraCostType)
class DynamicExtraCostTypeAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [DynamicExtraCostDivisionInline, DynamicExtraCostInline]
    form = DynamicExtraTypeForm


# =============================================================================
# SERVICE
# =============================================================================
@register(models.BusinessLine)
class BusinessLineAdmin(UpdateReadonlyMixin, ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_when_update = ('ci_id', 'ci_uid')


@register(models.Environment)
class EnvironmentAdmin(UpdateReadonlyMixin, ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_when_update = ('ci_id', 'ci_uid')


@register(models.Owner)
class OwnerAdmin(ModelAdmin):
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')

    def first_name(self, obj):
        return obj.profile.user.first_name

    def last_name(self, obj):
        return obj.profile.user.last_name


class ServiceOwnershipInline(admin.TabularInline):
    model = models.ServiceOwnership


class ServiceEnvironmentsInline(admin.TabularInline):
    model = models.ServiceEnvironment


@register(models.Service)
class ServiceAdmin(UpdateReadonlyMixin, SimpleHistoryAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [ServiceOwnershipInline, ServiceEnvironmentsInline]
    readonly_when_update = ('ci_id', 'ci_uid')


# =============================================================================
# PRICING SERVICE
# =============================================================================
class PricingServiceForm(forms.ModelForm):
    class Meta:
        model = models.PricingService

    services = forms.ModelMultipleChoiceField(
        help_text=_('Services used to calculate costs of Pricing Service'),
        queryset=models.Service.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Services', False),

    )

    def __init__(self, *args, **kwargs):
        super(PricingServiceForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['services'].initial = (
                self.instance.services.exclude(pricing_service=None)
            )

    def save(self, commit=True):
        # NOTE: Previously assigned Services and their pricing services are
        # silently reset
        instance = super(PricingServiceForm, self).save(commit=False)
        self.fields['services'].initial.update(pricing_service=None)
        instance.save()
        if self.cleaned_data['services']:
            self.cleaned_data['services'].update(pricing_service=instance)
        return instance


class ServiceUsageTypesInline(admin.TabularInline):
    model = models.ServiceUsageTypes


@register(models.PricingService)
class PricingServiceAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    form = PricingServiceForm
    inlines = [ServiceUsageTypesInline]


# =============================================================================
# TEAMS
# =============================================================================
class TeamCostInline(admin.TabularInline):
    model = models.TeamCost


class TeamForm(forms.ModelForm):
    class Meta:
        model = models.Team
        widgets = {
            'excluded_ventures': FilteredSelectMultiple('Ventures', False)
        }


@register(models.Team)
class TeamAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [TeamCostInline]
    form = TeamForm


class TeamServiceEnvironmentPercentInline(admin.TabularInline):
    model = models.TeamServiceEnvironmentPercent


@register(models.TeamCost)
class TeamCostAdmin(UpdateReadonlyMixin, ModelAdmin):
    list_display = ('team', 'start', 'end')
    search_fields = ('team__name', 'start', 'end',)
    list_filter = ('team__name', )
    readonly_when_update = ('team', )
    inlines = [TeamServiceEnvironmentPercentInline]

    def team_name(self, obj):
        return obj.team.service

    def queryset(self, request):
        result = super(TeamCostAdmin, self).queryset(request)
        return result.filter(team__billing_type=models.TeamBillingType.time)
