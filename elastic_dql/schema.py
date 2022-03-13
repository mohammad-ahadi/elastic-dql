from django.utils.module_loading import import_string
from djangoql.ast import Name
from elasticsearch import Elasticsearch

from elastic_dql.serializers import serialize_suggestions_values_response
from .config import get_dql_config
from .exceptions import SchemaError
from .field import FieldMapper
from .utils import build_field_name_from_parts


class SchemaFactory(object):
    instance = None
    include_indices = ('*',)
    exclude_indices = ()
    index_field_limits = {}

    @classmethod
    def get_instance(cls):
        """
            Get one instance of schema foctory.(singleton pattern)
            it is class method because this class can be inherited
        :return:
        """
        if not cls.instance:
            cls.instance = cls()
        return cls.instance

    def __init__(self):
        if self.include_indices and self.exclude_indices:
            raise SchemaError(
                'Either include_indices or exclude_indices can be specified, but not both',
            )
        if not (self.include_indices or self.exclude_indices):
            raise SchemaError(
                'One of include_indices or exclude_indices must be specified',
            )
        self.per_index_instance = {}

    def get_schema_instance(self, schema_cls, index):
        if self.excluded(index):
            raise SchemaError(
                "%s can't be used with %s index because it's excluded from it" % (
                    index,
                    self.__class__,
                ),
            )
        try:
            schema_instance = self.per_index_instance.get(index, None)
            if not schema_instance or isinstance(schema_instance, schema_cls):
                schema_instance = self._create_schema_instance(schema_cls, index)
        except Exception as exception:
            raise SchemaError(str(exception))
        return schema_instance

    def excluded(self, index):
        if self.include_indices:
            excluded = ("*" not in self.include_indices) and (index not in self.include_indices)
        else:
            excluded = index in self.exclude_indices
        return excluded

    def _create_schema_instance(self, schema_cls, index):
        fields_limit = self.index_field_limits.get(index, [])
        client = self._create_elastic_connection()
        schema_instance = schema_cls(client, index, fields_limit=fields_limit)
        self.per_index_instance[index] = schema_instance
        return schema_instance

    def _create_elastic_connection(self):
        dql_config = get_dql_config()
        elastic_connection = Elasticsearch(**dql_config.elastic_connection_params)
        return elastic_connection


class AbstractElasticDjangoQlSchema(object):
    pass


class ElasticDjangoQlSchema(AbstractElasticDjangoQlSchema):

    def __init__(self, client, index, fields_limit=None):
        self.client = client
        self.index = index
        self.fields_limit = fields_limit if fields_limit else []
        self.valid_properties_dict = {}

    def get_mappings(self):
        try:
            result = self.client.indices.get_mapping(index=self.index)
            mappings = result[self.index]["mappings"]
        except Exception as e:
            raise SchemaError(str(e))
        valid_properties = self._cache_properties(mappings)
        return valid_properties

    def suggestions(self, field_name, search=None):
        field = self.resolve_name(field_name)
        if not field:
            raise SchemaError("%s is not a valid field_name" % field_name)
        if not field.can_suggest_values():
            raise SchemaError("field %s hasn't type keyword" % field_name)
        query, aggregations = self._get_suggestions_query(field.name, search)
        try:
            result = self.client.search(index=self.index, query=query, aggregations=aggregations)
        except Exception as exception:
            raise SchemaError(str(exception))
        final_result = serialize_suggestions_values_response(result)
        return final_result

    def resolve_name(self, field_name):
        if isinstance(field_name, Name):
            field_name = build_field_name_from_parts(field_name.parts)
        return self._resolve_name_str(field_name)

    def _resolve_name_str(self, field_name):
        if not self.valid_properties_dict:
            self.get_mappings()
        field = self.valid_properties_dict.get(field_name)
        if not field:
            raise SchemaError("invalid field_name: %s" % field_name)
        return field

    def _cache_properties(self, properties):
        field_mapper = FieldMapper()
        must_be_limited_field_name = set(self.fields_limit)
        all_fields = field_mapper.get_properties(properties)
        valid_properties = list(filter(lambda field: field.name not in must_be_limited_field_name, all_fields))
        self.valid_properties_dict = {field.name: field for field in valid_properties}
        return valid_properties

    def _get_suggestions_query(self, field_name, search):
        # TODO: seprate query building from schema
        query = {
            "exists": {
                "field": field_name
            }
        }
        if search:
            query["wildcard"] = {
                field_name: {
                    "value": "*" + search + "*"
                }
            }
        aggregations = {
            "values": {
                "terms": {"field": field_name}
            }}
        return query, aggregations

    def validate(self, ast):
        pass


class SchemaHandler:
    schema_factory = None
    schema_cls = None
    initiated = False

    @staticmethod
    def initiate():
        dql_config = get_dql_config()
        if not SchemaHandler.initiated:
            schema_factory_cls = import_string(dql_config.schema_factory_path)
            SchemaHandler.schema_factory = schema_factory_cls.get_instance()
            SchemaHandler.schema_cls = import_string(dql_config.default_schema_path)
            SchemaHandler.initiated = True
        return SchemaHandler.schema_factory, SchemaHandler.schema_cls


def get_schema_instance(index):
    schema_factory, schema_cls = SchemaHandler().initiate()
    schema_instance = schema_factory.get_schema_instance(schema_cls, index)
    return schema_instance
