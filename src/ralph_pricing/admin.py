# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib import admin
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


class ServiceUsageTypesInline(admin.TabularInline):
    model = models.ServiceUsageTypes


@register(models.Service)
class ServiceAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [ServiceUsageTypesInline]
