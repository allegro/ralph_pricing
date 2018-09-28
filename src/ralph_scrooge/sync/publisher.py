"""
Publish accepted costs to configured recipients.
"""
import logging

import dateutil.parser
import requests
from django.conf import settings
from django.db.models import F, Sum, Func
from ralph_scrooge.models import DailyCost

logger = logging.getLogger(__name__)


class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 2)'


def publish_accepted_costs_dump(date_from, date_to, forecast=False):
    dump = _prepare_accepted_costs_dump(date_from, date_to, forecast)
    _publish_dump(dump)


def _prepare_accepted_costs_dump(date_from, date_to, forecast):
    if isinstance(date_from, basestring):
        date_from = dateutil.parser.parse(date_from)
    if isinstance(date_to, basestring):
        date_to = dateutil.parser.parse(date_to)

    se_costs = DailyCost.objects.filter(
        forecast=forecast, date__gte=date_from, date__lte=date_to
    ).values(
        # need to put these in values first to include it in "GROUP BY" clause
        'service_environment__service__ci_uid',
        'service_environment__environment__name'
    ).annotate(
        service_uid=F('service_environment__service__ci_uid'),
        environment=F('service_environment__environment__name'),
        total_cost=Round(Sum('cost'))
    ).values(
        'service_uid', 'environment', 'total_cost'
    )

    result = {
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
        'type': settings.ACCEPTED_COSTS_SYNC_TYPE,
        'costs': list(se_costs)
    }
    return result


def _publish_dump(dump):
    for recipient_url, auth_token in settings.ACCEPTED_COSTS_SYNC_RECIPIENTS:
        response = requests.post(  # todo: retry, timeout
            recipient_url,
            json=dump,
            headers={
                'Authorization': 'Token {}'.format(auth_token),
                'Content-Type': 'application/json'
            }
        )
        try:
            response.raise_for_status()
        except requests.HTTPError:
            logger.error('Error publishing accepted costs to {}: {}'.format(
                recipient_url, response.text
            ))
