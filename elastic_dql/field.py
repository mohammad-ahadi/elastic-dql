from datetime import datetime

from djangoql.compat import text_type

from .exceptions import FieldError
from .query_generator import QueryBuilderFactory
from .utils import dot_join


class ElasticDjangoQlField(object):
    name = None
    nullable = False
    field_type = None
    elastic_field_type = ""
    value_types = []
    valid_operators = (
        '=', '>', '>=', '<', '<=', '~', 'in', 'startswith', 'endswith', '!=', '!~', 'not in', 'not startswith',
        'not endswith')
    value_types_description = ''

    def __init__(self, name, nullable=False, field_type=None, elastic_field_type=None):
        self.name = name
        self.nullable = nullable
        self.elastic_field_type = elastic_field_type
        if field_type is not None:
            self.field_type = field_type

    def get_lookup_name(self):
        return self.name

    def get_lookup(self, path, operator, value):
        # field_name = '.'.join(path + [self.get_lookup_name()])
        field_name = self.get_lookup_name()
        if operator not in self.valid_operators:
            raise FieldError("operator %s is not valid for this type" % operator)
        formatted_value = self.format_value(value)
        query_builder_factory = QueryBuilderFactory()
        query_builder = query_builder_factory.get_query_builder(operator)
        query, invert = query_builder.generate(field_name, formatted_value)
        return query, invert

    def format_value(self, value):
        """
        override this method to clean value or change type, ...

        :param value:
        :return: formatted_value:
            formatted_value:
        """
        return self.field_type(value)

    def validate(self, value):
        if not self.nullable and value is None:
            raise FieldError(
                'Field %s is not nullable, '
                "can't compare it to None" % self.name,
            )
        if value is not None and type(value) not in self.value_types:
            if self.nullable:
                msg = (
                    'Field "{field}" has "nullable {field_type}" type. '
                    'It can be compared to {possible_values} or None, '
                    'but not to {value}'
                )
            else:
                msg = (
                    'Field "{field}" has "{field_type}" type. It can '
                    'be compared to {possible_values}, '
                    'but not to {value}'
                )
            raise FieldError(msg.format(
                field=self.name,
                field_type=self.field_type,
                possible_values=self.value_types_description,
                value=repr(value),
            ))

    def can_suggest_values(self):
        return False


class LongField(ElasticDjangoQlField):
    value_types = [int, float]
    field_type = int
    value_types_description = "numeric fields"


class FloatField(ElasticDjangoQlField):
    value_types = [int, float]
    field_type = float
    value_types_description = "numeric fields"


class TextType(ElasticDjangoQlField):
    value_types = [text_type]
    field_type = text_type
    value_types_description = "strings"


class DateField(ElasticDjangoQlField):
    value_types = [text_type]
    field_type = text_type
    value_types_description = 'dates in "YYYY-MM-DD" format'

    def validate(self, value):
        super(DateField, self).validate(value)
        try:
            datetime.strptime(value, '%Y-%m-%d').date()
        except:
            raise FieldError()
    # TODO: time format checking
    # pass


class BoolField(ElasticDjangoQlField):
    value_types = [bool]
    field_type = bool
    value_types_description = "booleans"


class KeywordField(ElasticDjangoQlField):
    value_types = [text_type]
    field_type = text_type

    def __init__(self, name, parent, *args, **kwargs):
        super(KeywordField, self).__init__(name, *args, **kwargs)
        self.parent = parent

    def can_suggest_values(self):
        return True


class FieldMapper(object):
    type_mapping = {
        "date": DateField,
        "keyword": KeywordField,
        "boolean": BoolField,
        "long": LongField,
        "text": TextType,
        "float": FloatField,
        "unsigned_long": LongField
    }

    def get_fields(self, fields_dict: dict, parent: ElasticDjangoQlField):
        fields = []
        for field_name, data in fields_dict.items():
            field_cls = self._get_field_cls(data["type"])
            field_name = dot_join(parent.name, field_name)
            field = field_cls(field_name, parent=parent, elastic_field_type=data["type"])
            fields.append(field)
        return fields

    def get_properties(self, mappings, base_name=None):
        result = []
        if not mappings:
            return result
        properties = mappings.get("properties")
        if properties:
            for property_name, property_data in properties.items():
                prefix = dot_join(base_name, property_name) if base_name else property_name
                props = self.get_properties(property_data, base_name=prefix)
                result.extend(props)
            return result
        field_type = mappings.get("type")
        if field_type:
            field_cls = self._get_field_cls(field_type)
            field = field_cls(base_name, elastic_field_type=field_type)
            result.append(field)
            fields_property = mappings.get("fields")
            if fields_property:
                fields = self.get_fields(fields_property, field)
                result.extend(fields)
        return result

    def _get_field_cls(self, property_type):
        field_cls = self.type_mapping.get(property_type)
        if not field_cls:
            raise FieldError("invalid field type: %s" % property_type)
        return field_cls
