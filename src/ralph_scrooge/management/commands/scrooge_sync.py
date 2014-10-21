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

from ralph_scrooge.models import SyncStatus


logger = logging.getLogger(__name__)

PLUGINS_LOADED = False


class PluginError(Exception):
    pass


def _load_plugins():
    """
    Loads all collect plugins using scrooge.collect_plugins entry point.
    """
    global PLUGINS_LOADED
    if not PLUGINS_LOADED:
        for p in pkg_resources.iter_entry_points('scrooge.collect_plugins'):
            p.load()
        PLUGINS_LOADED = True


def get_collect_plugins_names():
    _load_plugins()
    return sorted([name for name in plugin.BY_NAME['scrooge'].keys()
                   if name in settings.COLLECT_PLUGINS])


def _run_plugin(name, today):
    logger.info('Running {0}...'.format(name))
    success, message = False, None
    sync_status = SyncStatus.objects.get_or_create(plugin=name, date=today)[0]
    try:
        success, message = plugin.run(
            'scrooge',
            name,
            today=today,
        )
        if not success:
            raise PluginError(message)
    except Exception as e:
        logger.exception("{0}: {1}".format(name, e))
        raise PluginError(e)
    finally:
        sync_status.success = success
        sync_status.remarks = message
        sync_status.save()
        logger.info('Done: {0}'.format(message))


def run_plugins(today, plugins, run_only=False):
    _load_plugins()
    logger.info('Synchronizing for {0}.'.format(today.isoformat()))
    done = set()
    tried = set()
    if run_only:
        name = plugins[0]
        try:
            _run_plugin(name, today)
            yield name, True
        except Exception:
            yield name, False
    else:
        while True:
            to_run = plugin.next('scrooge', done) - tried
            if not to_run:
                break
            name = plugin.highest_priority('scrooge', to_run)
            tried.add(name)
            if name in plugins:
                try:
                    _run_plugin(name, today)
                    done.add(name)
                    yield name, True
                except PluginError:
                    yield name, False

        # save not executed plugins
        for p in set(plugins) - tried:
            status = SyncStatus.objects.get_or_create(
                date=today,
                plugin=p,
            )[0]
            status.success = False
            status.remarks = 'Not executed'
            status.save()


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

    def handle(self, today, run_only, *args, **options):
        if today:
            today = datetime.datetime.strptime(today, '%Y-%m-%d').date()
        else:
            today = datetime.date.today()

        if options.get('yesterday'):
            today -= datetime.timedelta(days=1)
        if not run_only:
            for r in run_plugins(today, settings.COLLECT_PLUGINS):
                pass
        else:
            for r in run_plugins(today, [run_only], run_only=True):
                pass
