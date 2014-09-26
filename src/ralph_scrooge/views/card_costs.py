# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph_scrooge.app import Scrooge
from ralph_scrooge.views.base import Base
from ralph_scrooge.sidebar_menus import service_environments


class CardCosts(Base):
    template_name = 'ralph_scrooge/card_costs.html'
    submodule_name = 'card_costs'

    def get_context_data(self, **kwargs):
        context = super(CardCosts, self).get_context_data(**kwargs)
        context.update({
        	'sidebar_items': service_environments(
                '/{0}/card_costs'.format(Scrooge.url_prefix),
            ),
        })
        return context
