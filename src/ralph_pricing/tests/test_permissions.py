# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import inspect

from django.test import TestCase
from django.views.generic import View

from ralph_pricing import urls
from ralph_pricing.views.base import Base


class TestPermissions(TestCase):
    def setUp(self):
        pass

    def test_urls(self):
        """
        Checks if every view from urls is subclass of Base view
        """
        for i in urls.__dict__.values():
            if inspect.isclass(i) and issubclass(i, View):
                self.assertTrue(issubclass(i, Base))
