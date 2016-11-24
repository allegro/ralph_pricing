# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UsernameField
from django.utils.translation import ugettext_lazy as _
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


class ScroogeUserChangeForm(UserChangeForm):
    class Meta:
        model = models.ScroogeUser
        fields = '__all__'
        field_classes = {'username': UsernameField}


@register(models.ScroogeUser)
class ScroogeUserAdmin(UserAdmin):

    form = ScroogeUserChangeForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


# =============================================================================
# WAREHOUSE
# =============================================================================
@register(models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_in_report')
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


class VIPInfoInline(
    UpdateReadonlyMixin,
    PricingObjectChildInlineBase
):
    model = models.VIPInfo
    readonly_when_update = ('vip_id', )
    fk_name = 'pricingobject_ptr'
    related_search_fields = {
        'ip_info': ['^name'],
        'load_balancer': ['^name'],
    }


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
class PricingObjectAdmin(UpdateReadonlyMixin, admin.ModelAdmin):
    list_display = ('name', 'service', 'type', 'remarks',)
    search_fields = ('name', 'service_environment__service__name', 'remarks',)
    list_filter = (PricingObjectTypeFilter,)
    filter_exclude = ['created_by', 'modified_by']
    inlines = [
        AssetInfoInline,
        VirtualInfoInline,
        TenantInfoInline,
        VIPInfoInline,
    ]
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
        )


# =============================================================================
# USAGE TYPES
# =============================================================================
class UsageTypeForm(forms.ModelForm):
    class Meta:
        model = models.UsageType
        fields = '__all__'
        widgets = {
            'excluded_services': FilteredSelectMultiple('Service', False),
            'owners': FilteredSelectMultiple('ScroogeUser', False),
        }


class UsagePriceInline(admin.TabularInline):
    model = models.UsagePrice


@register(models.UsageType)
class UsageTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol',)
    search_fields = ('name', 'symbol',)
    inlines = [UsagePriceInline]
    form = UsageTypeForm


# =============================================================================
# EXTRA COSTS
# =============================================================================
class ExtraCostInline(admin.TabularInline):
    model = models.ExtraCost


@register(models.ExtraCostType)
class ExtraCostTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'active')
    search_fields = ('name',)
    readonly_fields = ('symbol',)
    inlines = [ExtraCostInline]


class DynamicExtraCostDivisionInline(admin.TabularInline):
    model = models.DynamicExtraCostDivision


class DynamicExtraCostInline(admin.TabularInline):
    model = models.DynamicExtraCost


class DynamicExtraTypeForm(forms.ModelForm):
    class Meta:
        model = models.DynamicExtraCostType
        fields = '__all__'
        widgets = {
            'excluded_services': FilteredSelectMultiple('Service', False)
        }


@register(models.DynamicExtraCostType)
class DynamicExtraCostTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'active')
    search_fields = ('name',)
    readonly_fields = ('symbol',)
    inlines = [DynamicExtraCostDivisionInline, DynamicExtraCostInline]
    form = DynamicExtraTypeForm


# =============================================================================
# SERVICE
# =============================================================================
@register(models.BusinessLine)
class BusinessLineAdmin(UpdateReadonlyMixin, admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_when_update = ('ci_id', 'ci_uid')


@register(models.Environment)
class EnvironmentAdmin(UpdateReadonlyMixin, admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_when_update = ('ci_id', 'ci_uid')


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
        fields = '__all__'
        widgets = {
            'excluded_services': FilteredSelectMultiple('Service', False)
        }

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
class PricingServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'active')
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
        fields = '__all__'
        widgets = {
            'excluded_services': FilteredSelectMultiple('Service', False)
        }


@register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'active')
    search_fields = ('name',)
    inlines = [TeamCostInline]
    form = TeamForm


class TeamServiceEnvironmentPercentInline(admin.TabularInline):
    model = models.TeamServiceEnvironmentPercent


@register(models.TeamCost)
class TeamCostAdmin(UpdateReadonlyMixin, admin.ModelAdmin):
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
