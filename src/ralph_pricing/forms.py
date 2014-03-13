# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import collections
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
    Venture,
    Warehouse,
)


class ExtraCostForm(forms.ModelForm):
    class Meta:
        model = ExtraCost
        fields = 'type', 'price', 'start', 'end'
        widgets = {
            'start': DateWidget(attrs={'class': 'input-small'}),
            'end': DateWidget(attrs={'class': 'input-small'}),
        }

    def clean_end(self):
        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
        if start > end:
            raise forms.ValidationError(
                _("End date must be later than or equal to the start date."),
            )
        return end


class ExtraCostBaseFormSet(forms.models.BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return
        types = collections.defaultdict(list)
        for i in xrange(self.total_form_count()):
            form = self.forms[i]
            type_ = form.cleaned_data.get('type')
            start = form.cleaned_data.get('start')
            end = form.cleaned_data.get('end')
            if not type_ or not start or not end:
                continue
            for other_start, other_end in types[type_]:
                if other_start <= start <= other_end:
                    form._errors['start'] = form.error_class([
                        _("Start date overlaps with an existing extra "
                            "cost of the same type."),
                    ])
                    break
                if other_start <= end <= other_end:
                    form._errors['end'] = form.error_class([
                        _("End date overlaps with an existing extra "
                            "cost of the same type."),
                    ])
                    break
                if start <= other_start <= end:
                    form._errors['start'] = form.error_class([
                        _("A start date of an existing extra cost of "
                            "the same type overlaps with this time span."),
                    ])
                    break
                if start <= other_end <= end:
                    form._errors['start'] = form.error_class([
                        _("An end date of an existing extra cost of "
                            "the same type overlaps with this time span."),
                    ])
                    break
            else:
                types[type_].append((start, end))


ExtraCostFormSet = forms.models.modelformset_factory(
    ExtraCost,
    form=ExtraCostForm,
    formset=ExtraCostBaseFormSet,
    can_delete=True,
)


class UsagePriceForm(forms.ModelForm):
    '''
    Used by factory to create UsagesFormSet. Contain baisc form infromation
    like fields and widgets
    '''
    class Meta:
        model = UsagePrice

        fields = [
            'warehouse',
            'team',
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

    def clean_end(self):
        '''
        Test if end date is later or equal to the start date

        :returns string: the end of the time interval
        :rtype string:
        '''
        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
        if start > end:
            raise forms.ValidationError(
                _("End date must be later than or equal to the start date."),
            )
        return end


class UsagesBaseFormSet(forms.models.BaseModelFormSet):
    '''
    Used by factory to create UsagesFormSet. Contains rules to validate
    unique and correct data for each type of usage
    '''
    def clean(self):
        if any(self.errors):
            return
        dates = []
        for i in xrange(self.total_form_count()):
            form = self.forms[i]
            start = form.cleaned_data.get('start')
            end = form.cleaned_data.get('end')
            warehouse = form.cleaned_data.get('warehouse')
            if not start or not end:
                continue

            for other_start, other_end, other_warehouse in dates:
                if (other_start <= start <= other_end
                        and other_warehouse == warehouse):
                    form._errors['start'] = form.error_class([
                        _("Start date overlaps with an existing extra "
                            "cost of the same type and warehouse."),
                    ])
                    break
                if (other_start <= end <= other_end
                        and other_warehouse == warehouse):
                    form._errors['end'] = form.error_class([
                        _("End date overlaps with an existing extra "
                            "cost of the same type and warehouse."),
                    ])
                    break
                if (start <= other_start <= end
                        and other_warehouse == warehouse):
                    form._errors['start'] = form.error_class([
                        _("A start date of an existing extra cost of "
                            "the same type and warehouse overlaps with "
                            "this time span."),
                    ])
                    break
                if (start <= other_end <= end
                        and other_warehouse == warehouse):
                    form._errors['start'] = form.error_class([
                        _("An end date of an existing extra cost of "
                            "the same type and warehouse overlaps with "
                            "this time span."),
                    ])
                    break
            else:
                dates.append((start, end, warehouse))


UsagesFormSet = forms.models.modelformset_factory(
    UsagePrice,
    form=UsagePriceForm,
    formset=UsagesBaseFormSet,
    can_delete=True,
)


class TeamDaterangeForm(forms.ModelForm):
    class Meta:
        model = TeamDaterange

        fields = [
            'start',
            'end',
        ]

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
        # check if dates are not-overlaping
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

        fields = [
            'venture',
            'percent',
        ]


class TeamVenturePercentBaseFormSet(forms.models.BaseModelFormSet):
    """
    Used by factory to create TeamVenturePercentFormSet.
    Contains rules to validate correctness of
    """
    def clean(self):
        if any(self.errors):
            return
        # check if sum of percents is 100
        percent = [f.cleaned_data.get('percent') or 0 for f in self.forms]
        if sum(percent) != 100.0:
            for form in self.forms:
                if form.cleaned_data.get('percent') is not None:
                    form._errors['percent'] = form.error_class([
                        "Sum of percent different than 100"
                    ])


TeamVenturePercentFormSet = forms.models.modelformset_factory(
    TeamVenturePercent,
    form=TeamVenturePercentForm,
    formset=TeamVenturePercentBaseFormSet,
    can_delete=True,
    extra=5,
)


class DateRangeForm(forms.Form):
    '''Form schema. Used to generate venture raports'''
    warehouse = forms.ModelChoiceField(
        empty_label=None,
        queryset=Warehouse.objects.all(),
    )
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
