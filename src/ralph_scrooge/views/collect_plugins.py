# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict
from dateutil import rrule

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.forms import CollectPluginsForm
from ralph_scrooge.management.commands.scrooge_sync import run_plugins
from ralph_scrooge.utils.common import get_cache_name, get_queue_name
from ralph_scrooge.utils.worker_job import WorkerJob
from ralph_scrooge.views.base import Base


logger = logging.getLogger(__name__)


class CollectPlugins(WorkerJob, Base):
    """
    Report with listing of devices ventures changes. Contains basic information
    about change such as device info (sn, barcode, name), change date and
    ventures (before and after change).
    """
    template_name = 'ralph_scrooge/collect_plugins.html'
    Form = CollectPluginsForm
    submodule_name = 'collect-plugins'
    title = _('Collect plugins runner')
    description = _('Run collect plugins in period of time.')
    initial = None

    queue_name = get_queue_name('scrooge_collect')
    cache_name = get_cache_name('scrooge_collect')
    cache_section = 'scrooge_collect'
    cache_timeout = 60 * 60  # 1 hour (max time for plugin to run)
    cache_final_result_timeout = 60  # 1 minute for final result

    def __init__(self, *args, **kwargs):
        super(CollectPlugins, self).__init__(*args, **kwargs)
        self.form = None
        self.progress = 0
        self.got_query = False
        self.plugins = []
        self.data = {}

    def get(self, *args, **kwargs):
        get = self.request.GET
        if get:
            self.form = self.Form(get)
            self.got_query = True
        else:
            self.form = self.Form(initial=self.initial)
        if self.form.is_valid():
            if 'clear' in get:
                self.progress = 0
                self.got_query = False
                self._clear_cache(**self.form.cleaned_data)
                messages.success(
                    self.request, "Cache cleared for this report.",
                )
            else:
                self.plugins = sorted(self.form.cleaned_data['plugins'])
                self.progress, self.data = self.run_on_worker(
                    **self.form.cleaned_data
                )
                self.data = self.data or {}
                if self.progress < 100:
                    messages.warning(self.request, _(
                        "Please wait for plugins to finish collecting data."
                    ))
        else:
            self.got_query = False
        return super(CollectPlugins, self).get(*args, **kwargs)

    def _parse_data(self):
        result = []
        for day, plugins in sorted(self.data.items(), key=lambda k: k[0]):
            tmp = [day.date()]
            for plugin in self.plugins:
                tmp.append(plugins.get(plugin, None))
            result.append(tmp)
        return result

    def get_context_data(self, **kwargs):
        context = super(CollectPlugins, self).get_context_data(**kwargs)
        context.update({
            'progress': self.progress,
            'header': [''] + sorted(self.plugins),
            'data': self._parse_data(),
            'title': self.title,
            'description': self.description,
            'form': self.form,
            'got_query': self.got_query,
        })
        return context

    @classmethod
    def run(cls, plugins, start, end):
        days = (end - start).days + 1
        progress = 0
        step = 100.0 / (len(plugins) * days)
        result = defaultdict(dict)
        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            for plugin, success in run_plugins(day, plugins, run_only=True):
                progress += step
                result[day][plugin] = success
                yield progress, result
        if progress < 100:
            yield 100, result
