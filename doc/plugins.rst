Plugins
===========

Openstack
~~~~~~~~~

Plugin dependencies
*******************

- ventures

Description
***********

If you configure the variables ``OPENSTACK_URL``, ``OPENSTACK_USER`` and
``OPENSTACK_PASSWORD`` to point to the nova API of your OpenStack instance, and
add venture name in description tenant in format ``venture:venture_name;``,
then you can use the command::

    (ralph)$ ralph pricing_sync --run-only=openstack

to pull in the billing information for OpenStack tennants.
OpenStack plugin save five usages:

- CPU Hours,
- Disk GiB Hours,
- Images GiB hours,
- Memory GiB Hours,
- Volume GiB Hours,


Splunk
~~~~~~

Plugin dependencies
*******************

- ventures
- devices

Description
***********
If you configure ``SPLUNK_URL``, ``SPLUNK_USER`` and ``SPLUNK_PASSWORD``, then
you can use the command::

    (ralph)$ ralph pricing_sync --run-only=splunk

to download usage information about all the hosts from Splunk. Plugin save a ``Volume 1 MB`` usage.
