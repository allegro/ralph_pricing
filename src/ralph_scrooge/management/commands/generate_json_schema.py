# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging
import os.path
import yaml

from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Generates JSON schema file from it's YAML counterpart identified by
    `API_SCHEMA_FILE`, which is expected to be present in settings. Previous
    version of such JSON schema will be overwritten.

    This command should be executed at every change of schema, as well as when
    Scrooge is installed.
    """

    def handle(self, *args, **options):
        if not settings.API_SCHEMA_FILE:
            logger.error(
                'API_SCHEMA_FILE is not defined in settings. Aborting.'
            )
            return
        if not os.path.exists(settings.API_SCHEMA_FILE):
            logger.error(
                'YAML API schema file "{}" does not exist. Aborting.'
                .format(settings.API_SCHEMA_FILE)
            )
            return

        with open(settings.API_SCHEMA_FILE, 'r') as f:
            try:
                schema = yaml.load(f)
            except yaml.YAMLError as e:
                logger.error(
                    "There's a problem with your YAML schema file: {}. "
                    "Aborting.".format(e)
                )
                return

        json_schema_filename = os.path.splitext(
            os.path.basename(settings.API_SCHEMA_FILE)
        )[0] + '.json'

        json_schema_file = os.path.join(
            os.path.dirname(settings.API_SCHEMA_FILE),
            json_schema_filename
        )
        with open(json_schema_file, 'w') as f:
            # Add `indent=4` here if you need human-friendly output.
            json.dump(schema, f, ensure_ascii=False)
        logger.info(
            'JSON API schema saved successfully as: {}'
            .format(json_schema_file)
        )
