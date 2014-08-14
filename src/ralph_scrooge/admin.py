# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
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


@register(models.PricingObject)
class PricingObjectAdmin(UpdateReadonlyMixin, ModelAdmin):
    list_display = ('name', 'service', 'type', 'remarks',)
    search_fields = ('name', 'service_environment__service__name', 'remarks',)
    list_filter = ('type', )
    readonly_when_update = ('type', )
    inlines = [AssetInfoInline, VirtualInfoInline, TenantInfoInline]

    def service(self, obj):
        return obj.service_environment.service


# =============================================================================
# USAGE TYPES
# =============================================================================
class UsageTypeForm(forms.ModelForm):
    class Meta:
        model = models.UsageType
        widgets = {
            'excluded_ventures': FilteredSelectMultiple('Ventures', False)
        }


class UsagePriceInline(admin.TabularInline):
    model = models.UsagePrice


@register(models.UsageType)
class UsageTypeAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [UsagePriceInline]
    form = UsageTypeForm


@register(models.InternetProvider)
class InternetProviderAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


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


# =============================================================================
# SERVICE
# =============================================================================
@register(models.BusinessLine)
class BusinessLineAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@register(models.Environment)
class EnvironmentAdmin(UpdateReadonlyMixin, ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_when_update = ('environment_id', )


@register(models.Owner)
class OwnerAdmin(ModelAdmin):
    list_display = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name')


class ServiceOwnershipInline(admin.TabularInline):
    model = models.ServiceOwnership


class ServiceEnvironmentsInline(admin.TabularInline):
    model = models.ServiceEnvironment


@register(models.Service)
class ServiceAdmin(SimpleHistoryAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [ServiceOwnershipInline, ServiceEnvironmentsInline]


# =============================================================================
# PRICING SERVICE
# =============================================================================
class ServiceUsageTypesInline(admin.TabularInline):
    model = models.ServiceUsageTypes


@register(models.PricingService)
class PricingServiceAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
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
