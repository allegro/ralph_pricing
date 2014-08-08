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


@register(models.Warehouse)
class WarehouseAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# =============================================================================
# PRICING OBJECT
# =============================================================================
class AssetInfoInline(admin.StackedInline):
    model = models.AssetInfo


class VirtualInfoInline(admin.StackedInline):
    model = models.VirtualInfo


@register(models.PricingObject)
class PricingObjectAdmin(ModelAdmin):
    list_display = ('name', 'service', 'type', 'remarks',)
    search_fields = ('name', 'service__name', 'remarks',)
    list_filter = ('type', )
    inlines = [AssetInfoInline, VirtualInfoInline]


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


@register(models.Owner)
class OwnerAdmin(ModelAdmin):
    list_display = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name')


class ServiceOwnershipInline(admin.TabularInline):
    model = models.ServiceOwnership

# class ServiceForm(forms.ModelForm):
#     class Meta:
#         model = models.Service

#     def save(self, commit=True):
#         # NOTE: Previously assigned Ventures and their services are
#         # silently reset
#         instance = super(ServiceForm, self).save(commit=False)
#         self.fields['ventures'].initial.update(service=None)
#         instance.save()
#         if self.cleaned_data['ventures']:
#             self.cleaned_data['ventures'].update(service=instance)
#         return instance


@register(models.Service)
class ServiceAdmin(SimpleHistoryAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [ServiceOwnershipInline]


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
class TeamDaterangesInline(admin.TabularInline):
    model = models.TeamDaterange


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
    inlines = [
        UsagePriceInline,
        TeamDaterangesInline
    ]
    form = TeamForm


class TeamServicesPercentInline(admin.TabularInline):
    model = models.TeamServicePercent


@register(models.TeamDaterange)
class TeamDateranges(ModelAdmin):
    list_display = ('team', 'start', 'end')
    inlines = [TeamServicesPercentInline]
