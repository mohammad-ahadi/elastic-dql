from djangoql.exceptions import DjangoQLError


class ElasticDjangoQLError(DjangoQLError):
    pass


class SchemaError(ElasticDjangoQLError):
    pass


class FieldError(ElasticDjangoQLError):
    pass


class ConfigError(ElasticDjangoQLError):
    pass


class IndexNotSpecified(ElasticDjangoQLError):
    pass
