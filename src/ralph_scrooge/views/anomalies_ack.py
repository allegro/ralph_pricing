# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from argparse import ArgumentTypeError

from django.http import Http404
from django.shortcuts import render_to_response
from django.views.generic import View

from ralph_scrooge.models import (
    UsageType,
    UsageAnomalyAck,
)
from ralph_scrooge.utils.common import validate_date


class AnomaliesAck(View):

    def _is_request_valid(self, ut_id, date, user):
        """By "valid request" we understand that:
        - `ut_id` points to an existing UsageType
        - `date` is a valid date
        - `user` is one of the owners of UsageType pointed by `ut_id`
        """
        try:
            ut = UsageType.objects.get(id=ut_id)
            validate_date(date)
        except (UsageType.DoesNotExist, ArgumentTypeError):
            return False
        if user not in ut.owners.all():
            return False
        return True

    # POST would be an overkill here, really...
    def get(self, request):
        ut_id = request.GET.get('ut_id')
        date = request.GET.get('date')
        if (
            not (ut_id and date) or
            not self._is_request_valid(ut_id, date, self.request.user)
        ):
            raise Http404
        UsageAnomalyAck.objects.get_or_create(
            type_id=ut_id,
            anomaly_date=date,
            acknowledged_by=request.user,
        )
        return render_to_response('ralph_scrooge/anomalies_ack.html')
