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
    inlines = [DailyDeviceInline, DailyPartInline, DailyUsageInline]


class ExtraCostInline(admin.TabularInline):
    model = models.ExtraCost


@register(models.Venture)
class VentureAdmin(ModelAdmin):
    inlines = [ExtraCostInline]


class UsagePriceInline(admin.TabularInline):
    model = models.UsagePrice


@register(models.UsageType)
class UsageTypeAdmin(ModelAdmin):
    inlines = [UsagePriceInline]


@register(models.ExtraCostType)
class ExtraCostTypeAdmin(ModelAdmin):
    inlines = [ExtraCostInline]


@register(models.SplunkName)
class SplunkNameAdmin(ModelAdmin):
    list_display = ('splunk_name', 'pricing_device')
