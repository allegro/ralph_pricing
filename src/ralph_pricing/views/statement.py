# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import json

from bob.csvutil import make_csv_response
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from ralph_pricing.app import Scrooge
from ralph_pricing.forms import ExtraCostFormSet
from ralph_pricing.menus import ventures_menu, statement_menu
from ralph_pricing.models import Venture, Statement
from ralph_pricing.views.base import Base
from ralph_pricing.forms import DateRangeForm


class Statements(Base):
    template_name = 'ralph_pricing/statement.html'
    Form = DateRangeForm
    section = 'all-ventures-statement'

    def __init__(self, *args, **kwargs):
        super(Statements, self).__init__(*args, **kwargs)
        self.statement_id = None
        self.statement = None
        self.header = None
        self.data = None

    def init_args(self):
        self.statement_id = self.kwargs.get('statement_id')
        if self.statement_id is not None:
            try:
                self.statement = Statement.objects.get(id=self.statement_id)
            except Statement.DoesNotExist:
                messages.error(
                    self.request, "Statement does not exist!",
                )

    def get(self, *args, **kwargs):
        self.init_args()
        if self.statement:
            self.header = json.loads(self.statement.header)
            self.data = json.loads(self.statement.data)

        if self.request.GET.get('format', '').lower() == 'csv':
            return make_csv_response(
                itertools.chain(self.header, self.data),
                '{}.csv'.format(self.section),
            )
        return super(Statements, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Statements, self).get_context_data(**kwargs)
        context.update({
            'data': self.data,
            'header': self.header,
            'section': 'statement',
            'sidebar_items': statement_menu(
                '/{0}/statement'.format(Scrooge.url_prefix),
                self.statement_id
            ),
            'sidebar_selected': self.statement_id,
            'form': DateRangeForm()
        })
        return context
