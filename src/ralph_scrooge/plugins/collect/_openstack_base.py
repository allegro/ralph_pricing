# -*- coding: utf-8 -*-
"""
Base OpenStack collect plugin.
"""
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


class OpenStackBasePlugin(object):
    """
    Base plugin for OpenStack collect plugins.

    Can be used with any SQL database (ex. MySQL; just specify DB connection
    string and SQL query) or with any other source of data (then `get_usages`
    method has to be overwritten).

    :param metric_tmpl: template for metric name (without prefix)
    :type metric_tmpl: str
    :param metric_with_prefix_tmpl: template for metric name with prefix
        (prefix has to be specified in sites in settings)
    :type metric_with_prefix_tmpl: str
    :param query: SQL query to be used to get usage data. Query should return
        (project_id, value, matric name) tuple.
    :type query: str
    :param plugin_name: plugin name to display in logs
    :type plugin_name: str
    """
    metric_tmpl = 'openstack.{}'
    metric_with_prefix_tmpl = metric_tmpl + '.{}'
    query = ''  # should return (project_id, value, matric name)
    plugin_name = 'OpenStack'

    def _format_date(self, d):
        """
        Return date in format required by source of data

        :param d: datetime
        :type d: datetime.datetime
        """
        return time.mktime(d.timetuple())

    @memoize
    def get_usage_type(self, metric_name, prefix=None):
        """
        Return `ralph_scrooge.models.UsageType` for metric. If prefix is
        specified then `metric_with_prefix_tmpl` is used to create usage type
        name. Otherwise `metric_tmpl` is used.
        """
        if prefix:
            usage_name = self.metric_with_prefix_tmpl.format(
                prefix,
                metric_name
            )
        else:
            usage_name = self.metric_tmpl.format(metric_name)
        usage_symbol = usage_name.lower().replace(':', '.').replace(' ', '_')
        return UsageType.objects.get_or_create(
            symbol=usage_symbol,
            defaults=dict(
                name=usage_name,
                type='SU',
            ),
        )[0]

    @memoize
    def get_daily_tenant(self, tenant_id, date):
        """
        Return `ralph_scrooge.models.DailyTenant` instance for tenant_id and
        date.

        :param tenant_id: id of tenant
        :type tenant_id: int
        :param date: date
        :type date: datetime.date
        :rtype: `ralph_scrooge.models.DailyTenant`
        :raises TenantNotFoundError: if `ralph_scrooge.models.TenantInfo` with
            passed tenant_id was not found
        """
        try:
            tenant = TenantInfo.objects.get(tenant_id=tenant_id)
            return tenant.daily_tenants.get(date=date)
        except TenantInfo.DoesNotExist as e:
            raise TenantNotFoundError(e)
        except DailyTenantInfo.DoesNotExist:
            logger.warning('DailyTenant {} for date {} not found'.format(
                tenant_id,
                date,
            ))
            return tenant.get_daily_pricing_object(date)

    def _get_dates_from_to(self, date):
        """
        Return min and max `datetime.datetime` for given day.
        """
        date_from = datetime.datetime.combine(
            date,
            datetime.datetime.min.time()
        )
        date_to = datetime.datetime.combine(
            date,
            datetime.datetime.max.time()
        )
        return date_from, date_to

    def get_usages(self, date, connection_string):
        """
        Return usages from OpenStack for given date.

        :param connection_string: connection details
            (ex. mysql://user:pass@host/db)
        :type connection_string: str
        :return: list of usages
        :rtype: list
        """
        date_from, date_to = self._get_dates_from_to(date)
        engine = create_engine(connection_string)
        connection = engine.connect()
        params = dict(
            from_ts=self._format_date(date_from),
            to_ts=self._format_date(date_to),
        )
        query = self.query.format(**params)
        return connection.execute(query)

    def save_usages(self, usages, date, warehouse, prefix=None):
        """
        Save usages for single date into DB.
        """
        new = total = 0
        for usage in usages:
            if len(usage) == 3:
                tenant_id, value, metric_name = usage
                remarks = ''
            else:
                tenant_id, value, metric_name, remarks = usage
            total += 1
            usage_type = self.get_usage_type(metric_name, prefix)
            try:
                daily_tenant = self.get_daily_tenant(tenant_id, date)
            except TenantNotFoundError:
                logger.error('Tenant {} not found'.format(tenant_id))
                continue
            DailyUsage.objects.create(
                date=date,
                service_environment=daily_tenant.service_environment,
                daily_pricing_object=daily_tenant,
                value=value,
                type=usage_type,
                warehouse=warehouse,
                remarks=remarks,
            )
            new += 1
        return new, total

    def clear_previous_usages(self, date):
        """
        Remove previously saved records for given date from DB.
        """
        logger.debug('Clearing previous records for {}'.format(date))
        DailyUsage.objects.filter(
            type__symbol__startswith=self.metric_tmpl.format(''),
            date=date,
        ).delete()

    def run_plugin(self, sites, today, **kwargs):
        """
        Main method to run OpenStack plugin. Steps:
        * delete previous usages
        * for each site:
            * get data from OpenStack
            * save usages into DB
        """
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
