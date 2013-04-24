# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph_pricing.views.base import Base
from ralph_pricing.menus import ventures_menu


class Home(Base):
    template_name = 'ralph_pricing/home.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context.update({
            'sidebar_items': ventures_menu(),
        })
        return context

