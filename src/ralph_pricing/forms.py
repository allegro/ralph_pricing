# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django import forms
from ralph.ui.widgets import DateWidget

from ralph_pricing.models import ExtraCost


class ExtraCostForm(forms.ModelForm):
    class Meta:
        model = ExtraCost
        fields = 'type', 'price', 'start', 'end'
        widgets = {
            'start': DateWidget,
            'end': DateWidget,
        }


ExtraCostFormSet = forms.models.modelformset_factory(
    ExtraCost,
    form=ExtraCostForm,
    can_delete=True,
)
