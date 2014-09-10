# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
import pkg_resources
import textwrap
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings

from ralph.util import plugin


logger = logging.getLogger(__name__)

PLUGINS_LOADED = False


class PluginError(Exception):
    pass


class Command(BaseCommand):
    """Retrieve data for pricing for today"""

    help = textwrap.dedent(__doc__).strip()
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
        make_option(
            '-y',
            dest='yesterday',
            action='store_true',
            default=False,
            help="Generate report for yesterday",
        ),
        make_option(
            '--today',
            dest='today',
            default=None,
            help="Save the synchronised results under the specified date.",
        ),
        make_option(
            '--run-only',
            dest='run_only',
            default=None,
            help="Run only the selected plugin, ignore dependencies.",
        ),
    )

    def _run_plugin(self, name, today):
        logger.info('Running {0}...'.format(name))
        try:
            success, message = plugin.run(
                'scrooge',
                name,
                today=today,
            )
            if not success:
                raise PluginError(message)
            logger.info('{0}: Done'.format(message))
            return True
        except Exception as e:
            logger.exception("{0}: {1}".format(name, e))

    def _load_plugins(self):
        """
        Loads all collect plugins using scrooge.collect_plugins entry point.
        """
        global PLUGINS_LOADED
        if PLUGINS_LOADED:
            return
        for p in pkg_resources.iter_entry_points('scrooge.collect_plugins'):
            p.load()
        PLUGINS_LOADED = True

    def handle(self, today, run_only, *args, **options):
        self._load_plugins()
        if today:
            today = datetime.datetime.strptime(today, '%Y-%m-%d').date()
        else:
            today = datetime.date.today()

        if options.get('yesterday'):
            today -= datetime.timedelta(days=1)

        logger.info('Synchronizing for {0}.'.format(today.isoformat()))
        if not run_only:
            done = set()
            tried = set()
            while True:
                to_run = plugin.next('scrooge', done) - tried
                if not to_run:
                    break
                name = plugin.highest_priority('scrooge', to_run)
                tried.add(name)
                if (name in settings.COLLECT_PLUGINS and
                        self._run_plugin(name, today)):
                    done.add(name)
        else:
            self._run_plugin(run_only, today)
