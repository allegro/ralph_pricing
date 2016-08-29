# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import csv
import logging
import sys
import textwrap
from optparse import make_option

from django.core.management.base import BaseCommand
from django.db.transaction import commit_on_success

from ralph_scrooge.models import (
    PricingObjectModel,
    BusinessLine,
    Environment,
    ProfitCenter,
    TenantInfo,
    Warehouse,
)


logger = logging.getLogger(__name__)

MODEL_MAPPING = {
    'AssetModel': (PricingObjectModel, 'model_id', 'ralph3_model_id'),
    'BusinessSegment': (BusinessLine, 'ci_id', 'ralph3_id'),
    'DataCenter': (Warehouse, 'id_from_assets', 'ralph3_id'),
    'Environment': (Environment, 'ci_id', 'ralph3_id'),
    'ProfitCenter': (ProfitCenter, 'ci_id', 'ralph3_id'),
    'TenantInfo': (TenantInfo, 'tenant_id', 'ralph3_tenant_id'),
}


class Command(BaseCommand):
    """Retrieve data for pricing for base"""

    help = textwrap.dedent(__doc__).strip()
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
        make_option(
            '-m', '--model',
            dest='model',
            help="Model name",
            choices=MODEL_MAPPING.keys(),
        ),
        make_option(
            '-f', '--file',
            dest='file',
            help="CSV file with mapping Ralph2 (U)ID;Ralph3 ID",
            metavar="FILE"
        ),
    )

    @commit_on_success
    def handle(self, *args, **options):
        if not options.get('model') or not options.get('file'):
            print('Model and file params are required')
            sys.exit(1)

        model, ralph2_field, ralph3_field = MODEL_MAPPING[options['model']]

        with open(options['file'], 'r') as f:
            mapping = csv.reader(f, delimiter=b';')
            for ralph2_id, ralph3_id in mapping:
                try:
                    obj = model._default_manager.get(
                        **{ralph2_field: ralph2_id}
                    )
                except model.DoesNotExist:
                    logger.warning('{} with {}={} not found'.format(
                        options['model'], ralph2_field, ralph2_id
                    ))
                else:
                    logger.info('Saving {} with Ralph3 ID {}'.format(
                        obj, ralph3_id
                    ))
                    setattr(obj, ralph3_field, ralph3_id)
                    obj.save()
