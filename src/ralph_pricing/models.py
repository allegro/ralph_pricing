# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from decimal import Decimal as D
from dateutil import rrule

from django.db import models as db
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey


PRICE_DIGITS = 16
PRICE_PLACES = 6


def get_usages_count_price(query, start, end):
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
                daily_price = usage.type.get_price_at(day)
            except (
                UsagePrice.DoesNotExist,
                UsagePrice.MultipleObjectsReturned,
            ):
                price = None
            else:
                if price is not None:
                    price += D(daily_count) * daily_price
    return count, price


class Device(db.Model):
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

    def get_usages_count_price(
        self, start, end, type_, descendants=False, query=None
    ):
        if query is None:
            query = DailyUsage.objects
        query = query.filter(type=type_)
        query = self._by_venture(query, descendants)
        query = query.filter(date__gte=start, date__lte=end)
        return get_usages_count_price(query, start, end)

    def get_extra_costs(self, start, end, type_, descendants=False):
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
                daily_parent = self.parent.dailydevice_set.filter(
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
            for blade in self.pricing_device.children_set.filter(
                    date=self.date,
                    pricing_device__is_blade=True,
            ):
                price, cost = blade.get_bladesystem_price_cost(
                    zero_deprecated,
                    self,
                )
                total_price += price
                total_cost += cost
        return total_price, total_cost


class UsageType(db.Model):
    name = db.CharField(verbose_name=_("name"), max_length=255, unique=True)
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

    class Meta:
        verbose_name = _("usage type")
        verbose_name_plural = _("usage types")

    def __unicode__(self):
        return self.name

    def get_price_at(self, date):
        return self.usageprice_set.get(start__lte=date, end__gte=date).price


class UsagePrice(db.Model):
    type = db.ForeignKey(UsageType, verbose_name=_("type"))
    price = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("price"),
    )
    start = db.DateField()
    end = db.DateField()

    class Meta:
        verbose_name = _("usage price")
        verbose_name_plural = _("usage prices")
        unique_together = [
            ('start', 'type'),
            ('end', 'type'),
        ]
        ordering = ('type', 'start')

    def __unicode__(self):
        return '{} ({}-{})'.format(self.type, self.start, self.end)


class DailyUsage(db.Model):
    date = db.DateField()
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
    type = db.ForeignKey(UsageType, verbose_name=_("type"))

    class Meta:
        verbose_name = _("daily usage")
        verbose_name_plural = _("daily usages")
        unique_together = ('date', 'pricing_device', 'type')
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


class SplunkName(db.Model):
    splunk_name = db.CharField(
        verbose_name=_("Splunk name"),
        max_length=255,
        blank=False,
        unique=True,
    )
    pricing_device = db.ForeignKey(
        Device,
        verbose_name=_("pricing device"),
        null=True,
        blank=True,
        default=None,
        on_delete=db.SET_NULL,
    )

    class Meta:
        unique_together = ("splunk_name", "pricing_device")
