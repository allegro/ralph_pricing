# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

from ralph_pricing.plugins.base import register
from ralph_pricing.plugins.reports.base import BaseReportPlugin

logger = logging.getLogger(__name__)


@register(chain='reports')
class Information(BaseReportPlugin):
    def costs(self, *args, **kwargs):
        """
        Return informations about given ventures

        usages = {
            'venture_id': {
                'field_name': value,
                ...
            },
            ...
        }

        :returns dict: informations about ventures
        :rtype dict:
        """
        logger.debug("Get information usage")
        usages = {}
        for venture in kwargs.get('ventures'):
            venture_name = '/'.join(
                v.name for v in venture.get_ancestors(include_self=True),
            )
            usages[venture.id] = {
                'venture_id': venture.venture_id,
                'venture': venture_name,
                'department': venture.department,
                'business_segment': venture.business_segment,
                'profit_center': venture.profit_center,
            }
        return usages

    def schema(self, *args, **kwargs):
        """
        Build schema for this usage. Format of schema looks like:

        schema = {
            'field_name': {
                'name': 'Verbous name',
                'next_option': value,
                ...
            },
            ...
        }

        :returns dict: schema for usage
        :rtype dict:
        """
        logger.debug("Get information schema")
        schema = OrderedDict()
        schema['venture_id'] = {
            'name': _("ID"),
        }
        schema['venture'] = {
            'name': _("Venture"),
        }
        schema['department'] = {
            'name': _("Department"),
        }
        schema['business_segment'] = {
            'name': _("Business segment"),
        }
        schema['profit_center'] = {
            'name': _("Profit center"),
        }
        return schema

    def total_cost(self, *args, **kwargs):
        raise NotImplementedError()
