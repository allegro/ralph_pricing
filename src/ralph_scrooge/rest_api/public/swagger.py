# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.views.generic import TemplateView


class BootstrapSwagger(TemplateView):
    template_name = 'swagger_ui_index.html'
