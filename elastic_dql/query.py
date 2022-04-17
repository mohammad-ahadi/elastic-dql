from collections import defaultdict

from djangoql.ast import Logical
from djangoql.parser import DjangoQLParser

from .schema import get_schema_instance


def finalize_query(query, inverted):
    base_query = {"query": {
        "bool": defaultdict(list)
    }}
    if inverted:
        base_query["bool"]["filter"].append(query)
    else:
        base_query["bool"]["must_not"].append(query)
    return base_query


def build_query(expr, schema_instance):
    base_query = {
        "bool": {}
    }
    if isinstance(expr.operator, Logical):
        left, left_invert = build_query(expr.left, schema_instance)
        right, right_invert = build_query(expr.right, schema_instance)
        if expr.operator.operator == 'or':
            base_query["bool"]["minimum_should_match"] = 1
            base_query["bool"]["should"] = [left, right]
        else:
            base_query["bool"]["filter"] = [left, right]
        return base_query, False

    field = schema_instance.resolve_name(expr.left)

    # if not field:
    #     That must be a reference to a model without specifying a field.
    #     Let's construct an abstract lookup field for it
    #     field = ElasticDjangoQlField(
    #       name=expr.left.parts[-1],
    #       nullable=True,
    #     )
    query, inverted = field.get_lookup(
        path=expr.left.parts[:-1],
        operator=expr.operator.operator,
        value=expr.right.value,
    )
    if inverted:
        base_query["bool"]["must_not"] = [query]
    else:
        base_query["bool"]["minimum_should_match"] = 1
        base_query["bool"]["should"] = [query]
    return base_query, inverted


def get_query(index, search):
    ast = DjangoQLParser().parse(search)
    schema_instance = get_schema_instance(index)
    schema_instance.validate(ast)
    query, inverted = build_query(ast, schema_instance)
    query = finalize_query(query, inverted)
    return query
