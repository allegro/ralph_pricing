# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from ralph.util import plugin, api_pricing
from ralph_pricing.plugins import virtual, devices, cores


@plugin.register(chain='pricing', requires=['never run'])
def import_devices(**kwargs):
    """
        Imports devices, virtual usages and cores.
    """
    today = kwargs['today']
    end = datetime.date(2013, 3, 30)  # XXX Make it configurable!
    virtual_usages = virtual.get_usages()
    cores_usage = cores.get_usage()
    for data in api_pricing.devices_history(today, end):
        date = data['date']
        devices.update_device(data, date)
        if data['is_virtual']:
            virtual.update(data, virtual_usages, date)
        else:
            cores.update_cores(data, cores_usage, date)
