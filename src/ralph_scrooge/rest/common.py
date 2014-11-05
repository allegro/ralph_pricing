#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import calendar
from datetime import date, timedelta


def get_dates(year, month):
    year = int(year)
    month = int(month)
    days_in_month = calendar.monthrange(year, month)[1]
    first_day = date(year, month, 1)
    last_day = first_day + timedelta(days=days_in_month-1)
    return (first_day, last_day, days_in_month)
