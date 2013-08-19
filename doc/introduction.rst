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
