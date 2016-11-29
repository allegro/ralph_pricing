# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.shortcuts import render_to_response
from django.views.generic import View


class BootstrapSwagger(View):

    def get(self, request):
        return render_to_response('swagger_ui_index.html')
