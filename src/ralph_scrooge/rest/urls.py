#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from ralph_scrooge.rest import (
    AllocationAdminContent,
    AllocationClientContent,
    AllocationClientPerTeam,
    CostCardContent,
    allocation_save,
    allocation_content,
)

from ralph_scrooge.rest.menu import SubMenu


urlpatterns = patterns(
    '',
    url(
        r'^allocateadmin/(?P<year>\d+)/(?P<month>\d+)/$',
        AllocationAdminContent.as_view(),
    ),
    url(
        r'^allocateclient/(?P<service>\d+)/(?P<env>\d+)/(?P<year>\d+)/(?P<month>\d+)/$',  # noqa
        AllocationClientContent.as_view(),
    ),
    url(
        r'^allocateclient/(?P<team>\d+)/(?P<year>\d+)/(?P<month>\d+)/$',
        AllocationClientPerTeam.as_view(),
    ),
    url(
        r'^allocateclient/(?P<service>\d+|false)/(?P<env>\d+|false)/(?P<team>\d+|false)/(?P<year>\d+)/(?P<month>\d+)/$',  # noqa
        allocation_content,
    ),
    url(
        r'^allocateclient/(?P<allocate_type>\S+)/save/$',
        login_required(allocation_save),
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
