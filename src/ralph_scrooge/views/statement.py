# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import json

from bob.csvutil import make_csv_response
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.app import Scrooge
from ralph_scrooge.sidebar_menus import statement_menu
from ralph_scrooge.models import Statement
from ralph_scrooge.views.base import Base
from ralph_scrooge.views.base_report import format_csv_header


class Statements(Base):
    """
    Statement view with generate to csv option.
    """
    template_name = 'ralph_scrooge/statement.html'
    submodule_name = 'statement'

    def __init__(self, *args, **kwargs):
        super(Statements, self).__init__(*args, **kwargs)
        self.statement_id = None
        self.statement = None
        self.header = None
        self.data = None

    def init_args(self):
        """
        Init statement class field when given statement_id and statement with
        given id exist.
        """
        self.statement_id = self.kwargs.get('statement_id')
        if self.statement_id is not None:
            try:
                self.statement = Statement.objects.get(id=self.statement_id)
            except Statement.DoesNotExist:
                messages.error(
                    self.request, _("Statement does not exist!"),
                )

    def get(self, *args, **kwargs):
        """
        If statement exist then set header and data of current statement.
        Generate csv from current statement.
        """
        self.init_args()
        if self.statement:
            self.header = json.loads(self.statement.header)
            self.data = json.loads(self.statement.data)

        if self.request.GET.get('format', '').lower() == 'csv':
            self.header = format_csv_header(self.header)
            return make_csv_response(
                itertools.chain(self.header, self.data),
                '{}.csv'.format(self.section),
            )
        return super(Statements, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Generate submenu for statements with active row.
        """
        context = super(Statements, self).get_context_data(**kwargs)
        context.update({
            'data': self.data,
            'header': self.header,
            'section': 'statement',
            'sidebar_items': statement_menu(
                '/{0}/statement'.format(Scrooge.url_prefix),
                self.statement_id
            ),
            'sidebar_selected': str(self.statement),
        })
        return context
