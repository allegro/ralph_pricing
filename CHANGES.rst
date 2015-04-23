Change Log
----------

3.0.1
~~~~~

Released on April 23, 2015

* Added versioning to static files.
* Added database and Virtual IP as default components.
* Change default settings for collect plugins.
* Fixes:
    * Unification of menu items in angular views and old django views.
    * Removed unnecessary 'Extra costs' and 'Usage types' menu items.


3.0.0
~~~~~

Released on April 13, 2015

* Project name changed from Ralph Pricing to Ralph Scrooge

* Redesigned architecure comparing to (old) ralph_pricing
    * Calculation based on services and environments instead of ventures
    * Base PricingObject model to simplify adding new types of chared objects (ex. Database, Virtual server, Tenant)
    * Costs are (re)calculated and stored in database
    * Many performance improvements

* New client GUI written in AngularJS
    * Components: preview of historical objects (server, virtual, database etc) per service for single day
    * Costs card: summary of service costs in single month
    * Allocations: add service or team specific costs and manage it's distribution to other services
    * Costs: detailed costs for each pricing object

* New charging types:
    * Dynamic extra costs: specify cost (like Extra cost) and a dynamic way of it's distribution (ex. cores count)

* New collect plugins:
    * Collecting Database, VIP, Tenant info from Ralph
    * OpenStack SimpleUsage plugin
    * OpenStack Ceilometer MongoDB plugin
    * Support plugins (from Ralph Assets)

* New permissions:
    * Every (active) Ralph user has access to client part (components, allocation, cost card) for services which he owns
    * Admin (ralph_scrooge group) has access to whole system


2.7.0
~~~~~

* Adjusted ralph_pricing to work in parallel with ralph_scrooge


2.6.0
~~~~~

* Added regular usages to service
* Rounding value on report
* Added yeasterday flag to pricing_sync
* Added new extracost model


2.5.4
~~~~~

* Fixed team average with ventures subset


2.5.3
~~~~~

* Added exclude ventures for base usages
* Added ventures filter and forecast price to ceilometer report plugin
* Changed profit center field length from 75 to 255


2.5.2
~~~~~

* Logs compatible with python 2.7.3


2.5.1
~~~~~

* Improved services usages api logging

* Fixed fixed header scroll in reports

* Added DirectoryTimedRotatingFileHandler

* Removed sentry workaround

* Improved default loggers and config

* Separated unknown ventures for shares groups


2.5.0
~~~~~

* Fixed decimal precision in tests

* Remove back collecting disk share mount

* Fixed report error log text

* Added average team billing model

* Added share multiple groups

* Added san collect plugin

* Added exclude ventures to teams

* Added required permisions to view scrooge

* Renamed package to ralph_scrooge

* Added coverals

* Fixed venture hierarchy, when venture have no parent then venture parent is None

* Added html documentation


2.4.0
~~~~~

* New devices report

* Devices ventures changes report

* New ceilometer report plugin logic and logging tweakups

* Fixed asset collect plugin (replacing to None)

* Ceilometer collect plugin bugfixes

* Added venture tree rebuild when venture plugin job is finished

* Fixed extra costs - add more than 5 rows (with dynamic adding)

* Fixed header in csv statement

* Improved gitignore and manifest

* When venture have no parent set venture parent as none


2.3.0
~~~~~

* Fixed report table header on scroll.

* Exception instan error in logging on report plugin run.

* Fixed raise exception 0/0 by team plugins.

* Added extra costs to report as separated column and service to total cost.

* Fixed saving device_id, sn and barcode

* Added monthly statement

* Added plugin to bill cloud 1.0 from ralph

* Fixed ventures daily usages header colspan


2.2.3
~~~~~

* nfdump get only ips from given network.

* Changed logging to logger in network plugin.

* Only usage types wtih is_manually_type flag are show in menu.

* Fixed calculating price. Massage incomplete_price was incorrect sometime.

* Fixed percent rounding for teams.

* Remove PLN from fields and add it to name of column.

* Average option for usages is now available.

* Fixed is_blade. Now it is truly boolean value.

* Added overwriting in push API.

* Added ventures daily usages report.

* Fixed usages columns width.


2.2.2
~~~~~

* Fixed nfdump_str, executed command on remote server.

* Added console statistics


2.2.1
~~~~~

* Upgrade ceilometer collect plugins.

* Added ceilometer report plugin.

* Fixed overwriting configuration by pluggableaps.

* Fixed logging from collect plugins. Now, when venture does not exist log warning.

* Upgrade inserting teams usages. Added total prcent information and button to dynamically add more rows.

* Plugins indentify usages only by symbols. Name and more options are set as defaults.

* Added multiple ventures option for single virtual server usages. settings.VIRTUAL_VENTURE_NAMES must be dict where key is name of groub and value is list of ventures.

* Network cost is by providers.

* Remove teams count table and added count to usage price table.


2.2.0
~~~~~

* Displayed name changed from Ralph Pricing to Scrooge.

* Added service model and plugin for billing service depending on it's usage types, base usage types and dependent services.

* Change report plugins architecture (change from function to classes, create plugin for base usages (eg. power consumption) and dedicated plugin for depreciation).

* Added teams billing. Teams could be billed in 4 models: by time, by devices count, by devices and cores count or by cost distribution between other teams depending on other teams members count.

* Modified collects virtual plugin for getting usages for more than one virtual systems.

* Created plugin for colleting internet usages per IP address (using nfsen).

* Added height of device usage.

* Removed old AllVentures report and warehouse option from report.

* PUSH API for usages of service resources by ventures.

* New white theme.


2.1.1
~~~~~

* Added scrooge logger sentry


2.1.0
~~~~~

* Changes in the architecture. Generate report from plugins for each usage

* Create few plugins for each usage

* Distinguish two groups of plugins, reports and collections

* Rebuild generate reports view and add it as beta venture view

* New report contains separated columns for warehouses for one report

* Increased efficiency of report generation

* Fix splunk plugin

* Used pluggableapps for scrooge config

* Added more logs from logger

* Added separated logger for scrooge

* Openstack ceilometer plugin

* When usage is per warehouse then warehouse must be chosen

* Fix datepicker on report subpage

* Added flag to hide/show usages on report

* Remove TopVenture subpage


2.0.1
~~~~~

* If assets plugin cannot find device by asset_id then try get device by sn


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
