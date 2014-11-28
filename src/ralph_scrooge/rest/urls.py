#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from ralph_scrooge.rest import (
    AllocationAdminContent,
    CostCardContent,
)

from ralph_scrooge.rest.menu import SubMenu


urlpatterns = patterns(
    '',
    url(
        r'^allocateadmin/(?P<year>\d+)/(?P<month>\d+)/$',  # noqa
        AllocationAdminContent.as_view(),
    ),
    url(
        r'^costcard/(?P<service>\d+)/(?P<env>\d+)/(?P<year>\d+)/(?P<month>\d+)/$',  # noqa
        CostCardContent.as_view(),
    ),
    url(
        r'^submenu/$',
        SubMenu.as_view(),
        name='submenu'
    ),
)
