from django.conf import settings

from .exceptions import ConfigError


class ElasticDqlConfig:
    __instance = None
    schema_factory_path = None
    default_schema_path = None
    default_index = None
    accept_index_param = None
    elastic_connection_params = None

    def __init__(self, django_settings, default_settings):
        self.django_settings = django_settings
        self.defaults = default_settings
        self._configure()

    def _configure(self):
        settings = self.defaults if not self.django_settings else self.django_settings
        self.schema_factory_path = settings.get("schema_factory", self.defaults.get("schema_factory"))
        self.default_schema_path = settings.get("default_schema", self.defaults.get("default_schema"))
        self.default_index = settings.get("default_index", self.defaults.get("default_index"))
        self.accept_index_param = settings.get("accept_index_param", self.defaults.get("accept_index_param"))
        if not (self.accept_index_param or self.default_index):
            raise ConfigError("if accept_index_param is false default_index must be specified")
        self.elastic_connection_params = settings.get("connection", self.defaults.get("connection"))

    @staticmethod
    def get_config_instance(django_settings, default_settings):
        if not ElasticDqlConfig.__instance:
            ElasticDqlConfig.__instance = ElasticDqlConfig(django_settings, default_settings)
        return ElasticDqlConfig.__instance


DEFAULTS = {
    "schema_factory": "elastic_dql.schema.SchemaFactory",
    "default_schema": "elastic_dql.schema.ElasticDjangoQlSchema",
    "default_index": None,
    "accept_index_param": True,  # if false default_index should be specified
    "connection": {
        "hosts": ["http://localhost"],
    }
}


def get_dql_config():
    ELASTIC_DQL_SETTINGS_KEY = "ELASTIC_DQL"
    ELASTIC_DQL_SETTINGS = getattr(settings, ELASTIC_DQL_SETTINGS_KEY, {})
    dql_config = ElasticDqlConfig.get_config_instance(ELASTIC_DQL_SETTINGS, DEFAULTS)
    return dql_config
