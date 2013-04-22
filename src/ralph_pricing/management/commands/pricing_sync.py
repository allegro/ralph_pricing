# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from optparse import make_option
import textwrap
import datetime

from django.core.management.base import BaseCommand

from ralph.discovery.tasks import run_chain


class Command(BaseCommand):
    """Retrieve data for pricing for today"""

    help = textwrap.dedent(__doc__).strip()
    option_list = BaseCommand.option_list + (
        make_option(
            '--remote',
            action='store_true',
            dest='remote',
            default=False,
            help='Run the command on remote workers',
        ),
    )
    requires_model_validation = True

    def handle(self, *args, **options):
        from ralph_pricing import plugins  # noqa
        interactive = not options['remote']
        options['today'] = datetime.date.today()
        run_chain(
            options, 'pricing', interactive=interactive,
        )

