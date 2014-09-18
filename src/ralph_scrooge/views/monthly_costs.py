# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.plugins.cost.collector import Collector
from ralph_scrooge.views.base import Base
from ralph_scrooge.utils.common import get_cache_name, get_queue_name
from ralph_scrooge.utils.worker_job import WorkerJob
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
    cache_timeout = 60 * 60  # 1 hour (max time for plugin to run)
    cache_final_result_timeout = 60  # 1 minute for final result

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
    def run(cls, start, end, forecast):
        days = (end - start).days + 1
        progress = 0
        step = 100.0 / days
        result = {}
        collector = Collector()
        for day, success in collector.process_period(
            start,
            end,
            forecast,
            force_recalculation=True,
        ):
                progress += step
                result[day] = success
                yield progress, result
        if progress < 100:
            yield 100, result
