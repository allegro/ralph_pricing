# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from rest_framework import routers

from ralph_scrooge.rest_api.private.usagetypes import UsageTypesViewSet


router = routers.SimpleRouter()

router.register(r'usage-types', UsageTypesViewSet)
urlpatterns = router.urls
