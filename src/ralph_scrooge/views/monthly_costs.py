# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import time
from dateutil import rrule

from django.conf import settings
from django.contrib import messages
from django.core.cache import get_cache
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rq import get_current_job

from ralph_scrooge.plugins.cost.collector import Collector
from ralph_scrooge.views.base import Base
from ralph_scrooge.utils.common import get_cache_name, get_queue_name
from ralph_scrooge.utils.worker_job import WorkerJob, _get_cache_key
from ralph_scrooge.forms import MonthlyCostsForm
from ralph_scrooge.models import CostDateStatus


logger = logging.getLogger(__name__)


class MonthlyCosts(WorkerJob, Base):
    template_name = 'ralph_scrooge/monthly_costs.html'
    Form = MonthlyCostsForm
    submodule_name = 'monthly-costs'
    title = _('Recalculate and accept costs')
    description = _(
        'Recalculate and accept costs for selected period of time.'
    )
    initial = None

    queue_name = get_queue_name('scrooge_costs')
    cache_name = get_cache_name('scrooge_costs')
    cache_section = 'scrooge_costs'
    cache_timeout = 60 * 60 * 24  # 24 hours (max time for plugin to run)
    cache_final_result_timeout = 60 * 60 * 2  # 2 hours
    cache_all_done_timeout = 60  # 1 minute
    refresh_time = 30

    def __init__(self, *args, **kwargs):
        super(MonthlyCosts, self).__init__(*args, **kwargs)
        self.form = None
        self.progress = 0
        self.got_query = False
        self.data = {}

    def get(self, *args, **kwargs):
        if self.request.GET:
            self.form = self.Form(self.request.GET)
        else:
            self.form = self.Form(initial=self.initial)
        if self.form.is_valid():
            if 'recalculate' in self.request.GET:
                self.got_query = True
                self.progress, self.data = self.run_on_worker(
                    **self.form.cleaned_data
                )
                self.data = self.data or {}
                if self.progress < 100:
                    messages.warning(self.request, _(
                        "Please wait for costs recalculation."
                    ))
                else:
                    messages.success(self.request, _('Costs recalculated.'))
            elif 'accept' in self.request.GET:
                self.accept_costs(**self.form.cleaned_data)
            elif 'clear' in self.request.GET:
                self.progress = 0
                self.clear_cache(**self.form.cleaned_data)
                messages.success(
                    self.request, _("Cache cleared."),
                )
        return super(MonthlyCosts, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MonthlyCosts, self).get_context_data(**kwargs)
        context.update({
            'progress': self.progress,
            'header': [_('Date'), _('Success')],
            'data': sorted(self.data.items(), key=lambda k: k[0]),
            'title': self.title,
            'description': self.description,
            'form': self.form,
            'got_query': self.got_query,
            'refresh_time': self.refresh_time,
        })
        return context

    def accept_costs(self, start, end, forecast):
        calculated_costs = CostDateStatus.objects.filter(
            date__gte=start,
            date__lte=end,
            **{'forecast_calculated' if forecast else 'calculated': True}
        )
        days = (end - start).days + 1
        if len(calculated_costs) != days:
            messages.error(self.request, _(
                "Costs were not calculated for all selected days!"
            ))
        else:
            calculated_costs.update(**{
                'forecast_accepted' if forecast else 'accepted': True,
            })
            messages.success(self.request, _(
                "Costs were accepted!"
            ))

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
        cache = get_cache(cls.cache_name)
        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            key = _get_cache_key(cls.cache_section, day=day, **kwargs)
            cached = cache.get(key)
            cache.set(key, cached, timeout=cls.cache_all_done_timeout)

    def clear_cache(self, start, end, **kwargs):
        """
        Clear cache for period of time as clearing for one day at once.

        :param start: start date
        :type start: datetime.date
        :param end: end date
        :type end: datetime.date
        """
        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            self._clear_cache(day=day, **kwargs)
        self._clear_cache(start=start, end=end, **kwargs)

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
                continue
            dcj = DailyCostsJob()
            progress, success, result = dcj.run_on_worker(day=day, **kwargs)
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

    @classmethod
    @transaction.commit_on_success
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
