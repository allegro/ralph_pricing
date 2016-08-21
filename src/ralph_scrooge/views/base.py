# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.views.generic import TemplateView

from ralph_scrooge.menu import scrooge_menu

from ralph_scrooge.app import Scrooge as app


class Base(TemplateView):

    submodule_name = ''
    module_name = app.module_name

    def dispatch(self, *args, **kwargs):
        return super(Base, self).dispatch(*args, **kwargs)

    def get_title(self):
        for item in scrooge_menu:
            if item.kwargs.get('view_name') == self.submodule_name:
                return item.label
        return ''

    def get_context_data(self, **kwargs):
        context = super(Base, self).get_context_data(**kwargs)
        context.update({
            'menu': scrooge_menu,
            'active_menu': self.submodule_name,
            'title': self.get_title()
        })
        return context
