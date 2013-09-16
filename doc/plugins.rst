Plugins
=======

Ralph Pricing uses a number of plugins to pull in data from various sources.
Some of those plugins require additional configuration.

Ventures
~~~~~~~~

Retrieves the list of all ventures from Ralph's database. Doesn't require any
configuration.


Devices
~~~~~~~

This plugin communicates with Ralph's device database in order to determine
what devices there are, to which ventures they belong, what types they have
and, if they are blade servers, to what blade systems they are connected.

This plugin doesn't require any configuration.


Assets
~~~~~~

This plugin retrieves the list of assets for devices from Ralph Assets, and
connects them with the right devices from Ralph's database. It retrieves
information such as prices, deprecation rate, etc.

This plugin doesn't require any configuration.


Assets Part
~~~~~~~~~~~

This plugin retrieves the list of assets for those devices, that has been split
into parts. Every part has its own price, deprecation rate, etc.

This plugin doesn't require any configuration.

Cores
~~~~~

This plugin retrieves the counts of physical CPU cores installed in the
devices. No configuration is necessary.


Shares
~~~~~~

This plugin retrieves the information about network and disk shares used by
the particular devices. It requires no configuration.

Virtual
~~~~~~~

This plugin retrieves the data on virtual systems usage, in particular it pulls
in from Ralph the information on the number of virtual CPU cores and the amount
of RAM memory and disk space used by the virtual servers. No configuration is
necessary.


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

to pull in the billing information for OpenStack tenants.
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
