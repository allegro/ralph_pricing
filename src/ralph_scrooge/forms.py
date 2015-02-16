# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from ralph.ui.widgets import DateWidget
from ralph_scrooge.models import (
    ExtraCost,
    Service,
    TeamServiceEnvironmentPercent,
    UsagePrice,
    UsageType,
)
from ralph_scrooge.management.commands.scrooge_sync import (
    get_collect_plugins_names,
)
from ralph_scrooge.utils.common import ranges_overlap


class ExtraCostForm(forms.ModelForm):
    """
    Used by factory to create ExtraCostFormSet. Contain basic form infromation
    like fields.
    """
    class Meta:
        model = ExtraCost
        fields = 'service_environment', 'cost', 'start', 'end'

        widgets = {
            'start': DateWidget(attrs={'class': 'input-small'}),
            'end': DateWidget(attrs={'class': 'input-small'}),
        }


class ExtraCostBaseFormSet(forms.models.BaseModelFormSet):
    """
    Used by factory to create ExtraCostFormSet. Contains validation.
    """
    def clean(self):
        if any(self.errors):
            return


ExtraCostFormSet = forms.models.modelformset_factory(
    ExtraCost,
    form=ExtraCostForm,
    formset=ExtraCostBaseFormSet,
    can_delete=True,
    extra=5,
)


class UsagePriceForm(forms.ModelForm):
    """
    Used by factory to create UsagesFormSet. Contain basic form infromation
    like fields and widgets and simple validation like warehouse and team
    presence.
    """
    class Meta:
        model = UsagePrice

        fields = [
            'warehouse',
            'forecast_price',
            'price',
            'forecast_cost',
            'cost',
            'start',
            'end',
        ]

        widgets = {
            'start': DateWidget(attrs={'class': 'input-small'}),
            'end': DateWidget(attrs={'class': 'input-small'}),
        }

    def clean_warehouse(self):
        """
        If usage type is by_warehouse check if warehouse was provided
        """
        warehouse = self.cleaned_data.get('warehouse')
        if self.instance.type.by_warehouse and not warehouse:
            raise forms.ValidationError(_("Warehouse missing"))
        return warehouse

    def clean_end(self):
        """
        Test if end date is later or equal to the start date

        :returns string: the end of the time interval
        :rtype string:
        """
        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
        if start > end:
            raise forms.ValidationError(
                _("End date must be later than or equal to the start date."),
            )
        return end


class UsagesBaseFormSet(forms.models.BaseModelFormSet):
    """
    Used by factory to create UsagesFormSet. Contains rules to validate
    unique and correct data for each type of usage
    """
    def clean(self):
        if any(self.errors):
            return
        dates = []
        additional_column = None
        if self.usage_type.by_warehouse:
            additional_column = 'warehouse'
        msg = _("Another cost time interval with the same type "
                "(and warehouse/team/internet_provider) overlaps with this "
                "time interval.")

        for i in xrange(self.total_form_count()):
            form = self.forms[i]
            start = form.cleaned_data.get('start')
            end = form.cleaned_data.get('end')
            additional_value = form.cleaned_data.get(additional_column)
            if not start or not end:
                continue
            for other_start, other_end, other_additional in dates:
                # if additional values (eg. warehouse or team) are the same
                # or there is no additional column and dateranges are
                # overlapping
                if (
                   (other_additional == additional_value and
                    additional_column) or not
                   additional_column
                   ) and ranges_overlap(start, end, other_start, other_end):
                    form._errors['start'] = form.error_class([msg])
                    form._errors['end'] = form.error_class([msg])
                    break
            else:
                dates.append((start, end, additional_value))


UsagesFormSet = forms.models.modelformset_factory(
    UsagePrice,
    form=UsagePriceForm,
    formset=UsagesBaseFormSet,
    can_delete=True,
    extra=3,
)


class TeamServiceEnvironmentPercentForm(forms.ModelForm):
    class Meta:
        model = TeamServiceEnvironmentPercent

        fields = ['service_environment', 'percent']

    def __init__(self, *args, **kwargs):
        super(TeamServiceEnvironmentPercent, self).__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.order_by('name')


class TeamServiceEnvironmentPercentBaseFormSet(forms.models.BaseModelFormSet):
    """
    Used by factory to create TeamServiceEnvironmentPercentFormSet.
    Contains rules to validate correctness of
    """
    def clean(self):
        if any(self.errors):
            return
        # check if sum of percents is 100
        percent = [round(float(f.cleaned_data.get('percent') or 0), 2)
                   for f in self.forms]
        if abs(sum(percent) - 100.0) > 0.001:
            for form in self.forms:
                if form.cleaned_data.get('percent') is not None:
                    form._errors['percent'] = form.error_class([
                        "Sum of percent different than 100"
                    ])
        # check ventures uniqueness
        seen = set()
        for form in self.forms:
            venture = form.cleaned_data.get('venture')
            if venture:
                if venture in seen:
                    form._errors['venture'] = form.error_class([
                        "Venture not unique"
                    ])
                seen.add(venture)


TeamServiceEnvironmentPercentFormSet = forms.models.modelformset_factory(
    TeamServiceEnvironmentPercent,
    form=TeamServiceEnvironmentPercentForm,
    formset=TeamServiceEnvironmentPercentBaseFormSet,
    can_delete=True,
    extra=5,
)


class DateRangeForm(forms.Form):
    '''Form schema. Used to generate venture raports'''
    start = forms.DateField(
        widget=DateWidget(
            attrs={'class': 'input-small'},
        ),
        label='',
        initial=lambda: datetime.date.today() - datetime.timedelta(days=30),
    )
    end = forms.DateField(
        widget=DateWidget(
            attrs={'class': 'input-small'},
        ),
        label='',
        initial=datetime.date.today,
    )

collect_plugins_names = get_collect_plugins_names()


class CollectPluginsForm(DateRangeForm):
    plugins = forms.MultipleChoiceField(
        required=True,
        choices=zip(collect_plugins_names, collect_plugins_names),
    )


class MonthlyCostsForm(DateRangeForm):
    forecast = forms.BooleanField(
        required=False,
        label=_("Forecast"),
    )


# =============================================================================
# REPORTS FORMS
# =============================================================================
class ServicesCostsReportForm(DateRangeForm):
    forecast = forms.BooleanField(
        required=False,
        label=_("Forecast"),
    )
    is_active = forms.BooleanField(
        required=False,
        label=_("Show only active"),
    )


class DeviceReportForm(DateRangeForm):
    forecast = forms.BooleanField(
        required=False,
        label=_("Forecast"),
    )
    # use_subventures = forms.BooleanField(
    #     required=False,
    #     initial=True,
    #     label=_("Use subventures"),
    # )
    # venture = TreeNodeChoiceField(
    #     required=True,
    #     queryset=Venture.tree.all(),
    #     level_indicator='|---',
    #     empty_label="---",
    # )
    service = forms.ModelChoiceField(queryset=Service.objects.all())


class ServicesUsagesReportForm(DateRangeForm):
    """
    Form schema. Used to generate services environments daily usages report
    """
    is_active = forms.BooleanField(
        required=False,
        label=_("Show only active"),
    )
    usage_types = forms.ModelMultipleChoiceField(
        required=True,
        queryset=UsageType.objects.order_by('-order', 'name'),
        label=_("Usage types"),
    )


class ServicesChangesReportForm(DateRangeForm):
    """Form schema. Used to generate services changes reports"""
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        required=False,
    )
