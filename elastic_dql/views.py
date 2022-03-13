import json

from django.http import HttpResponse
from django.views.generic.base import View

from .config import get_dql_config
from .exceptions import IndexNotSpecified, SchemaError
from .schema import get_schema_instance
from .serializers import serialize_mappings


class BaseAPIView(View):
    def _get_index(self, request):
        dql_config = get_dql_config()
        accept_param = dql_config.accept_index_param
        index = request.GET.get("index") if accept_param else dql_config.default_index
        if not index:
            raise IndexNotSpecified("index not specified")
        return index

    def _error(self, message, status_code=400):
        return HttpResponse(
            content=json.dumps({"error": message}, indent=2),
            content_type='application/json; charset=utf-8',
            status=status_code
        )


class MappingsAPIView(BaseAPIView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        try:
            index = self._get_index(request)
            schema_instance = get_schema_instance(index)
            mappings = schema_instance.get_mappings()
            serialized_mappings = serialize_mappings(mappings)
        except (SchemaError, IndexNotSpecified) as exception:
            return self._error(str(exception))
        return HttpResponse(
            content=json.dumps(serialized_mappings, indent=2),
            content_type='application/json; charset=utf-8',
        )


class SuggestionsAPIView(BaseAPIView):
    http_method_names = ['get']

    def get(self, request, field, *args, **kwargs):
        # TODO: add pagination
        try:
            index = self._get_index(request)
            schema_instance = get_schema_instance(index)
            search = request.GET.get("search")
            suggestions = schema_instance.suggestions(field, search=search)
        except (SchemaError, IndexNotSpecified) as exception:
            return self._error(message=str(exception))
        return HttpResponse(
            content=json.dumps(suggestions, indent=2),
            content_type='application/json; charset=utf-8',
        )
