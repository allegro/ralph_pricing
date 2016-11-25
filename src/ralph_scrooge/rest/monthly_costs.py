# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import time
from dateutil import rrule

from django.conf import settings
from django.core.cache import caches as dj_caches
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rq import get_current_job

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ralph_scrooge.plugins.cost.collector import Collector
from ralph_scrooge.utils.common import get_cache_name, get_queue_name
from ralph_scrooge.utils.worker_job import WorkerJob, _get_cache_key
from ralph_scrooge.models import CostDateStatus
from ralph_scrooge.rest.serializers import MonthlyCostsSerializer


logger = logging.getLogger(__name__)


class AcceptMonthlyCosts(APIView):

    def post(self, request, *args, **kwargs):
        result = {'status': 'failed', 'message': ''}
        serializer = MonthlyCostsSerializer(data=request.data)
        if serializer.is_valid():
            start = serializer.validated_data['start']
            end = serializer.validated_data['end']
            forecast = serializer.validated_data['forecast']
            calculated_costs = CostDateStatus.objects.filter(
                date__gte=start,
                date__lte=end,
                forecast_calculated=forecast
            )
            days = (end - start).days + 1
            if len(calculated_costs) != days:
                result['message'] = _(
                    'Costs were not calculated for all selected days!'
                )
            else:
                calculated_costs.update(**{
                    'forecast_accepted' if forecast else 'accepted': True,
                })
                result['message'] = _('Costs were accepted!')
                result['status'] = 'ok'
        return Response(result)


class MonthlyCosts(APIView, WorkerJob):

    _return_job_meta = True
    queue_name = get_queue_name('scrooge_costs_master', 'scrooge_costs')
    cache_name = get_cache_name('scrooge_costs_master', 'scrooge_costs')
    cache_section = 'scrooge_costs'
    cache_timeout = 60 * 60 * 24  # 24 hours (max time for plugin to run)
    # cache for main (master) job result
    cache_final_result_timeout = 60  # 1 minute
    # cache for partial results for each day when every job is done (costs
    # for each day are recalculated)
    cache_all_done_timeout = 60  # 1 minute

    def __init__(self, *args, **kwargs):
        self.progress = 0
        self.got_query = False
        self.data = {}

    def post(self, request, *args, **kwargs):
        """Recalculate costs."""
        serializer = MonthlyCostsSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["start"] > serializer.data["end"]:
                return Response(
                    {'message': 'End date can not be less than start date.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            result = {}
            self.got_query = True
            logger.info('Starting recalculation from {} to {}'.format(
                serializer.validated_data['start'],
                serializer.validated_data['end'],
            ))
            self.progress, self.data, job, meta = self.run_on_worker(
                **serializer.validated_data
            )
            result['job_id'] = job.id
            result['message'] = _(
                'Please wait for costs recalculation.'
            )
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, job_id, *args, **kwargs):
        job = self.get_rq_job(job_id)
        progress, data, job, meta = self.run_on_worker(
            **job.kwargs
        )
        status = 'running'
        data = data or {}
        data = sorted(data.items(), key=lambda k: k[0]),
        data = [(str(i[0].date()), i[1]) for i in data[0]]
        if job.is_finished:
            status = 'finished'
        elif job.is_failed:
            status = 'failed'

        return Response({'status': status, 'data': data, 'progress': progress})

    @classmethod
    def forget_cache(cls, start, end, **kwargs):
        """
        Set cache timeout to `cache_all_done_timeout` when all jobs are
        finished.

        :param start: start date
        :type start: datetime.date
        :param end: end date
        :type end: datetime.date
        """
        cache = dj_caches[cls.cache_name]
        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            key = _get_cache_key(cls.cache_section, day=day, **kwargs)
            cached = cache.get(key)
            cache.set(key, cached, timeout=cls.cache_all_done_timeout)

    @classmethod
    @transaction.atomic
    def _save_costs(self, data, start, end, forecast):
        """
        Save costs between start and end.

        :param data: list of DailyCost instances
        :type data: list
        :param start: start date
        :type start: datetime.date
        :param end: end date
        :type end: datetime.date
        :param forecast: True, if forecast costs
        :type forecast: bool
        """
        collector = Collector()
        collector.save_period_costs(start, end, forecast, data)

    @classmethod
    def _process_daily_result(self, data, date, forecast):
        """
        Process results from subtask jobs (single day) - create daily costs
        instances.

        :param data: costs per service environments
        :type data: dict of lists (key: service environment id, value: list of
            costs of service environment)
        :param date: date for which process daily results
        :type date: datetime.date
        :param forecast: True, if forecast costs
        :type forecast: bool
        """
        collector = Collector()
        return collector._create_daily_costs(date, data, forecast)

    @classmethod
    def run(cls, start, end, forecast=False, **kwargs):
        """
        Run collecting costs between start and end.

        It's running as "master" worker, which delegate jobs for single date to
        subtask workers, collects results from them and process them and at the
        end it saves all costs to the database.
        """
        progress = 0
        statuses = {}
        processed_results = []  # list of DailyCost instances for whole period
        logger.info('Recalculating costs from {} to {}'.format(start, end))
        while progress < 100:
            progress, statuses, results = cls._check_subjobs(
                statuses,
                start=start,
                end=end,
                forecast=forecast,
                **kwargs
            )
            if results:
                for day, day_results in results.iteritems():
                    processed_results.extend(cls._process_daily_result(
                        day_results,
                        day,
                        forecast,
                    ))
            if progress < 100:
                yield progress, statuses
                time.sleep(settings.SCROOGE_COSTS_MASTER_SLEEP)
        # save all costs
        cls._save_costs(processed_results, start, end, forecast)
        yield 100, statuses

    @classmethod
    def _check_subjobs(cls, statuses, start, end, **kwargs):
        """
        Check subjobs (jobs for single day) statuses.

        :param statuses: shared dict with statuses (True/False) for each day
            between start and end.
        :type statuses: dict
        :param start: start date
        :type start: datetime.date
        :param end: end date
        :type end: datetime.date
        """
        days = (end - start).days + 1
        step = 100.0 / days
        total_progress = 0
        results = {}
        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            # if day is in statuses, it was already calculated - do not check
            # it again
            if day in statuses:
                total_progress += step
                continue
            dcj = DailyCostsJob()
            progress, success, job, result = dcj.run_on_worker(
                day=day, **kwargs
            )
            if progress == 100:
                total_progress += step
                statuses[day] = success
            if result:
                results[day] = result['collector_result']
        # clear cache if all done
        if len(statuses) == days:
            cls.forget_cache(start, end, **kwargs)
            total_progress = 100
        return total_progress, statuses, results


class DailyCostsJob(WorkerJob):
    """
    Job for single day (running as "subtask")
    """
    queue_name = get_queue_name('scrooge_costs')
    cache_name = get_cache_name('scrooge_costs')
    cache_section = 'scrooge_costs'
    cache_timeout = 60 * 60 * 2  # 2 hours (max time for all plugins to run)
    cache_final_result_timeout = 60 * 60 * 2  # 2 hours
    _return_job_meta = True

    @classmethod
    def run(cls, day, forecast):
        """
        Run collecting costs for one day.
        """
        collector = Collector()
        result = {}
        try:
            result = collector.process(day, forecast)
            success = True
        except Exception as e:
            logger.exception(e)
            success = False
        job = get_current_job()
        # save result to job meta to keep log clean
        job.meta['collector_result'] = result
        job.save()
        yield 100, success
