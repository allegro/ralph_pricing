# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from ralph_pricing.views import (
    Home,
)


urlpatterns = patterns(
    '',
    url(r'^$',
        login_required(Home.as_view()),
        name='home'),
)

