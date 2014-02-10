# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from decimal import Decimal as D
from dateutil import rrule
from lck.cache import memoize

from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.common.models import (
    EditorTrackable,
    Named,
    TimeTrackable,
    WithConcurrentGetOrCreate,
)

from mptt.models import MPTTModel, TreeForeignKey


PRICE_DIGITS = 16
PRICE_PLACES = 6


def get_usages_count_price(
    query,
    start,
    end,
    warehouse_id=None,
    forecast=False
):
    '''
    Generate count and price from te DayliUsage query

    :param object query: DailyUsage query
    :param datetime start: Start of the time interval
    :param datetime end: End of the time interval
    :param integer warehouse_id: Warehouse id or None
    :param boolean forecast: Information about use forecast or real price
    :returns tuple: count and price
    :rtype tuple:
    '''
    days = (end - start).days + 1
    count = 0
    price = D(0)
    for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
        daily_count = 0
        for usage in query.filter(date=day):
            daily_count = usage.value
            if usage.type.average:
                count += daily_count / days
            else:
                count += daily_count
            try:
                daily_price = usage.type.get_price_at(
                    day,
                    warehouse_id,
                    forecast,
                )
            except (
                UsagePrice.DoesNotExist,
                UsagePrice.MultipleObjectsReturned,
            ):
                price = None
            else:
                if price is not None:
                    price += D(daily_count) * daily_price
    return count, price


class Warehouse(TimeTrackable, EditorTrackable, Named,
                WithConcurrentGetOrCreate):
    """
    Pricing warehouse model contains name and id from assets and own create
    and modified date
    """
    def __unicode__(self):
        return self.name


class Device(db.Model):
    """
    Pricing device model contains data downloaded from devices and assets.
    """
    name = db.CharField(verbose_name=_("name"), max_length=255)
    sn = db.CharField(max_length=200, null=True, blank=True)
    barcode = db.CharField(max_length=200, null=True, blank=True, default=None)
    device_id = db.IntegerField(
        verbose_name=_("device id"),
        unique=True,
    )
    asset_id = db.IntegerField(
        verbose_name=_("asset id"),
        unique=True,
        null=True,
        blank=True,
        default=None,
    )
    is_virtual = db.BooleanField(verbose_name=_("is virtual"), default=False)
    is_blade = db.BooleanField(verbose_name=_("is blade"), default=False)
    slots = db.FloatField(verbose_name=_("slots"), default=0)

    class Meta:
        verbose_name = _("device")
        verbose_name_plural = _("devices")

    def __unicode__(self):
        return '{} - {}'.format(self.name, self.device_id)

    def get_deprecated_status(self, start, end, venture):
        query = self.dailydevice_set.filter(
            pricing_venture=venture,
            date__gte=start,
            date__lte=end,
        )
        statuses = []
        last = None
        for daily_device in query:
            status = daily_device.is_deprecated
            if status != last:
                data = '%s: %s' % (daily_device.date, status)
                statuses.append(data)
            last = status
        return " ".join(statuses)

    def get_daily_usages(self, start, end):
        query = DailyUsage.objects.filter(pricing_device=self)
        for type_ in UsageType.objects.all():
            count, price = get_usages_count_price(
                query.filter(type=type_),
                start,
                end,
            )
            if count or price:
                yield {
                    'name': type_.name,
                    'count': count,
                    'price': price,
                }

    def get_daily_parts(self, start, end):
        ids = self.dailypart_set.filter(
            pricing_device=self.id,
            date__gte=start,
            date__lte=end,
        ).values_list('asset_id', flat=True)
        parts = []
        for asset_id in set(ids):
            price, cost = get_daily_price_cost(asset_id, self, start, end)
            parts.append(
                {
                    'name': self.dailypart_set.filter(
                        asset_id=asset_id
                    )[0].name,
                    'price': price,
                    'cost': cost,
                }
            )
        return parts


class ParentDevice(Device):
    class Meta:
        proxy = True


