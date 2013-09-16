Introduction
************

The Pricing module for Ralph is supposed to replace the parts of Ralph that
deal with money. Its main function is to generate reports telling how much of
different resources were used by particular ventures, and how much it costs.

This is achieved by collecting data about the resource use from multiple
services (using the pricing plugins) every day, storing them in the database
and then aggregating in those reports.

There are three categories of costs:

* assets -- the physical stuff that costs money, because it is getting deprecated,
* usages -- those reflect the resources being used, such as disk space, electricity, data center space,
* extra -- things that are not physical, but don't depend on how much they are being used, such as various licenses.


Assets
======

The information about asset price, parts and deprecation rate is taken from the
Ralph Assets module.  The information about which venture owns an asset is
taken from Ralph itself. All this is recorder daily, so that it can be used
later to generate the reports.

The actual costs of the assets are based on their price and their deprecation
rates (assets that are already deprecated have cost of 0).

There is a special case for counting the costs of blade servers and blade
systems -- the cost of every blade server is increased by a fraction of the
cost of the blade system in which it is installed -- so that a fully used blade
system is paid for by the blade servers.

Usages
======

The information about the use of resources is downloaded by particular plugins. At the moment this includes:

* OpenStack CPU, memory, disk, volume and image hours,
* Hamster capacity,
* Splunk volume,
* ScaleMe events,
* Disk shares,
* Physical CPU cores,
* Virtual server CPU, memory and disk.

I addition to the usage data, each of those resources can have a price
configured in the Pricing module configuration.
All usage prices have time ranges -- because they are expected to change over
time. When a price changes, a new time range with a new price should be
entered, instead of changing the already entered prices.

The usages can optionally have columns with data showing the proportion of
total usage (this is controlled by the "Show percentage of value" and "Show
percentage of price" checkboxes).

There are two ways the usages can be aggregated, depending on their
configuration. The usages that have the "Average the values over multiple days"
checkbox checked are averaged over the time span of the report. That includes
resources such as CPU cores, disk shares, virtual server resources. The usages
that don't have this checkbox checked are simply added. That includes OpenStack
hours and ScaleMe events.

The usages can be associated with assets or directly with the ventures.

Extra costs
===========

Extra costs represent things that don't fit in the asset or resource category,
but still have to be counted. They are associated directly with ventures, and have type, daily price and a time span.

As with usage prices, every time an extra cost changes, a new entry with a new
time span should be entered.

Extra costs are just summed directly for every venture and every day.
