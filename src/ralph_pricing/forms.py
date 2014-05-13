# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from mptt.forms import TreeNodeChoiceField

from ralph.ui.widgets import DateWidget
from ralph_pricing.models import (
    ExtraCost,
    TeamDaterange,
    TeamVenturePercent,
    UsagePrice,
    UsageType,
    Venture,
)
from ralph_pricing.utils import ranges_overlap


class ExtraCostForm(forms.ModelForm):
    """
    Used by factory to create ExtraCostFormSet. Contain basic form infromation
    like fields.
    """
    class Meta:
        model = ExtraCost
        fields = 'pricing_venture', 'monthly_cost'


class ExtraCostBaseFormSet(forms.models.BaseModelFormSet):
    """
    Used by factory to create ExtraCostFormSet. Contains validation.
    """
    def clean(self):
        if any(self.errors):
            return
        ventures_set = set()
        for form in self.forms:
            venture = form.cleaned_data.get('pricing_venture')
            if venture in ventures_set:
                form._errors['pricing_venture'] = form.error_class(
                    [_('Duplicated venture!')]
                )
                continue
            ventures_set.add(venture)


ExtraCostFormSet = forms.models.modelformset_factory(
    ExtraCost,
    form=ExtraCostForm,
    formset=ExtraCostBaseFormSet,
    can_delete=True,
    max_num=5
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
            'team',
            'team_members_count',
            'internet_provider',
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

    def clean_team(self):
        """
        If usage type is by_team check if team was provided
        """
        team = self.cleaned_data.get('team')
        if self.instance.type.by_team and not team:
            raise forms.ValidationError(_("Team missing"))
        return team

    def clean_internet_provider(self):
        """
        If usage type is by_team check if team was provided
        """
        internet_provider = self.cleaned_data.get('internet_provider')
        if self.instance.type.by_internet_provider and not internet_provider:
            raise forms.ValidationError(_("Internet Provider missing"))
        return internet_provider

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
        elif self.usage_type.by_team:
            additional_column = 'team'
        elif self.usage_type.by_internet_provider:
            additional_column = 'internet_provider'
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
                   (other_additional == additional_value and additional_column)
                   or not additional_column
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


class TeamDaterangeForm(forms.ModelForm):
    class Meta:
        model = TeamDaterange

        fields = ['start', 'end']

        widgets = {
            'start': DateWidget(attrs={'class': 'input-small'}),
            'end': DateWidget(attrs={'class': 'input-small'}),
        }

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


class TeamDaterangeBaseFormSet(forms.models.BaseModelFormSet):
    """
    Used by factory to create TeamDaterangeFormSet.
    Contains rules to validate correctness of dateranges.
    """
    def clean(self):
        if any(self.errors):
            return
        # check if dates are not-overlapping
        dates = []
        for form in self.forms:
            start = form.cleaned_data.get('start')
            end = form.cleaned_data.get('end')
            if start and end:
                dates.append((start, False))
                dates.append((end, True))
        dates = sorted(dates)
        for form in self.forms:
            open_intervals = 0
            start = form.cleaned_data.get('start')
            end = form.cleaned_data.get('end')
            if not (start and end):
                continue
            for date, is_end in dates:
                if date > end:
                    break
                if not is_end:
                    open_intervals += 1
                if date == end and open_intervals > 1:
                    form._errors['end'] = form.error_class([
                        "Overlaping intervals"
                    ])
                    break
                if is_end:
                    open_intervals -= 1

TeamDaterangeFormSet = forms.models.modelformset_factory(
    TeamDaterange,
    form=TeamDaterangeForm,
    formset=TeamDaterangeBaseFormSet,
    can_delete=True,
)


class TeamVenturePercentForm(forms.ModelForm):
    class Meta:
        model = TeamVenturePercent

        fields = ['venture', 'percent']

    def __init__(self, *args, **kwargs):
        super(TeamVenturePercentForm, self).__init__(*args, **kwargs)
        self.fields['venture'].queryset = Venture.objects.filter(
            is_active=True,
        ).order_by('name')


class TeamVenturePercentBaseFormSet(forms.models.BaseModelFormSet):
    """
    Used by factory to create TeamVenturePercentFormSet.
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


TeamVenturePercentFormSet = forms.models.modelformset_factory(
    TeamVenturePercent,
    form=TeamVenturePercentForm,
    formset=TeamVenturePercentBaseFormSet,
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
    is_active = forms.BooleanField(
        required=False,
        label=_("Show only active"),
    )
    forecast = forms.BooleanField(
        required=False,
        label=_("Forecast"),
    )


class DateRangeVentureForm(DateRangeForm):
    venture = TreeNodeChoiceField(
        queryset=Venture.tree.all(),
        level_indicator='|---',
        empty_label="---",
    )


class VenturesDailyUsagesForm(forms.Form):
    """Form schema. Used to generate venture daily usages reports"""
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
    is_active = forms.BooleanField(
        required=False,
        label=_("Show only active"),
    )
    usage_types = forms.ModelMultipleChoiceField(
        required=True,
        queryset=UsageType.objects.order_by('-order', 'name'),
        label=_("Usage types"),
    )
