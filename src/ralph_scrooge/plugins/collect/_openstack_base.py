# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
import time

from ralph_scrooge.utils.common import memoize
from sqlalchemy import create_engine

from ralph_scrooge.models import (
    DailyTenantInfo,
    DailyUsage,
    TenantInfo,
    UsageType,
    Warehouse
)


logger = logging.getLogger(__name__)


class TenantNotFoundError(Exception):
    """
    Raised when tenant info does not exist
    """
    pass


class DailyTenantNotFoundError(Exception):
    """
    Raised when daily tenant info does not exist
    """
    pass


class OpenStackBasePlugin(object):
    metric_tmpl = None
    metric_with_prefix_tmpl = None
    query = None  # should return (project_id, value, matric name)
    plugin_name = 'OpenStack'

    def _format_date(self, d):
        return time.mktime(d.timetuple())

    @memoize
    def get_usage_type(self, flavor_name, prefix=None):
        if prefix:
            usage_name = self.metric_with_prefix_tmpl.format(
                prefix,
                flavor_name
            )
        else:
            usage_name = self.metric_tmpl.format(flavor_name)
        usage_symbol = usage_name.lower().replace(':', '.').replace(' ', '_')
        return UsageType.objects.get_or_create(
            symbol=usage_symbol,
            defaults=dict(
                name=usage_name,
                show_in_services_report=False,
                type='SU',
            ),
        )[0]

    @memoize
    def get_daily_tenant(self, tenant_id, date):
        try:
            tenant = TenantInfo.objects.get(tenant_id=tenant_id)
            return tenant.daily_tenants.get(date=date)
        except TenantInfo.DoesNotExist as e:
            raise TenantNotFoundError(e)
        except DailyTenantInfo.DoesNotExist as e:
            logger.warning('DailyTenant {} for date {} not found'.format(
                tenant_id,
                date,
            ))
            return tenant.get_daily_pricing_object(date)

    def get_usages(self, date, connection_string):
        """
        Function which talks with openstack
        """
        date_from = datetime.datetime.combine(date, datetime.datetime.min.time())
        date_to = date_from + datetime.timedelta(days=1)

        engine = create_engine(connection_string)
        connection = engine.connect()
        params = dict(
            from_ts=date_from,
            to_ts=date_to,
        )
        if self.use_mktime:
            params = {k: self._format_date(v) for (k, v) in params.items()}
        query = self.query.format(**params)
        return connection.execute(query)

    def save_usages(self, usages, date, warehouse, prefix=None):
        new = total = 0
        for tenant_id, value, flavor_name in usages:
            total += 1
            usage_type = self.get_usage_type(flavor_name, prefix)
            try:
                daily_tenant = self.get_daily_tenant(tenant_id, date)
            except TenantNotFoundError:
                logger.error('Tenant {} not found'.format(tenant_id))
                continue
            DailyUsage(
                date=date,
                service_environment=daily_tenant.service_environment,
                daily_pricing_object=daily_tenant,
                value=value,
                type=usage_type,
                warehouse=warehouse,
            ).save()
            new += 1
        return new, total

    def clear_previous_usages(self, date):
        logger.debug('Clearing previous records for {}'.format(date))
        DailyUsage.objects.filter(
            type__symbol__startswith=self.metric_tmpl.format(''),
            date=date,
        ).delete()

    def run_plugin(self, sites, today, **kwargs):
        self.clear_previous_usages(today)
        new = total = 0
        for site in sites:
            logger.info(
                "Processing {} {}".format(
                    self.plugin_name,
                    site['WAREHOUSE'],
                )
            )
            try:
                warehouse = Warehouse.objects.get(name=site['WAREHOUSE'])
            except Warehouse.DoesNotExist:
                logger.error('Invalid warehouse: {}'.format(
                    site['WAREHOUSE']
                ))
                continue
            usages = self.get_usages(today, site['CONNECTION'])
            site_new, site_total = self.save_usages(
                usages,
                today,
                warehouse,
                prefix=site.get('USAGE_PREFIX'),
            )

            logger.info(
                '{} new, {} total usages saved for {}'.format(
                    site_new,
                    site_total,
                    site['WAREHOUSE'],
                )
            )

            new += site_new
            total += site_total

        return new, total
