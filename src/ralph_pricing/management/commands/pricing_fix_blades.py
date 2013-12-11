# -*- coding: utf-8 -*-

"""A one-time command that should fix the devices in pricing that have no
slot information. We take this info from catalog to fix existing data."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import textwrap
from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    """Check for the devices in the database that are parts of blade systems,
    but have no 'slots' set. Try to fix this information with the use of
    catalog."""

    help = textwrap.dedent(__doc__).strip()

    option_list = BaseCommand.option_list + (
        make_option(
            '--commit',
            dest='commit',
            action='store_true',
            help="Commit the fix to the database",
        ),
    )

    FIX_QUERY = """
        UPDATE ralph_pricing_device
        LEFT JOIN discovery_device
            ON ralph_pricing_device.device_id = discovery_device.id
        LEFT JOIN discovery_devicemodel
            ON discovery_device.model_id = discovery_devicemodel.id
        LEFT JOIN discovery_devicemodelgroup
            ON discovery_devicemodelgroup.id = discovery_devicemodel.group_id
        SET ralph_pricing_device.slots = discovery_devicemodelgroup.slots
        WHERE ralph_pricing_device.is_blade = 1 AND
            ralph_pricing_device.slots = 0 AND
            discovery_devicemodelgroup.slots IS NOT NULL;
    """
    COUNT_QUERY = """
        SELECT COUNT(*) FROM ralph_pricing_device
        WHERE ralph_pricing_device.is_blade = 1 AND
            ralph_pricing_device.slots = 0;
    """

    def __init__(self):
        self.cur = connection.cursor()

    def _get_broken_count(self):
        """Return the number of currently slotless blade devices."""
        self.cur.execute(self.COUNT_QUERY)
        return self.cur.fetchall()[0][0]

    def handle(self, commit, **kwargs):
        """Perform the query and print out some stats."""
        before_count = self._get_broken_count()
        self.cur.execute(self.FIX_QUERY)
        after_count = self._get_broken_count()
        fixed_count = before_count - after_count

        print("""
Blade devices without slots:
Before fix: {before_count}
Fixed: {fixed_count}
Left: {after_count}
        """.format(**locals()))
        if commit:
            transaction.commit_unless_managed()
        else:
            print(
                "Use this command with --commit switch to commit the fix to"
                " database."
            )
