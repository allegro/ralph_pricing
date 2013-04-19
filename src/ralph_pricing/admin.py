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
    verbose_name = "Daily device"
    verbose_name_plural = "Daily devices"

class DailyPartInline(admin.TabularInline):
    model = models.DailyDevice
    verbose_name = "Daily part"
    verbose_name_plural = "Daily parts"

class DailyUsageInline(admin.TabularInline):
    model = models.DailyUsage
    verbose_name = "Daily usage"
    verbose_name_plural = "Daily usages"

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
    pass


