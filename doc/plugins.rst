=======
Plugins
=======

There are two types of plugins. One of them is use to collect data from remote applications or servers and second plugins named report is use to present the results in report form. The main goal of plugins idea is create universal and configurable logic for each new service and handle non-standard cases where collect or/and report plugin must be more complicated and cannot by handle by universal plugin. For example, if you have not possibility to push usages data to scrooge, you can go to scrooge administrators and try to negotiate write collects plugin for your. This way is very very not recommended but it is possible. Second situation is when your service require pre-processing befor display results or do really complicated logic you can go to scrooge administrators and ask for help how to create own plugin again try to negotiate write report plugin for your. Recommended is use universal plugin and adjust your account logic to scrooge model. Plugins use queues, every plugin befor run is placed on the queue and wait for its turn.

Collect plugins
~~~~~~~~~~~~~~~

.. image:: images/collects_data_plugins.png

Report plugins
~~~~~~~~~~~~~~

Comming soon...
