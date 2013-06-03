# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import textwrap
import datetime
from optparse import make_option

from django.core.management.base import BaseCommand

from ralph.util import plugin


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

    def handle(self, today, run_only, *args, **options):
        from ralph_pricing import plugins  # noqa
        if today:
            today = datetime.datetime.strptime(today, '%Y-%m-%d').date()
        else:
            today = datetime.date.today()
        print('Synchronizing for {0}.'.format(today.isoformat()))
        if run_only:
            print('Running only {0}...'.format(run_only))
            success, message, context = plugin.run(
                'pricing',
                run_only,
                today=today,
            )
            print('{1}: {0}'.format(message, 'Done' if success else 'Failed'))
            return
        done = set()
        tried = set()
        while True:
            to_run = plugin.next('pricing', done) - tried
            if not to_run:
                break
            name = plugin.highest_priority('pricing', to_run)
            tried.add(name)
            print('Running {0}...'.format(name))
            success, message, context = plugin.run(
                'pricing', name, today=today,
            )
            print('{1}: {0}'.format(message, 'Done' if success else 'Failed'))
            if success:
                done.add(name)
