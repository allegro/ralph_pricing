# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.views.generic import TemplateView

from ralph_scrooge.app import Scrooge as app


class BootstrapAngular(TemplateView):
    """
    Initial view for bootstrap angularjs
    """
    template_name = 'ralph_scrooge/index.html'
    module_name = app.module_name


class BootstrapAngular2(TemplateView):
    """
    Initial view for bootstrap angularjs
    """
    template_name = 'ralph_scrooge/angular2.html'
    module_name = app.module_name
