def serialize_suggestions_values_response(result):
    try:
        field_values = result["aggregations"]["values"]["buckets"]
    except KeyError:
        field_values = []
    return field_values


def serialize_mappings(mappings):
    result = []
    for field in mappings:
        result.append({"name": field.name, "type": field.elastic_field_type})
    return result
