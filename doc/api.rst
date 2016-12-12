========
REST API
========

Scrooge provides public REST API described by OpenAPI_-compliant
schema, which is available for consumption by external
programs/clients at ``/scrooge/api/schema.json``.

On top of this schema, we provide swagger-ui_ , which is available at
``/scrooge/api`` or ``/api`` endpoint (the latter just redirects to
the former). It serves both as documentation and convenience tool,
that is meant to facilitate human interaction with our API and improve
its discoverability.


Notes for Scrooge developers/administrators
===========================================

API schema is defined in file pointed by ``API_SCHEMA_FILE`` setting (by default
``ralph_scrooge.media.api_schema.yaml``). This file, in YAML format is meant for
editing and feeding ``swagger-ui`` during development. For production though,
you should generate a JSON file from it. There's a management command ``scrooge
generate_json_schema``, which is meant exactly for that. So basically, YAML file
is a source file, while JSON should be seen as kind of artifact, which is not
meant to be edited directly (it is minified BTW), and shouldn't be kept in
Scrooge's repo.

There is one important setting related to API schema - ``SCROOGE_HOST`` - which
should be filled if you want to provide Scrooge's REST API schema to your
clients (and swagger-ui is one of them) - see the comment in
``ralph_scrooge.settings.base`` for additional info on this.


.. _OpenAPI: https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md

.. _swagger-ui: https://github.com/swagger-api/swagger-ui
