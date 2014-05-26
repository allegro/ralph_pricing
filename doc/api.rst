===
API
===
For improve work and communication with scrooge we prepared api. Currently, there is only push api implemented and can be used to push usages data by services. In the future we are planning create pull api for get report data only for single venture/service. For communicate with API we use JSON as a message format and REST API for maintenance of communication standards.

Push API
~~~~~~~~

.. image:: images/push_api.png

Each service is obligate push usages data to scrooge. Before you start using push api, first you need to create service and usages manually. When you have created service and usages then you can start push to scrooge using api. http://127.0.0.1:8000/scrooge/api/v0.9/serviceusages/ this is address for pushing data, current api version is 'v0.9'. The best way to provide data for Scrooge is pushing it every day, but data can also be pushed for specified date.

**JSON FORMAT**

::

    {
        "service": "<service_symbol>",
        "date": "<date>",
        "venture_usages": [
            {
                "venture": "<venture_symbol>",
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

**JSON EXAMPLE**

::

    {
        "service": "service_symbol",
        "date": "2111-11-11",
        "venture_usages": [
            {
                "venture": "venture1",
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
                "venture": "venture2",
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
                "venture": "venture3",
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

Pull API
~~~~~~~~

Coming soon...
