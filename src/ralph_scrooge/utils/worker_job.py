# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import urllib

import django_rq
from django.core.cache import get_cache
from django.core.cache.backends.dummy import DummyCache
from rq.job import Job


logger = logging.getLogger(__name__)


def _get_cache_key(cache_section, **kwargs):
    return b'{}?{}'.format(cache_section, urllib.urlencode(kwargs))


class WorkerJob(object):
    """
    Mixin to jobs that are running on RQ worker.
    """
    cache_section = 'default'
    queue_name = 'default'
    cache_name = 'default'
    work_timeout = 4 * 60 * 60  # 4 hours
    cache_timeout = 60 * 60  # 1 hour for result of work in progress
    cache_final_result_timeout = 60 * 10  # 10 minutes for final result
    progress_update = 5  # update cache every 5% of progress
    _return_job_meta = False  # if True return job metadata in _worker_func too

    @classmethod
    def _clear_cache(cls, **kwargs):
        cache = get_cache(cls.cache_name)
        key = _get_cache_key(cls.cache_section, **kwargs)
        cache.set(key, None)

    def run_on_worker(self, **kwargs):
        cache = get_cache(self.cache_name)
        if isinstance(cache, DummyCache):
            # No caching or queues with dummy cache.
            data = self._worker_func(**kwargs)
            return (100, data, {}) if self._return_job_meta else (100, data)
        key = _get_cache_key(self.cache_section, **kwargs)
        cached = cache.get(key)
        if cached is not None:
            progress, job_id, data = cached
            connection = django_rq.get_connection(self.queue_name)
            job = Job.fetch(job_id, connection)
            if progress < 100 and job_id is not None:
                if job.is_finished:
                    data = job.result
                    progress = 100
                    cache.set(
                        key,
                        (progress, job_id, data),
                        timeout=self.cache_final_result_timeout,
                    )
                elif job.is_failed:
                    data = None
                    progress = 100
                    cache.delete(key)
        else:
            queue = django_rq.get_queue(self.queue_name)
            job = queue.enqueue_call(
                func=self._worker_func,
                kwargs=kwargs,
                timeout=self.work_timeout,
                result_ttl=self.cache_final_result_timeout,
            )
            progress = 0
            data = None
            cache.set(
                key,
                (progress, job.id, data),
                timeout=self.cache_timeout,
            )
        if self._return_job_meta:
            return progress, data, job.meta
        return progress, data

    @classmethod
    def _worker_func(cls, **kwargs):
        """
        Main method executed on worker, which run user defined worker function,
        check for progress and store results in cache.
        """
        cache = get_cache(cls.cache_name)
        key = _get_cache_key(cls.cache_section, **kwargs)
        cached = cache.get(key)
        if cached is not None:
            job_id = cached[1]
        else:
            job_id = None

        last_progress = 0
        data = None
        for progress, data in cls.run(**kwargs):
            if (
                job_id is not None and
                progress - last_progress > cls.progress_update
            ):
                # Update cache when progress incremented by cls.progress_update
                # or every time when cls.progress_update is None
                cache.set(
                    key,
                    (progress, job_id, data),
                    timeout=cls.cache_timeout,
                )
                last_progress = progress
        cache.set(
            key,
            (progress, job_id, data),
            timeout=cls.cache_final_result_timeout,
        )
        return data

    @classmethod
    def run(cls, *args, **kwargs):
        raise NotImplementedError()
