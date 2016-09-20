# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


WARN_MSG = u"""
This migration does IRREVERSIBLE changes!
Which means removing warehouses other then these:
- warehouse with name 'Default',
- warehouse with name NOT matching datacenters names from Asset Datacenter
    models

{to_delete_count} warehouses to delete:
{up_to_delete_names}
{left_count} warehouses will be left after migration:
{left_names}

Type 'yes' to procceed.
"""


class Migration(DataMigration):

    def forwards(self, orm):
        """
        Deleted because we don't use models from ralph asset.
        """
        pass

    def backwards(self, orm):
        """
        Deleted because we don't use models from ralph asset.
        """
        pass
