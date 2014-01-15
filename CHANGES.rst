Change Log
----------

2.0.0
~~~~~

* Changes in the architecture. Now devices are taken by asset plugin from assets
* Remove device and cores plugin (This this is a role of asset plugin)
* DailyUsage contains warehouse field
* Added version of usage type price based on cost
* Added price or cost per warehouse
* Now venture reports are generated per warehouse (only colums with flag by_warehouse are different between reports)
* Added forecast prices and costs and possibility to generate forecast reports
* Added cost to price converter used by 'get_assets_count_price_cost' method


1.2.8
~~~~~
Released on December 11, 2013

* F5 devices billing added.


1.2.7
~~~~~
Released on November 03, 2013

* Added search boxes, filters and additional columns in admin.
* Fixed corner-case bug related to calculation of bladesystems costs.


1.2.6
~~~~~

Released on August 08, 2013

* Added "show only active" option in the reports
* Added short descriptions to reports templates
* Fixed assets plugin - IntegrityError protection, added new tests
* Show extra costs in the extra costs types admin


1.0.0
~~~~~

* initial release