class Venture(MPTTModel):
    """
    Venture device model contains asset ventures.
    """
    venture_id = db.IntegerField()
    name = db.CharField(
        verbose_name=_("name"),
        max_length=255,
        default='',
    )
    department = db.CharField(
        verbose_name=_("department name"),
        max_length=255,
        default='',
    )
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        default=None,
        related_name=_('children'),
    )
    symbol = db.CharField(
        verbose_name=_("symbol"),
        max_length=32,
        blank=True,
        default="",
    )
    business_segment = db.TextField(
        verbose_name=_("Business segment"),
        max_length=75,
        blank=True,
        default="",
    )
    profit_center = db.CharField(
        verbose_name=_("Profit center"),
        max_length=75,
        blank=True,
        default="",
    )
    is_active = db.BooleanField(
        verbose_name=_("Is active"),
        default=False,
    )

    class Meta:
        verbose_name = _("venture")
        verbose_name_plural = _("ventures")

    class MPTTMeta:
        order_insertion_by = ['name']

    def __unicode__(self):
        return self.name

    def _by_venture(self, query, descendants):
        if descendants:
            ventures = self.get_descendants(include_self=True)
            return query.filter(pricing_venture__in=ventures)
        return query.filter(pricing_venture=self)

    def get_assets_count_price_cost(
        self,
        start,
        end,
        descendants=False,
        zero_deprecated=True,
        device_id=False,
    ):
        days = (end - start).days + 1
        query = DailyDevice.objects.filter(pricing_device__is_virtual=False)
        if device_id:
            query = query.filter(pricing_device_id=device_id)
        else:
            query = self._by_venture(query, descendants)
        query = query.filter(date__gte=start, date__lte=end)
        query = query.select_related('pricing_device', 'parent')
        total_count = 0
        total_price = D('0')
        total_cost = D('0')
        for daily_device in query:
            asset_price, asset_cost = daily_device.get_price_cost(
                zero_deprecated,
            )
            system_price, system_cost = daily_device.get_bladesystem_price_cost(  # noqa
                zero_deprecated,
            )
            blades_price, blades_cost = daily_device.get_blades_price_cost(
                zero_deprecated,
            )
            total_price += asset_price + system_price - blades_price
            total_cost += asset_cost + system_cost - blades_cost
            total_count += 1
        return total_count / days, total_price / days, total_cost

    def get_usages_count_price(self,
                               start,
                               end,
                               type_,
                               warehouse_id=None,
                               forecast=False,
                               descendants=False,
                               query=None):
        '''
        The filter part of get count and price single type of usage

        :param datetime start: Start of the time interval
        :param datetime end: End of the time interval
        :param object type_: UsageType object for whitch price and
                             count will be returned
        :param integer warehouse_id: Warehouse id or None
        :param object query: DailyUsage query
        :param boolean forecast: Information about use forecast or real price
        :param boolean descendants: If true, children price will be count
        :returns tuple: count and price
        :rtype tuple:
        '''
        if query is None:
            query = DailyUsage.objects
        query = query.filter(type=type_)
        query = self._by_venture(query, descendants)
        query = query.filter(date__gte=start, date__lte=end)

        if warehouse_id:
            query = query.filter(warehouse=warehouse_id)

        return get_usages_count_price(
            query,
            start,
            end,
            warehouse_id,
            forecast,
        )

    def get_extra_costs(self, start, end, type_, descendants=False):
        '''
        The filter part of get count and price single type of usage

        :param datetime start: Start of the time interval
        :param datetime end: End of the time interval
        :param object type_: UsageType object for whitch price and
                             count will be returned
        :returns decimal: price
        :rtype decimal:
        '''
        price = D('0')
        query = ExtraCost.objects.filter(type=type_)
        query = self._by_venture(query, descendants)
        for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
            extras = query.filter(start__lte=day, end__gte=day)
            price += extras.aggregate(db.Sum('price'))['price__sum'] or 0
        return price

    def get_extracost_details(self, start, end):
        extracost = ExtraCost.objects.filter(
            start__gte=start,
            end__lte=end,
            pricing_venture=self,
        )
        return extracost

    def get_daily_usages(self, start, end):
        query = DailyUsage.objects.filter(pricing_device=None)
        query = self._by_venture(query, descendants=False)
        for type_ in UsageType.objects.all():
            count, price = get_usages_count_price(
                query.filter(type=type_),
                start,
                end,
            )
            if count or price:
                yield {
                    'name': type_.name,
                    'count': count,
                    'price': price,
                }


