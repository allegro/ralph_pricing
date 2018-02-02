# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from dal import autocomplete
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
    readonly_fields = ('api_token_key',)
    fieldsets = (
        (None, {'fields': ('username', 'password', 'api_token_key')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def get_queryset(self, *args, **kwargs):
        return super(ScroogeUserAdmin, self).get_queryset(
            *args, **kwargs
        ).select_related(
            'auth_token'
        )


# =============================================================================
# WAREHOUSE
# =============================================================================
@register(models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_in_report')
    search_fields = ('name',)
    exclude = ('created_by', 'modified_by')
    readonly_fields = ('created', 'modified')


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


class VIPInfoInlineForm(forms.ModelForm):
    class Meta:
        model = models.VIPInfo
        fields = '__all__'
        widgets = {
            'ip_info': autocomplete.ModelSelect2(
                url='autocomplete:pricing-object'
            ),
            'load_balancer': autocomplete.ModelSelect2(
                url='autocomplete:pricing-object'
            ),
        }


class VIPInfoInline(
    UpdateReadonlyMixin,
    PricingObjectChildInlineBase
):
    model = models.VIPInfo
    form = VIPInfoInlineForm
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


class PricingObjectForm(forms.ModelForm):
    class Meta:
        model = models.PricingObject
        fields = '__all__'
        widgets = {
            'service_environment': autocomplete.ModelSelect2(
                url='autocomplete:service-environment'
            ),
            'model': autocomplete.ModelSelect2(
                url='autocomplete:pricing-object-model'
            ),
        }


@register(models.PricingObject)
class PricingObjectAdmin(UpdateReadonlyMixin, admin.ModelAdmin):
    form = PricingObjectForm
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
    exclude = ('created_by', 'modified_by')
    readonly_fields = ('created', 'modified')
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
    list_display = ('name', 'symbol', 'active', 'usage_type', 'get_owners')
    search_fields = ('name', 'symbol',)
    list_filter = ('active', 'usage_type',)
    inlines = [UsagePriceInline]
    form = UsageTypeForm

    def get_queryset(self, *args, **kwargs):
        qs = super(UsageTypeAdmin, self).get_queryset(*args, **kwargs)
        return qs.prefetch_related('owners')

    def get_owners(self, usage_type):
        return ', '.join(map(unicode, usage_type.owners.all()))
    get_owners.short_description = _('Owners')


# =============================================================================
# EXTRA COSTS
# =============================================================================
class ExtraCostInlineForm(forms.ModelForm):
    class Meta:
        model = models.ExtraCost
        fields = '__all__'
        widgets = {
            'service_environment': autocomplete.ModelSelect2(
                url='autocomplete:service-environment'
            ),
        }


class ExtraCostInline(admin.TabularInline):
    model = models.ExtraCost
    form = ExtraCostInlineForm

    def get_queryset(self, *args, **kwargs):
        qs = super(ExtraCostInline, self).get_queryset(*args, **kwargs)
        return qs.select_related(
            'extra_cost_type',
            'service_environment__service',
            'service_environment__environment',
        )


@register(models.ExtraCostType)
class ExtraCostTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'active')
    search_fields = ('name',)
    readonly_fields = ('symbol',)
    inlines = [ExtraCostInline]


class DynamicExtraCostDivisionInlineForm(forms.ModelForm):
    class Meta:
        model = models.DynamicExtraCostDivision
        fields = '__all__'
        widgets = {
            'usage_type': autocomplete.ModelSelect2(
                url='autocomplete:usage-type'
            ),
        }


class DynamicExtraCostDivisionInline(admin.TabularInline):
    model = models.DynamicExtraCostDivision
    form = DynamicExtraCostDivisionInlineForm

    def get_queryset(self, *args, **kwargs):
        qs = super(DynamicExtraCostDivisionInline, self).get_queryset(
            *args, **kwargs
        )
        return qs.select_related(
            'dynamic_extra_cost_type',
        )


class DynamicExtraCostInline(admin.TabularInline):
    model = models.DynamicExtraCost


class DynamicExtraTypeForm(forms.ModelForm):
    class Meta:
        model = models.DynamicExtraCostType
        fields = '__all__'
        widgets = {
            'excluded_services': FilteredSelectMultiple('Service', False),
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


class ServiceOwnershipInlineForm(forms.ModelForm):
    class Meta:
        model = models.ServiceOwnership
        fields = '__all__'
        widgets = {
            'owner': autocomplete.ModelSelect2(
                url='autocomplete:scrooge-user'
            ),
        }


class ServiceOwnershipInline(admin.TabularInline):
    model = models.ServiceOwnership
    form = ServiceOwnershipInlineForm

    def get_queryset(self, *args, **kwargs):
        return super(ServiceOwnershipInline, self).get_queryset(
            *args, **kwargs
        ).select_related(
            'owner'
        )


class ServiceEnvironmentsInline(admin.TabularInline):
    model = models.ServiceEnvironment

    def get_queryset(self, *args, **kwargs):
        return super(ServiceEnvironmentsInline, self).get_queryset(
            *args, **kwargs
        ).select_related(
            'environment'
        )


class ServiceAdminForm(forms.ModelForm):
    class Meta:
        model = models.Service
        widgets = {
            'profit_center': autocomplete.ModelSelect2(
                url='autocomplete:profit-center'
            ),
            'pricing_service': autocomplete.ModelSelect2(
                url='autocomplete:pricing-service'
            )
        }
        exclude = ()


@register(models.Service)
class ServiceAdmin(UpdateReadonlyMixin, SimpleHistoryAdmin):
    form = ServiceAdminForm
    list_display = ('name', 'ci_uid')
    search_fields = ('name', 'ci_uid')
    inlines = [ServiceOwnershipInline, ServiceEnvironmentsInline]
    readonly_when_update = ('ci_id', 'ci_uid')
    exclude = ('created_by', 'modified_by')
    readonly_fields = ('created', 'modified')


# =============================================================================
# PRICING SERVICE
# =============================================================================
class PricingServiceForm(forms.ModelForm):
    class Meta:
        model = models.PricingService
        fields = '__all__'
        widgets = {
            'excluded_services': FilteredSelectMultiple('Service', False),
            'charge_diff_to_real_costs': autocomplete.ModelSelect2(
                url='autocomplete:pricing-service'
            )
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


class ServiceUsageTypesInlineForm(forms.ModelForm):
    class Meta:
        model = models.ServiceUsageTypes
        fields = '__all__'
        widgets = {
            'usage_type': autocomplete.ModelSelect2(
                url='autocomplete:usage-type'
            )
        }


class ServiceUsageTypesInline(admin.TabularInline):
    model = models.ServiceUsageTypes
    form = ServiceUsageTypesInlineForm

    def get_queryset(self, *args, **kwargs):
        qs = super(ServiceUsageTypesInline, self).get_queryset(*args, **kwargs)
        return qs.select_related(
            'pricing_service',
            'usage_type',
        )


@register(models.PricingService)
class PricingServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'active', 'plugin_type', 'get_services')
    search_fields = ('name', 'symbol',)
    list_filter = ('active', 'plugin_type',)
    form = PricingServiceForm
    inlines = [ServiceUsageTypesInline]

    def get_queryset(self, *args, **kwargs):
        qs = super(PricingServiceAdmin, self).get_queryset(*args, **kwargs)
        return qs.prefetch_related('services')

    def get_services(self, pricing_service):
        return ', '.join(map(unicode, pricing_service.services.all()))
    get_services.short_description = _('Services')


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
            'excluded_services': FilteredSelectMultiple('Service', False),
        }


@register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'active', 'billing_type',)
    list_filter = ('active', 'billing_type',)
    search_fields = ('name',)
    inlines = [TeamCostInline]
    form = TeamForm
    exclude = ('created_by', 'modified_by')
    readonly_fields = ('created', 'modified')


class TeamServiceEnvironmentPercentInlineForm(forms.ModelForm):
    class Meta:
        model = models.TeamServiceEnvironmentPercent
        fields = '__all__'
        widgets = {
            'service_environment': autocomplete.ModelSelect2(
                url='autocomplete:service-environment'
            ),
        }


class TeamServiceEnvironmentPercentInline(admin.TabularInline):
    model = models.TeamServiceEnvironmentPercent
    form = TeamServiceEnvironmentPercentInlineForm

    def get_queryset(self, *args, **kwargs):
        qs = super(TeamServiceEnvironmentPercentInline, self).get_queryset(
            *args, **kwargs
        )
        return qs.select_related(
            'team_cost__team',
            'service_environment__service',
            'service_environment__environment',
        )


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
