# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import textwrap
import datetime

from django.core.management.base import BaseCommand

from ralph.util import plugin


class Command(BaseCommand):
    """Retrieve data for pricing for today"""

    help = textwrap.dedent(__doc__).strip()
    requires_model_validation = True

    def handle(self, *args, **options):
        from ralph_pricing import plugins  # noqa
        today = datetime.date.today()
        done = set()
        tried = set()
        while True:
            to_run = plugin.next('pricing', done) - tried
            if not to_run:
                break
            name = plugin.highest_priority('pricing', to_run)
            tried.add(name)
            if plugin.run('pricing', name, today=today):
                done.add(name)

