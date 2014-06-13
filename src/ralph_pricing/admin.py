# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from lck.django.common.admin import ModelAdmin

from ralph_pricing import models


def register(model):
    def decorator(cls):
        admin.site.register(model, cls)
        return cls
    return decorator


class DailyDeviceInline(admin.TabularInline):
    model = models.DailyDevice


class DailyPartInline(admin.TabularInline):
    model = models.DailyPart


class DailyUsageInline(admin.TabularInline):
    model = models.DailyUsage


@register(models.Device)
class DeviceAdmin(ModelAdmin):
    list_display = ('name', 'sn', 'barcode')
    list_filter = ('is_virtual', 'is_blade')
    search_fields = ('name', 'sn', 'barcode')
    inlines = [DailyDeviceInline, DailyPartInline, DailyUsageInline]


class ExtraCostInline(admin.TabularInline):
    model = models.ExtraCost


@register(models.Venture)
class VentureAdmin(ModelAdmin):
    list_display = ('name', 'department', 'venture_id', 'business_segment',
                    'profit_center')
    list_filter = ('department', 'business_segment', 'profit_center')
    search_fields = ('name', 'venture_id', 'symbol')
    inlines = [ExtraCostInline]


class UsagePriceInline(admin.TabularInline):
    model = models.UsagePrice


@register(models.UsageType)
class UsageTypeAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [UsagePriceInline]


@register(models.ExtraCostType)
class ExtraCostTypeAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [ExtraCostInline]


@register(models.Warehouse)
class WarehouseAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@register(models.InternetProvider)
class InternetProviderAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ServiceUsageTypesInline(admin.TabularInline):
    model = models.ServiceUsageTypes


class ServiceForm(forms.ModelForm):
    class Meta:
        model = models.Service

    ventures = forms.ModelMultipleChoiceField(
        queryset=models.Venture.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Ventures', False),
    )

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['ventures'].initial = (
                self.instance.venture_set.exclude(service=None)
            )

    def save(self, commit=True):
        # NOTE: Previously assigned Ventures and their services are
        # silently reset
        instance = super(ServiceForm, self).save(commit=False)
        self.fields['ventures'].initial.update(service=None)
        instance.save()
        if self.cleaned_data['ventures']:
            self.cleaned_data['ventures'].update(service=instance)
        return instance


@register(models.Service)
class ServiceAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    form = ServiceForm
    inlines = [ServiceUsageTypesInline]


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


class TeamVenturesPercentInline(admin.TabularInline):
    model = models.TeamVenturePercent


@register(models.TeamDaterange)
class TeamDateranges(ModelAdmin):
    list_display = ('team', 'start', 'end')
    inlines = [TeamVenturesPercentInline]
