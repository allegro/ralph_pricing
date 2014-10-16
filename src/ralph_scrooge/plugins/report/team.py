# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.report.base import BaseReportPlugin


logger = logging.getLogger(__name__)


@register(chain='scrooge_reports')
class TeamPlugin(BaseReportPlugin):
    """
    Extra costs plugin
    """
    base_usage_cost_symbol = 'cost_{0}'
