# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.views.generic import TemplateView
from ralph.ui.views.common import MenuMixin

from ralph_scrooge.app import Scrooge as app


class BootstrapAngular(MenuMixin, TemplateView):
    """
    Initial view for bootstrap angularjs
    """
    template_name = 'ralph_scrooge/index.html'
    submodule_name = 'scrooge'  # to satisfy MenuMixin, not used in angular
    module_name = app.module_name
