def dot_join(first: str, secound: str) -> str:
    if not (isinstance(first, str) and isinstance(secound, str)):
        raise TypeError("both first and second args should have the str type")
    return f"{first}.{secound}"


def build_field_name_from_parts(parts):
    return '.'.join(parts)


def get_fields(fields_dict, base_name):
    """
        this method is not used yet
        :param fields_dict:
        :param base_name:
        :return:
    """
    fields = []
    for field_name, data in fields_dict.items():
        fields.append({"name": dot_join(base_name, field_name), "type": data["type"]})
    return fields


def get_properties(mappings, base_name=None):
    """
        this method is not used yet
        :param fields_dict:
        :param base_name:
        :return:
    """
    result = []
    if not mappings:
        return result
    properties = mappings.get("properties")
    if properties:
        for property_name, property_data in properties.items():
            prefix = dot_join(base_name, property_name) if base_name else property_name
            props = get_properties(property_data, base_name=prefix)
            result.extend(props)
        return result
    field_type = mappings.get("type")
    if field_type:
        result.append({"name": base_name, "type": field_type})
        fields_property = mappings.get("fields")
        if fields_property:
            fields = get_fields(fields_property, base_name)
            result.extend(fields)
    return result