class DailyPart(db.Model):
    date = db.DateField()
    name = db.CharField(verbose_name=_("name"), max_length=255)
    pricing_device = db.ForeignKey(Device)
    asset_id = db.IntegerField()
    price = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("price"),
        default=0,
    )
    deprecation_rate = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("deprecation rate"),
        default=0,
    )
    is_deprecated = db.BooleanField(
        verbose_name=_("is deprecated"),
        default=False,
    )
    daily_cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("daily cost"),
        default=0,
    )
    monthly_cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("monthly cost"),
        default=0,
    )

    class Meta:
        verbose_name = _("daily part")
        verbose_name_plural = _("daily parts")
        unique_together = ('date', 'asset_id')
        ordering = ('asset_id', 'pricing_device', 'date')

    def __unicode__(self):
        return '{} ({})'.format(self.name, self.date)

    def get_price_cost(self, zero_deprecated=True):
        if zero_deprecated and self.is_deprecated:
            return D('0'), D('0')
        total_cost = self.price * self.deprecation_rate / 36500
        return self.price, total_cost

    def calc_costs(self):
        """
        Calculates daily and monthly depreciation costs
        """
        self.daily_cost = self.deprecation_rate * self.price / 36500 if not \
            self.is_deprecated else 0
        self.monthly_cost = self.deprecation_rate * self.price / 1200 if not \
            self.is_deprecated else 0

    def save(self):
        self.calc_costs()
        super(DailyPart, self).save()


def get_daily_price_cost(asset_id, device, start, end):
    days = (end - start).days + 1
    query = DailyPart.objects.filter(
        asset_id=asset_id,
        pricing_device=device,
        date__gte=start,
        date__lte=end,
    )
    total_price, total_cost = 0, 0
    for daily in query:
        price, cost = daily.get_price_cost()
        total_price += price
        total_cost += cost
    return total_price / days, total_cost


