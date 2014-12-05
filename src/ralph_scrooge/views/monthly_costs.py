# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from dateutil import rrule

from django.contrib import messages
from django.core.cache import get_cache
from django.utils.translation import ugettext_lazy as _

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
    cache_timeout = 60 * 60 * 24  # 1 hour (max time for plugin to run)
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
                self.run_jobs(**self.form.cleaned_data)
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
                    self.request, "Cache cleared.",
                )
        return super(MonthlyCosts, self).get(*args, **kwargs)

    def run_jobs(self, start, end, **kwargs):
        """
        Run calculating as separated jobs - each for one day in period.
        """
        days = (end - start).days + 1
        self.progress = 0
        self.data = {}
        step = 100.0 / days
        all_done = True
        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            progress, result = self.run_on_worker(day=day, **kwargs)
            if progress == 100 and result:
                self.progress += step
                self.data.update(result)
            else:
                all_done = False
        # clear cache if all done
        if all_done:
            self.forget_cache(start, end, **kwargs)

    def forget_cache(self, start, end, **kwargs):
        """
        Set cache timeout to `cache_all_done_timeout` when all jobs are
        finished.
        """
        cache = get_cache(self.cache_name)
        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            key = _get_cache_key(self.cache_section, day=day, **kwargs)
            cached = cache.get(key)
            cache.set(key, cached, timeout=self.cache_all_done_timeout)

    def clear_cache(self, start, end, **kwargs):
        """
        Clear cache for period of time as clearing for one day at once.
        """
        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            self._clear_cache(day=day, **kwargs)

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
    def run(cls, day, forecast):
        """
        Run collecting costs for one day.
        """
        collector = Collector()
        try:
            collector.process(day, forecast)
            success = True
        except Exception as e:
            logger.exception(e)
            success = False
        yield 100, {day: success}
