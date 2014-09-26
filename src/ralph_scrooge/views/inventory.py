# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph_scrooge.app import Scrooge
from ralph_scrooge.views.base import Base
from ralph_scrooge.sidebar_menus import service_environments
from ralph_scrooge.models import Service, Environment


class Inventory(Base):
    template_name = 'ralph_scrooge/inventory.html'
    submodule_name = 'inventory'

    def __init__(self, *args, **kwargs):
        super(Inventory, self).__init__(*args, **kwargs)
        self.service = None
        self.environment = None

    def _init_args(self):
        if self.kwargs.get('service_id'):
            self.service = Service.objects.filter(
                id=self.kwargs.get('service_id')
            )[0]
        if self.kwargs.get('environment_id'):
            self.environment = Environment.objects.filter(
                id=self.kwargs.get('environment_id')
            )[0]

    def get(self, *args, **kwargs):
        self._init_args()
        return super(Inventory, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Inventory, self).get_context_data(**kwargs)
        sidebar_selected = self.service
        if self.environment:
            sidebar_selected = "{0}_{1}".format(
                self.service,
                self.environment
            )
        context.update({
        	'sidebar_items': service_environments(
                '/{0}/inventory'.format(Scrooge.url_prefix),
                service=self.service,
                environment=self.environment,
            ),
            'sidebar_selected': sidebar_selected,
        })
        return context