class DailyDevice(db.Model):
    """
    Model for daily imprint of device
    """
    date = db.DateField()
    name = db.CharField(verbose_name=_("name"), max_length=255)
    pricing_device = db.ForeignKey(
        Device,
        verbose_name=_("pricing device"),
    )
    parent = db.ForeignKey(
        # Note: this is only relevant for blade and virtual servers.
        ParentDevice,
        verbose_name=_("parent"),
        related_name='child_set',
        null=True,
        blank=True,
        default=None,
        on_delete=db.SET_NULL,
    )
    price = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("price"),
        default=0,
    )
    deprecation_rate = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("deprecation rate"),
        default=0,
    )
    pricing_venture = db.ForeignKey(
        Venture,
        verbose_name=_("venture"),
        null=True,
        blank=True,
        default=None,
        on_delete=db.SET_NULL,
    )
    is_deprecated = db.BooleanField(
        verbose_name=_("is deprecated"),
        default=False,
    )
    daily_cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("daily cost"),
        default=0,
    )
    monthly_cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("monthly cost"),
        default=0,
    )

    class Meta:
        verbose_name = _("daily device")
        verbose_name_plural = _("daily devices")
        unique_together = ('date', 'pricing_device')

    def __unicode__(self):
        return '{} ({})'.format(self.name, self.date)

    def get_price_cost(self, zero_deprecated=True):
        """
        Return the price and daily cost of the device on that day.
        This only includes the price of the asset itself, not the
        prices of its parents (in case of blade systems).
        """

        total_price = D('0')
        total_cost = D('0')
        # If the device has parts, sum them up
        for daily_part in self.pricing_device.dailypart_set.filter(
                date=self.date,
        ):
            price, cost = daily_part.get_price_cost()
            total_price += price
            total_cost += cost
        # Otherwise just take the price and cost of the device
        if zero_deprecated and self.is_deprecated:
            return D('0'), D('0')
        if not total_price and not total_cost:
            total_price = self.price
            total_cost = self.price * self.deprecation_rate / 36500
        return total_price, total_cost

    def get_bladesystem_price_cost(
        self,
        zero_deprecated=True,
        daily_parent=None,
    ):
        """
        Return the fraction of the price and cost of the blade system
        containing this device.
        """

        total_price = D('0')
        total_cost = D('0')
        if (
            not self.pricing_device.is_blade or
            not self.parent or
            not self.pricing_device.slots
        ):
            return total_price, total_cost
        if not daily_parent:
            try:
                daily_parent = self.parent.dailydevice_set.get(
                    date=self.date,
                )
            except DailyDevice.DoesNotExist:
                pass
        if daily_parent and daily_parent.pricing_device.slots:
            system_price, system_cost = daily_parent.get_price_cost(
                zero_deprecated,
            )
            system_fraction = (
                D(self.pricing_device.slots) /
                D(daily_parent.pricing_device.slots)
            )
            total_cost += system_cost * system_fraction
            total_price += system_price * system_fraction
        return total_price, total_cost

    def get_blades_price_cost(self, zero_deprecated=True):
        """
        Return the prices and costs that the blades contained in a blade
        system subtract from that blade system.
        """

        total_price = D('0')
        total_cost = D('0')
        if self.pricing_device.slots and not self.pricing_device.is_blade:
            try:
                blades = self.pricing_device.children_set.filter(
                    date=self.date,
                    pricing_device__is_blade=True,
                )
            except AttributeError:
                pass
            else:
                for blade in blades:
                    price, cost = blade.get_bladesystem_price_cost(
                        zero_deprecated,
                        self,
                    )
                    total_price += price
                    total_cost += cost
        return total_price, total_cost

    def calc_costs(self):
        """
        Calculates daily and monthly depreciation costs
        """
        self.daily_cost = self.deprecation_rate * self.price / 36500 if not \
            self.is_deprecated else 0
        self.monthly_cost = self.deprecation_rate * self.price / 1200 if not \
            self.is_deprecated else 0

    def save(self):
        self.calc_costs()
        super(DailyDevice, self).save()


class UsageType(db.Model):
    """
    Model contains usage types
    """
    name = db.CharField(verbose_name=_("name"), max_length=255, unique=True)
    symbol = db.CharField(
        verbose_name=_("symbol"),
        max_length=255,
        default="",
        blank=True,
    )
    average = db.BooleanField(
        verbose_name=_("Average the values over multiple days"),
        default=False,
    )
    show_value_percentage = db.BooleanField(
        verbose_name=_("Show percentage of value"),
        default=False,
    )
    show_price_percentage = db.BooleanField(
        verbose_name=_("Show percentage of price"),
        default=False,
    )
    by_warehouse = db.BooleanField(
        default=False,
    )
    by_cost = db.BooleanField(
        default=False,
    )
    show_in_report = db.BooleanField(
        verbose_name=_("Show usage type in report"),
        default=True,
    )

    class Meta:
        verbose_name = _("usage type")
        verbose_name_plural = _("usage types")

    def __unicode__(self):
        return self.name

    @memoize
    def _get_price_from_cost(self, cost, usage, warehouse_id):
        '''
        Get price from cost for given date and warehouse

        :param decimal cost: Cost for given time interval
        :param object usage: Usage object
        :param integer warehouse_id: warehouse id or None
        :returns decimal: price
        :rtype decimal:
        '''
        dailyusages = DailyUsage.objects.filter(
            date__gte=usage.start,
            date__lte=usage.end,
            type=self.id,
            warehouse_id=warehouse_id,
        )

        total_usage = sum([D(dailyusage.value) for dailyusage in dailyusages])
        if total_usage == 0:
            return 0
        return D(cost / total_usage / ((usage.end - usage.start).days + 1))

    def get_price_at(self, date, warehouse_id, forecast):
        '''
        Get price for the specified warehouse for the given day

        :param datetime date: Day for which the price will be returned
        :param integer warehouse_id: warehouse id or None
        :param boolean forecast: Information about use forecast or real price
        :returns decimal: price
        :rtype decimal:
        '''
        usage = self.usageprice_set.get(
            start__lte=date,
            end__gte=date,
            warehouse=warehouse_id,
        )

        price = usage.forecast_price if forecast else usage.price
        cost = usage.forecast_cost if forecast else usage.cost

        if not price and cost:
            return self._get_price_from_cost(
                cost,
                usage,
                warehouse_id,
            )
        else:
            return price


