# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import urllib

from django.conf import settings
from django.core.cache import get_cache, InvalidCacheBackendError

from ralph_pricing.views.base import Base
from bob.csvutil import make_csv_response


def currency(value):
    return '{:,.2f} {}'.format(value or 0, settings.CURRENCY).replace(',', ' ')


class Report(Base):
    template_name = None
    Form = None
    section = ''

    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        self.data = []
        self.header = []
        self.form = None

    def get(self, *args, **kwargs):
        get = self.request.GET
        if get:
            self.form = self.Form(get)
        else:
            self.form = self.Form()
        if self.form.is_valid():
            self.header, self.data = self.get_cached(**self.form.cleaned_data)
            if get.get('format', '').lower() == 'csv':
                return make_csv_response(
                    itertools.chain([self.header], self.data),
                    '{}.csv'.format(self.section),
                )
        return super(Report, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Report, self).get_context_data(**kwargs)
        context.update({
            'data': self.data,
            'header': self.header,
            'section': self.section,
            'form': self.form,
        })
        return context

    def get_cache_key(self, **kwargs):
        return b'{}?{}'.format(self.section, urllib.urlencode(kwargs))

    def get_cached(self, **kwargs):
        try:
            cache = get_cache('pricing_reports')
        except InvalidCacheBackendError:
            cache = get_cache('default')
        key = self.get_cache_key(**kwargs)
        cached = cache.get(key)
        if cached is not None:
            jobid, header, data = cached
            # XXX if jobid is not None, we are still processing...
        else:
            cache.set(key, (1, None, None))  # Avoid dogpiling
            header = self.get_header(**kwargs)
            data = self.get_data(**kwargs)
            cache.set(key, (None, header, data))
        return header, data

    def get_data(self, **kwargs):
        return []

    def get_header(self, **kwargs):
        return []

