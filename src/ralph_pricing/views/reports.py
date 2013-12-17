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
from django.contrib import messages
from django.core.cache.backends.dummy import DummyCache


CACHE_NAME = 'reports_pricing'
if CACHE_NAME not in settings.CACHES:
    CACHE_NAME = 'default'
QUEUE_NAME = 'reports_pricing'
if QUEUE_NAME not in settings.RQ_QUEUES:
    QUEUE_NAME = None
TIMEOUT = getattr(settings, 'PRICING_REPORTS_TIMEOUT', 4 * 3600)  # 4 hours


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
    report_name = ''

    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        self.data = []
        self.header = []
        self.form = None
        self.progress = 0
        self.got_query = False

    def get(self, *args, **kwargs):
        get = self.request.GET
        if get:
            self.form = self.Form(get)
            self.got_query = True
        else:
            self.form = self.Form()
        if self.form.is_valid():
            if 'clear' in get:
                self.progress = 0
                self.got_query = False
                self._clear_cache(**self.form.cleaned_data)
                messages.success(
                    self.request, "Cache cleared for this report.",
                )
            else:
                self.progress, self.header, self.data = self._get_cached(
                    **self.form.cleaned_data
                )
                if get.get('format', '').lower() == 'csv':
                    if self.progress == 100:
                        return make_csv_response(
                            itertools.chain([self.header], self.data),
                            '{}.csv'.format(self.section),
                        )
                    else:
                        messages.warning(
                            self.request,
                            "Please wait for the report "
                            "to finish calculating.",
                        )
        return super(Report, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Report, self).get_context_data(**kwargs)
        context.update({
            'progress': self.progress,
            'data': self.data,
            'header': self.header,
            'section': self.section,
            'report_name': self.report_name,
            'form': self.form,
            'got_query': self.got_query,
        })
        return context

    def _clear_cache(self, **kwargs):
        cache = get_cache(CACHE_NAME)
        key = _get_cache_key(self.section, **kwargs)
        cache.set(key, None)

    def _get_cached(self, **kwargs):
        cache = get_cache(CACHE_NAME)
        if isinstance(cache, DummyCache):
            # No caching or queues with dummy cache.
            header, data = self._get_header_and_data(**kwargs)
            return 100, header, data
        key = _get_cache_key(self.section, **kwargs)
        cached = cache.get(key)
        if cached is not None:
            progress, job_id, header, data = cached
            if progress < 100 and job_id is not None and QUEUE_NAME:
                connection = django_rq.get_connection(QUEUE_NAME)
                job = Job.fetch(job_id, connection)
                if job.is_finished:
                    header, data = job.result
                    progress = 100
                    cache.set(key, (progress, job_id, header, data))
                elif job.is_failed:
                    header, data = None, None
                    progress = 100
                    cache.delete(key)
        else:
            if QUEUE_NAME:
                queue = django_rq.get_queue(QUEUE_NAME)
                job = queue.enqueue_call(
                    func=self._get_header_and_data,
                    kwargs=kwargs,
                    timeout=TIMEOUT,
                )
                progress = 0
                header = None
                data = None
                cache.set(key, (progress, job.id, header, data))
            else:
                progress = 0
                cache.set(key, (progress, None, None, None))
                header, data = self._get_header_and_data(**kwargs)
                progress = 100
                cache.set(key, (progress, None, header, data))
        return progress, header or [], data or []

    @classmethod
    def _get_header_and_data(cls, **kwargs):
        cache = get_cache(CACHE_NAME)
        key = _get_cache_key(cls.section, **kwargs)
        cached = cache.get(key)
        if cached is not None:
            job_id = cached[1]
        else:
            job_id = None
        header = cls.get_header(**kwargs)
        last_progress = 0
        data = []
        for progress, data in cls.get_data(**kwargs):
            if job_id is not None and progress - last_progress > 5:
                # Update progress in 5% increments
                cache.set(key, (progress, job_id, header, data))
                last_progress = progress
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
