# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph_scrooge.app import Scrooge
from ralph_scrooge.views.base import Base
from ralph_scrooge.sidebar_menus import service_environments


class DependencyTree(Base):
    template_name = 'ralph_scrooge/dependency_tree.html'
    submodule_name = 'dependency_tree'

    def get_context_data(self, **kwargs):
        context = super(DependencyTree, self).get_context_data(**kwargs)
        context.update({
        	'sidebar_items': service_environments(
                '/{0}/dependency_tree'.format(Scrooge.url_prefix),
            ),
        })
        return context
