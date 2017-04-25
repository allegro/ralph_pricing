# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from ralph_scrooge.utils.common import validate_date
from ralph_scrooge.plugins.validations import (
    DataForReportValidationError,
    DataForReportValidator
)


class Command(BaseCommand):
    """
    Validate data for costs report for particular date.
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=validate_date,
            dest='date',
            required=True,
        )

    def handle(self, *args, **options):
        validator = DataForReportValidator(options['date'])
        try:
            validator.validate()
        except DataForReportValidationError as e:
            for error in e.errors:
                self.stdout.write(error)
