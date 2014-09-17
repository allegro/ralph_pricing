# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph_scrooge.app import Scrooge
from ralph_scrooge.views.base import Base
from ralph_scrooge.sidebar_menus import service_environments


class Allocation(Base):
    template_name = 'ralph_scrooge/allocation.html'
    submodule_name = 'allocation'

    def get_context_data(self, **kwargs):
        context = super(Allocation, self).get_context_data(**kwargs)
        context.update({
        	'sidebar_items': service_environments(
                '/{0}/allocation'.format(Scrooge.url_prefix),
            ),
        })
        return context
