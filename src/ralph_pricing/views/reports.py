# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings

from ralph_pricing.views.base import Base


def currency(value):
    return '{:,.2f} {}'.format(value or 0, settings.CURRENCY).replace(',', ' ')


class Report(Base):
    template_name = None
    Form = None
    section = None

    def get_context_data(self, **kwargs):
        context = super(Report, self).get_context_data(**kwargs)
        if self.request.GET:
            form = self.Form(self.request.GET)
        else:
            form = self.Form()
        if form.is_valid():
            context.update(data=self.get_data(**form.cleaned_data))
            context.update(header=self.get_header(**form.cleaned_data))
        context.update({
            'section': self.section,
            'form': form,
        })
        return context

    def get_data(self, **kwargs):
        return []

    def get_header(self, **kwargs):
        return []

