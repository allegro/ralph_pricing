# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import urllib

from django.conf import settings
from django.core.cache import get_cache

from ralph_pricing.views.base import Base
from bob.csvutil import make_csv_response
import django_rq
from rq.job import Job


CACHE_NAME = 'reports'
if CACHE_NAME not in settings.CACHES:
    CACHE_NAME = 'default'
QUEUE_NAME = 'reports'
if QUEUE_NAME not in settings.RQ_QUEUES:
    QUEUE_NAME = None


def currency(value):
    """Formats currency as string according to the settings."""

    return '{:,.2f} {}'.format(value or 0, settings.CURRENCY).replace(',', ' ')


def _get_cache_key(section, **kwargs):
    return b'{}?{}'.format(section, urllib.urlencode(kwargs))


class Report(Base):
    """
    A base class for the reports. Override ``template_name``, ``Form``,
    ``section``, ``get_header`` and ``get_data`` in the specific reports.

    Make sure that ``get_header`` and ``get_data`` are static methods.
    """
    template_name = None
    Form = None
    section = ''

    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        self.data = []
        self.header = []
        self.form = None
        self.processing = False
        self.got_query = False

    def get(self, *args, **kwargs):
        get = self.request.GET
        if get:
            self.form = self.Form(get)
            self.got_query = True
        else:
            self.form = self.Form()
        if self.form.is_valid():
            self.processing, self.header, self.data = self._get_cached(
                **self.form.cleaned_data
            )
            if get.get('format', '').lower() == 'csv':
                return make_csv_response(
                    itertools.chain([self.header], self.data),
                    '{}.csv'.format(self.section),
                )
        return super(Report, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Report, self).get_context_data(**kwargs)
        context.update({
            'processing': self.processing,
            'data': self.data,
            'header': self.header,
            'section': self.section,
            'form': self.form,
            'got_query': self.got_query,
        })
        return context


    def _get_cached(self, **kwargs):
        cache = get_cache(CACHE_NAME)
        key = _get_cache_key(self.section, **kwargs)
        cached = cache.get(key)
        if cached is not None:
            processing, job_id, header, data = cached
            if processing and job_id is not None and QUEUE_NAME:
                connection = django_rq.get_connection(QUEUE_NAME)
                job = Job.fetch(job_id, connection)
                if job.is_finished:
                    header, data = job.result
                    processing = False
                    cache.set(key, (processing, job_id, header, data))
                elif job.is_failed:
                    header, data = None, None
                    processing = False
                    cache.delete(key)
        else:
            if QUEUE_NAME:
                queue = django_rq.get_queue(QUEUE_NAME)
                job = queue.enqueue(self._get_header_and_data, **kwargs)
                processing = True
                header = None
                data = None
                cache.set(key, (processing, job.id, None, None))
            else:
                processing = True
                cache.set(key, (processing, None, None, None))
                header, data = self._get_header_and_data(**kwargs)
                processing = False
                cache.set(key, (processing, None, header, data))
        return processing, header or [], data or []

    @classmethod
    def _get_header_and_data(cls, **kwargs):
        header, data =  cls.get_header(**kwargs), cls.get_data(**kwargs)
        cache = get_cache(CACHE_NAME)
        key = _get_cache_key(cls.section, **kwargs)
        # If the workers share the cache with the WWW instance, we save it now.
        cache.set(key, (False, None, header, data))
        return header, data

    @staticmethod
    def get_data(**kwargs):
        """
        Override this static method to provide data for the report.
        It gets called with the form's data as arguments.
        Make sure it's a static method.
        """
        return []

    @staticmethod
    def get_header(**kwargs):
        """
        Override this static method to provide header for the report.
        It gets called with the form's data as arguments.
        Make sure it's a static method.
        """
        return []

