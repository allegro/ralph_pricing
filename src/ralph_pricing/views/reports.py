# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools

from django.conf import settings

from ralph_pricing.views.base import Base
from bob.csvutil import make_csv_response


def currency(value):
    return '{:,.2f} {}'.format(value or 0, settings.CURRENCY).replace(',', ' ')


class Report(Base):
    template_name = None
    Form = None
    section = None

    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        self.data = []
        self.header = []
        self.form = None

    def get(self, *args, **kwargs):
        get = self.request.GET
        if get:
            self.form = self.Form(get)
        else:
            self.form = self.Form()
        if self.form.is_valid():
            self.data = self.get_data(**self.form.cleaned_data)
            self.header = self.get_header(**self.form.cleaned_data)
            if get.get('format') == 'csv':
                return make_csv_response(
                    itertools.chain([self.header], self.data),
                    '{}.csv'.format(self.section),
                )
        return super(Report, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Report, self).get_context_data(**kwargs)
        context.update({
            'data': self.data,
            'header': self.header,
            'section': self.section,
            'form': self.form,
        })
        return context

    def get_data(self, **kwargs):
        return []

    def get_header(self, **kwargs):
        return []