class UsagePrice(db.Model):
    """
    Model contains usages price information
    """
    type = db.ForeignKey(UsageType, verbose_name=_("type"))
    price = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("price"),
        default=0,
    )
    forecast_price = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("forecast price"),
        default=0,
    )
    cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        default=0.00,
        verbose_name=_("cost"),
    )
    forecast_cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        default=0.00,
        verbose_name=_("forecast cost"),
    )
    start = db.DateField()
    end = db.DateField()
    warehouse = db.ForeignKey(
        Warehouse,
        null=True,
        blank=True,
        on_delete=db.PROTECT,
    )

    class Meta:
        verbose_name = _("usage price")
        verbose_name_plural = _("usage prices")

        unique_together = [
            ('warehouse', 'start', 'type'),
            ('warehouse', 'end', 'type'),
        ]
        ordering = ('type', '-start')

    def __unicode__(self):
        return '{}-{} ({}-{})'.format(
            self.warehouse,
            self.type,
            self.start,
            self.end,
        )


class DailyUsage(db.Model):
    """
    DailyUsage model contains daily usage information for each
    usage
    """
    date = db.DateTimeField()
    pricing_venture = db.ForeignKey(
        Venture,
        verbose_name=_("venture"),
        null=True,
        blank=True,
        default=None,
        on_delete=db.SET_NULL,
    )
    pricing_device = db.ForeignKey(
        Device,
        verbose_name=_("pricing device"),
        null=True,
        blank=True,
        default=None,
        on_delete=db.SET_NULL,
    )
    value = db.FloatField(verbose_name=_("value"), default=0)
    total = db.FloatField(verbose_name=_("total usage"), default=0)
    type = db.ForeignKey(UsageType, verbose_name=_("type"))
    warehouse = db.ForeignKey(Warehouse, null=True, on_delete=db.PROTECT)
    remarks = db.TextField(
        verbose_name=_("Remarks"),
        help_text=_("Additional information."),
        blank=True,
        default="",
    )

    class Meta:
        verbose_name = _("daily usage")
        verbose_name_plural = _("daily usages")
        unique_together = ('date', 'pricing_device', 'type', 'pricing_venture')
        ordering = ('pricing_device', 'type', 'date')

    def __unicode__(self):
        return '{0}/{1} ({2}) {3}'.format(
            self.pricing_device,
            self.type,
            self.date,
            self.value,
        )


class ExtraCostType(db.Model):
    name = db.CharField(verbose_name=_("name"), max_length=255, unique=True)

    class Meta:
        verbose_name = _("extra cost type")
        verbose_name_plural = _("extra cost types")

    def __unicode__(self):
        return self.name

    def get_cost_at(self, date):
        return 1  # XXX


class ExtraCost(db.Model):
    start = db.DateField()
    end = db.DateField()
    type = db.ForeignKey(ExtraCostType, verbose_name=_("type"))
    price = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("price"),
    )
    pricing_venture = db.ForeignKey(Venture, verbose_name=_("venture"))

    class Meta:
        verbose_name = _("extra cost")
        verbose_name_plural = _("extra costs")
        unique_together = [
            ('start', 'pricing_venture', 'type'),
            ('end', 'pricing_venture', 'type'),
        ]

    def __unicode__(self):
        return '{}/{} ({} - {})'.format(
            self.pricing_venture,
            self.type,
            self.start,
            self.end,
        )
