===
API
===
To improve work and communication with Scrooge, we have prepared the API. Currently, there is only push API which can be used to push usages of data by different services. In the future, we are planning to create pull API for example to generate report data. To communicate with API, use JSON as a message format and REST API for maintenance of communication standards.


Push API
~~~~~~~~

.. image:: images/push_api.png

-------------------
General description
-------------------

Every pricing service [#]_ can upload data to Scrooge with the use of its resources
(e.g. requests count, transfer, etc.) by services. To upload data to Scrooge, some preconditions must be satisfied:

* usage type(s) used by service must be added to Scrooge
* service has to be added to Scrooge (usually synchronized from Ralph)
* pricing service has to be added to Scrooge
* usage type(s) must be connected with the pricing service

A unique symbol has to be provided for every usage type in Scrooge, which is later used to identify it in request processing.

The unit of resource usage doesn't matter (e.g. in the case of transferring kB, MB, GB) - the most important thing is to keep the unit of every usage the same (even abstract) – after all, the cost of service is distributed to other services proportionally to their usages (of resources).

If the pricing service has more than one usage type, it is necessary to provide their percentage division in the period of time (e.g. transfer – 30%, requests count – 70%, which means that 30% of the total cost of pricing service is distributed proportionally to the transfer usage and 70% proportionally to the requests count).


-------------------------
User Guide (step-by-step)
-------------------------
.. _user-api-label:

1. (General) Ralph Admin part

  a. Create a user or use the account that is already provided for your service.
  b. Log in to Ralph using technical user credentials and find out what your API Key is (RALPH_URL/user/preferences/api_key)

2. Scrooge Admin part

  a. Create Usage Type(s) (one or more) that reflect(s) resources used by pricing service (``RALPH_URL/admin/ralph_scrooge/usagetype/add/``). Every service usage type must have a unique symbol.

    * Leave "Show usage type in report" checked.
    * Type: select "Service usage type".

  b. Create Pricing Service (``RALPH_URL/admin/ralph_scrooge/pricingservice/add/``). Possible options for pricing service:

    * Plugin type – use ``universal``, if pricing service costs should be allocated proportionally to usage types (total real cost of pricing service will be divided into other services). Use ``fixed price`` if you'll provide price for every unit of usage type used by this pricing service (like AWS billing, where you are charged fixed price by every hour of working instance; notice that sum of this cost could be different than real pricing service cost).
    * Services – select services which total cost will be summed up to pricing service cost (usually it should be 1:1 mapping)
    * Service usage types – select usage type(s) created in the previous step. Notice that only usage types with the “Service usage type” are presented here. If you only have one usage type for your service, select it and type 100 in its percentage field.


3. API usage

  Send a JSON message to API endpoint (``RALPH_URL/scrooge/api/v0.9/pricingserviceusages/``) using POST method with data in the format described in the “Technical description” section.


.. _technical-label:

---------------------
Technical description
---------------------

""""""""""""""
API definition
""""""""""""""
::

  {
    "pricing_service": "<pricing service name or id>",
    "date": "<date>",
    "overwrite: "no|values_only|delete_all_previous",
    "usages": [
        {
            "service": "<service name or uid or id>",
            "pricing_object": "<pricing_object_name>",
            "usages": [
                {
                    "symbol": "<usage_type_1_symbol>",
                    "value": <usage1>
                },
                ...
            ]
        },
        ...
    ]
  }


Notice that you could either provide charged service here (it will be charged directly) or pricing object (ex. hostname or IP address) - the service (assigned to this pricing object) will be charged implicitly here.


Example::

  {
      "pricing_service": "pricing_service1",
      "date": "2013-10-10",
      "usages": [
          {
              "service": "service1",
              "environment": "env1",
              "usages": [
                  {
                      "symbol": "requests",
                      "value": 123
                  },
                  {
                      "symbol": "transfer",
                      "value": 321
                  }
              ]
          },
          {
              "pricing_object": "pricing_object1",
              "usages": [
                  {
                      "symbol": "requests",
                      "value": 543
                  },
                  {
                      "symbol": "transfer",
                      "value": 565
                  }
              ]
          },
          {
              "service_id": 123,
              "environment": "env2",
              "usages": [
                  {
                      "symbol": "requests",
                      "value": 788
                  },
                  {
                      "symbol": "transfer",
                      "value": 234
                  }
              ]
          },
          {
              "service_uid": "sc-123",
              "environment": "env2",
              "usages": [
                  {
                      "symbol": "requests",
                      "value": 788
                  },
                  {
                      "symbol": "transfer",
                      "value": 234
                  }
              ]
          }
      ]
  }

"""""""""""""
Communication
"""""""""""""

Communication with Scrooge API takes place using the HTTP protocol. Data should be sent with the POST request. Authentication is done using HTTP header "Authorization: ApiKey <username>:<api_key>", where api_key is a key generated to a user in Ralph (see *Ralph Admin part*).

"""""""""""""""""""""""""""
Overwriting previous values
"""""""""""""""""""""""""""

API provides a way to define how to treat previous service usages values uploaded for a given date (e.g. when data is sent twice for a given date). The possible actions (overwrite) are:

* ``delete_all_previous`` - all previous usages for a given date are removed before inserting new data

* ``values_only`` - previously uploaded usages are overwritten by new values

* ``no`` - any usage is removed - new usages are appended to the old ones

Example: first data package is (A:1, B:2), the next one is (B:3, C:4) - final data will be as follows:

* ``delete_all_previous`` - (B:3, C:4)
* ``values_only`` (default) - (A:1, B:3, C:4)
* ``no`` - (A:1, B:2, B:3, C:4) (cumulatively: B:5)

Default action (when overwrite is not passed) is `no`.

"""""""""""""""""""""""""""""""
Possible responses (HTTP codes)
"""""""""""""""""""""""""""""""

201 - everything ok, data saved properly.

400 - invalid symbol or name (ex. usage type or service) - there will be provided detailed information about invalid data.

401 - authorization/authentication error.

500 - error on server side during data processing.


Pull API
~~~~~~~~

You could validate if your usages are properly saved calling ``<pricing_service_name>/<date(YYYY-MM-DD)>`` endpoint of Scrooge API (``RALPH_URL/scrooge/api/v0.9/pricingserviceusages/<pricing_service_name>/<date(YYYY-MM-DD)>``) with GET method.


.. [#] Pricing Service is financial extension to regular service. It contains information about methods of service costs allocation, services excluded from charging etc.
