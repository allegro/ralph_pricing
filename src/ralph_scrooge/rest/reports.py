# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import dateutil
import itertools
import logging

from ralph_scrooge.csvutil import make_csv_response
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from ralph_scrooge.models import UsageType
from ralph_scrooge.report.report_services_costs import ServicesCostsReport
from ralph_scrooge.report.report_services_usages import ServicesUsagesReport

logger = logging.getLogger(__name__)


def format_csv_header(header):
    """
    Format csv header rows. Insert empty cells to show rowspan and colspan.
    """
    result = []
    for row in header:
        output_row = []
        for col in row:
            output_row.append(col[0])
            for colspan in range((col[1].get('colspan') or 1) - 1):
                output_row.append('')
        result.append(output_row)
    # rowspans
    for row_num, row in enumerate(header):
        i = 0
        for col in row:
            if 'rowspan' in col[1]:
                for rowspan in range(1, (col[1]['rowspan'] or 1)):
                    result[row_num + rowspan].insert(i, '')
            i += col[1].get('colspan', 1)
    return result


class BaseReportContent(APIView):
    allow_csv_download = True
    section = ''

    def __init__(self, *args, **kwargs):
        super(BaseReportContent, self).__init__(*args, **kwargs)
        self.data = []
        self.header = []
        self.progress = 0

    def _get_params(self, request):
        return {}

    def get(self, request):
        self.progress, result = self.run_on_worker(
            **self._get_params(request)
        )
        if result:
            self.header, self.data = result
            self._format_header()

        self.progress = round(self.progress, 0)
        if request.QUERY_PARAMS.get('report_format', '').lower() == 'csv':
            if self.progress == 100:
                self.header = format_csv_header(self.header)
                return make_csv_response(
                    itertools.chain(self.header, self.data),
                    '{}.csv'.format(self.section),
                )
        response_data = {
            "status": True,
            "progress": self.progress,
            "finished": self.progress == 100,
        }
        return Response(response_data)

    def delete(self, request):
        self._clear_cache(**self._get_params(request))
        return Response(status=HTTP_204_NO_CONTENT)

    def _format_header(self):
        """
        Format header to make tuple of (text, options dict) for each cell.
        """
        result = []
        for row in self.header:
            output_row = []
            for col in row:
                if not isinstance(col, (tuple, list)):
                    col = (col, {})
                output_row.append(col)
            result.append(output_row)
        self.header = result

    def run_on_worker(self, **kwargs):
        return self.report.run_on_worker(**kwargs)

    def _clear_cache(self, **kwargs):
        return self.report._clear_cache(**kwargs)

    def _parse_start_end(self, request):
        params = {}
        for date in ['start', 'end']:
            try:
                params[date] = dateutil.parser.parse(
                    request.QUERY_PARAMS.get('start')
                )
            except ValueError:
                raise ParseError('Invalid value for {} param'.format(
                    date
                ))
        return params

    def _parse_bool_param(self, request, param):
        return str(request.QUERY_PARAMS.get(param)) in ('1', 'true')


class UsagesReportContent(BaseReportContent):
    report = ServicesUsagesReport()
    section = 'services-usages-report'

    def _get_params(self, request):
        params = self._parse_start_end(request)
        try:
            params['usage_types'] = UsageType.objects.filter(
                pk__in=request.QUERY_PARAMS.getlist('usage_types')
            )
        except ValueError:
            raise ParseError('Invalid value for usage_types param')
        return params


class ServicesCostsReportContent(BaseReportContent):
    report = ServicesCostsReport()
    section = 'services-costs-report'

    def _get_params(self, request):
        params = self._parse_start_end(request)
        params['forecast'] = self._parse_bool_param(request, 'forecast')
        params['is_active'] = self._parse_bool_param(request, 'is_active')
        return params
