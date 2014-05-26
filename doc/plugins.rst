=======
Plugins
=======

There are two type of plugins. One of them is use to collect data from remote applications or servers, second type named report is use to present the results on the report. 

The main goal of plugins idea is create universal and configurable logic for each new service and handle non-standard cases where collect or/and report plugin contains more complicated logic and cannot by handle by universal plugin. For example, if there is not possibility to push usages data to scrooge, you can go to scrooge administrators and try to negotiate write collects plugin for your. This way is very very not recommended but it is possible (prefer use push API). Second situation is when your service require pre-processing befor display results or contains really complicated logic also, you can go to scrooge administrators and ask him for help with create own plugin and again you can try to negotiate write report plugin for you. Recommended is use universal plugin and adjust your account logic to scrooge logic model.

Plugins use queues, every plugin befor run is placed on the queue and wait for its turn.

Collect plugins
~~~~~~~~~~~~~~~

.. image:: images/collects_data_plugins.png

Collects plugins are using to collect data from remote sources. Exactly, collect plugins are using for collect base usages. Collect service usages is inadvisable so, create plugin for service usages is finality.

Each plugin is running, for example, on 9 AM o'clock and collect data from all day. There is no base plugin or something like that. Each collect plugins contains custom logic and result of plugin work is add/update data in scrooge database.

Report plugins
~~~~~~~~~~~~~~

.. image:: images/report_plugins.png

Report plugins are using to generate columns on report. Each plugin must return 2 informations, column schema and column value pre venture. This is most important becouse column schema is use to define and create additional columns on report but column value fill this columns for each venture. When venture have no value for any column 0.0 will be set as default. For default cases was created universal plugin so, each service can use this plugins when:

1. Service was created
2. All usage types for this service was defined
3. Service contains usage types
4. Service contains percen for each choosen usage. (100 when only 1 usage)
5. Service contains base usages selected
6. Service contains assigned ventures
7. For each day was provided usages

Service and usages are configurable parts so, its can be choose from scrooge admin panel. More about 'how to' you can find in Services & usages section.

Report plugins for calculate cost of service require cost of base usages. Base usages without costs are exclude from total base cost of service so, data from raport will incorrect. More about cost in cost & extra costs section.
