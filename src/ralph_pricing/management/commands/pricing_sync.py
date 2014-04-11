# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
import textwrap
from optparse import make_option

from django.core.management.base import BaseCommand

from ralph.util import plugin
from ralph_pricing.app import setup_scrooge_logger


logger = logging.getLogger(__name__)


class PluginError(Exception):
    pass


class Command(BaseCommand):
    """Retrieve data for pricing for today"""

    help = textwrap.dedent(__doc__).strip()
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
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
            success, message, context = plugin.run(
                'pricing',
                name,
                today=today,
            )
            if not success:
                raise PluginError(message)
            logger.info('{0}: Done'.format(message))
            return True
        except Exception as e:
            logger.exception("{0}: {1}".format(name, e))

    def handle(self, today, run_only, *args, **options):
        setup_scrooge_logger()
        from ralph_pricing.plugins import collects  # noqa
        if today:
            today = datetime.datetime.strptime(today, '%Y-%m-%d').date()
        else:
            today = datetime.date.today()
        logger.info('Synchronizing for {0}.'.format(today.isoformat()))
        if not run_only:
            done = set()
            tried = set()
            while True:
                to_run = plugin.next('pricing', done) - tried
                if not to_run:
                    break
                name = plugin.highest_priority('pricing', to_run)
                tried.add(name)
                if self._run_plugin(name, today):
                    done.add(name)
        else:
            self._run_plugin(run_only, today)
