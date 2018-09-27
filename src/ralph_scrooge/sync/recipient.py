import logging
from datetime import datetime

from django.conf import settings
from django.db import transaction

from ralph_scrooge.models import ExtraCost, ExtraCostType, ServiceEnvironment

logger = logging.getLogger(__name__)


def accepted_costs_handler(date_from, date_to, type_, costs):
    logger.info(
        'Start accepted costs processing (between {} and {}): '.format(
            date_from, date_to
        )
    )

    extra_cost_type = ExtraCostType.objects_admin.get_or_create(
        symbol=type_,
        defaults=dict(
            name=type_,
        )
    )[0]

    extra_costs = _prepare_extra_costs(costs, date_from, date_to, extra_cost_type)
    _update_extra_costs(extra_cost_type, date_from, date_to, extra_costs)

    logger.info(
        'End of accepted costs processing (between {} and {}): '.format(
            date_from, date_to
        )
    )


def _update_extra_costs(extra_cost_type, date_from, date_to, extra_costs):
    with transaction.atomic():
        deleted = extra_cost_type.extracost_set.filter(start=date_from, end=date_to).delete()
        logger.info('Deleted {} previously saved extra costs of type {}'.format(
            deleted, extra_cost_type
        ))
        ExtraCost.objects.bulk_create(extra_costs)


def _prepare_extra_costs(costs, date_from, date_to, extra_cost_type):
    import_datetime = datetime.now()
    extra_costs = []  # List[ExtraCost]

    service_envs = {
        (se.service.ci_uid, se.environment.name): se.id
        for se in ServiceEnvironment.objects.filter(
            service__business_line_id=settings.ACCEPTED_COSTS_SYNC_HANDLER_BUSINESS_LINE_ID
        ).select_related('service', 'environment')
    }

    for cost_info in costs:
        service_uid, env_name = cost_info['service_uid'], cost_info['environment']
        try:
            service_env_id = service_envs[(service_uid, env_name)]
        except KeyError:
            logger.info('Ignoring costs for service {} - {}'.format(
                service_uid, env_name
            ))
        else:
            extra_cost = ExtraCost(
                start=date_from,
                end=date_to,
                service_environment_id=service_env_id,
                cost=cost_info['total_cost'],
                forecast_cost=cost_info['total_cost'],
                extra_cost_type=extra_cost_type,
                remarks='Imported at {}'.format(import_datetime)
            )
            extra_costs.append(extra_cost)
            logger.info('Saving imported cost for {} - {}'.format(service_uid, env_name))
    return extra_costs
