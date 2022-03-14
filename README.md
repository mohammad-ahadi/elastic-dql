Elastic-dql
========


Advanced search language for Django and elasticsearch based on DjangoQL project.

DjangoQL is a library that provides search language that works with django orm. elastic-dql extends DjangoQL project to
generate elasticsearch queries.<br><br>
elastic-dql suppports logical operators and parenthesis.It also provides to apis to get index mappings and value
suggestions for keyword fields.


Contents
--------

* `Installation`_
* `Generating Elasticsearch Queries`_
* `Custom SchemaFactory`_
* `Mappings and Suggestions (auto-complete) api`_
* `Features`_
* `TODO Tasks`_
* `DjangoQL project`_
* `Language reference`_
* `License`_

Installation
------------

```shell
$ pip install elastic-dql
```

Add ``'elastic_dql'`` to ``INSTALLED_APPS`` in your ``settings.py``:

```python

INSTALLED_APPS = [
    ...
    'elastic_dql',
    ...
]
```

Add ``ELASTIC_DQL`` section in ``settings.py``:

```python
ELASTIC_DQL = {
  "schema_factory": "elastic_dql.schema.SchemaFactory",
  "default_schema": "elastic_dql.schema.ElasticDjangoQlSchema",
  "default_index": None,
  "accept_index_param": True,  # if False default_index should be specified
  "connection": {
    "hosts": ["http://localhost"],
  }
}
```
this values are default configs.if you have just one elasticsearch index you better set a default index otherwise you
should pass ``index`` parameter in ``mappings`` and ``suggestions``  apis.

Generating Elasticsearch Queries
--------------------------------

to create elasticsearch queries you should follow these lines:

```python
from elastic_dql.query import get_query
index_name = "your_elasticsearch_index"
query = 'name = "mohammad" and age = 10'
elastic_query = get_query(index_name, query)
```

Custom SchemaFactory
--------------------

SchemaFactory handles limits to access elasticsearch.by default elastic-dql uses ``elastic_dql.schema.SchemaFactory``
and allows to access to all indexes and fields.

To make some limits at first you should create custom SchemaFactory:

```python
from elastic_dql.schema import SchemaFactory

class CustomSchemaFactory(SchemaFactory):
    include_indices = ('*',)
    exclude_indices = ()
    index_field_limits = {
        "some-index": ["password_field","other_limited_field"]
    }
```

after implementing ``CustomSchemaFactory`` add the class path to ``settings.py``:
```python
ELASTIC_DQL = {
  "schema_factory": "path.to.CustomSchemaFactory",
  ...
}
```

> :warning: **you must either fill include_indices or exclude_indices not both**

Mappings and Suggestions (auto-complete) api
--------------------------------------------

``Mappings api`` : provides field mappings of index (default_index or get from url parameters)

``Suggestions api`` : provides field value suggestion for ``Keyword`` fields.can use for auto-complete.

To use this apis you must add elastic_dql urls:

```python

from elastic_dql.urls import get_urls

urlpatterns = [
              ...
          ] + get_urls()
```

OR

```python

from django.urls import include

urlpatterns = [
    ...
    include("elastic_dql.urls"),
    ...
]
```

```shell
$ curl localhost:8000/mappings?index=your_index
```

> :warning: **if use default_index, index parameter will be skipped**


```shell
$ curl localhost:8000/suggestions/some_keyword_field?index=your_index&search=values_must_contains_this
```

> :warning: **search is optional - if use default_index, index parameter will be skipped**


Features
--------

- index and field limiting with ``SchemaFactory`` Customization
- mappings and suggestions apis

TODO Tasks
----------

- add pagination to suggestions api
- make library compatible with elastic-dsl query generator
- add async for elasticsearch communications
- cache field mappings and invalidate it with user defined duration
- compatibility test with some elasticsearch (python lib) versions
- handle all elasticsearch fields now it supports (long,unsigned_long,text,keyword,float,int,date,boolean)

DjangoQL project
------------------

DjangoQL github page:

`DjangoQL <https://github.com/ivelum/djangoql>`_


Language reference
------------------

The query language is as same as djangoql query language

`Language refrence <https://github.com/ivelum/djangoql#language-reference>`_

License
-------

MIT
