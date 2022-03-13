import random
import string
from unittest import TestCase
from unittest.mock import patch, Mock

from elastic_dql.utils import dot_join, get_fields, get_properties


def mocked_dot_join(*args):
    return '.'.join(args)


def mocked_get_fields(*args, **kwargs):
    return [{"name": "field_name.keyword", "type": "keyword"}]


class TestDotJoin(TestCase):

    def test_dot_join(self):
        first_strings = [''.join(random.choices(string.ascii_lowercase)) for _ in range(5)]
        second_strings = [''.join(random.choices(string.ascii_lowercase)) for _ in range(5)]
        all_arguments = zip(first_strings, second_strings)
        for args in all_arguments:
            joined = '.'.join(args)
            self.assertEqual(joined, dot_join(*args))

    def test_first_is_not_str(self):
        first_string = 1
        second_string = "string"
        self.assertRaises(TypeError, dot_join, first_string, second_string)

    def test_second_is_not_str(self):
        first_string = "string"
        second_string = 1
        self.assertRaises(TypeError, dot_join, first_string, second_string)


class TestGetFields(TestCase):
    def setUp(self) -> None:
        self.random_base_name = ''.join(random.choices(string.ascii_lowercase, k=5))
        self.dot_join_patcher = patch("elastic_dql.utils.dot_join", new=mocked_dot_join)
        self.dot_join_patcher.start()

    def tearDown(self) -> None:
        self.dot_join_patcher.stop()

    def test_empty_dict_output_type(self):
        fields_dict = {}
        fields = get_fields(fields_dict, self.random_base_name)
        self.assertIsInstance(fields, list)

    def test_empty_dict(self):
        fields_dict = {}
        fields = get_fields(fields_dict, self.random_base_name)
        self.assertListEqual(fields, [])

    def test_filled_dict_output_type(self):
        fields_dict = {"keyword": {"type": "keyword"}}
        fields = get_fields(fields_dict, self.random_base_name)
        self.assertIsInstance(fields, list)

    def test_filled_dict(self):
        fields_dict = {"keyword": {"type": "keyword"}}
        fields = get_fields(fields_dict, self.random_base_name)
        self.assertListEqual(fields, [{"name": f"{self.random_base_name}.keyword", "type": "keyword"}])

    def test_multiple_fields(self):
        fields_dict = {"keyword": {"type": "keyword"}, "new_field": {"type": "new_type"}}
        fields = get_fields(fields_dict, self.random_base_name)
        expected_output = [{"name": f"{self.random_base_name}.keyword", "type": "keyword"}
            , {"name": f"{self.random_base_name}.new_field", "type": "new_type"}]
        self.assertListEqual(fields, expected_output)


class TestGetProperties(TestCase):
    def setUp(self) -> None:
        self.dot_join_patcher = patch("elastic_dql.utils.dot_join", new=mocked_dot_join)
        self.dot_join_patcher.start()
        self.get_fields_patcher = patch("elastic_dql.utils.get_fields", new=mocked_get_fields)
        self.get_fields_patcher.start()

    def tearDown(self) -> None:
        self.dot_join_patcher.stop()
        self.get_fields_patcher.stop()

    def test_empty_mapping(self):
        mappings = {}
        properties = get_properties(mappings)
        self.assertListEqual(properties, [])

    def test_has_not_properties(self):
        mappings = {"some_key": {"key": "value"}}
        properties = get_properties(mappings)
        self.assertListEqual(properties, [])

    def test_one_simple_property(self):
        mappings = {"properties": {"field_name": {"type": "field_type"}}}
        properties = get_properties(mappings)
        self.assertListEqual(properties, [{"name": "field_name", "type": "field_type"}])

    def test_multi_simple_properties(self):
        mappings = {"properties": {"field_name": {"type": "field_type"}, "field_name2": {"type": "field_type2"}}}
        properties = get_properties(mappings)
        self.assertListEqual(properties, [{"name": "field_name", "type": "field_type"},
                                          {"name": "field_name2", "type": "field_type2"}])

    def test_one_simple_property_with_field(self):
        mappings = {"properties": {"field_name": {"type": "field_type", "fields": {"keyword": {"type": "keyword"}}}}}
        properties = get_properties(mappings)
        self.assertListEqual(properties, [{"name": "field_name", "type": "field_type"},
                                          {"name": "field_name.keyword", "type": "keyword"}])

    def test_multi_simple_properties_with_field(self):
        mappings = {"properties": {"field_name": {"type": "field_type", "fields": {"keyword": {"type": "keyword"}}},
                                   "field_name2": {"type": "field_type2", "fields": {"keyword": {"type": "keyword"}}}}}
        properties = get_properties(mappings)
        self.assertListEqual(properties, [{"name": "field_name", "type": "field_type"},
                                          {"name": "field_name.keyword", "type": "keyword"},
                                          {"name": "field_name2", "type": "field_type2"},
                                          {"name": "field_name.keyword", "type": "keyword"}])

    def test_one_nested_property(self):
        mappings = {"properties": {"field_name": {"properties": {"nested_field_name": {"type": "nested_field_type"}}}}}
        properties = get_properties(mappings)
        self.assertListEqual(properties, [{"name": "field_name.nested_field_name", "type": "nested_field_type"}])

    def test_multi_nested_properties(self):
        mappings = {"properties": {"field_name": {"properties": {"nested_field_name": {"type": "nested_field_type"}}},
                                   "field_name2": {
                                       "properties": {"nested_field_name": {"type": "nested_field_type2"}}}}}
        properties = get_properties(mappings)
        self.assertListEqual(properties, [{"name": "field_name.nested_field_name", "type": "nested_field_type"},
                                          {"name": "field_name2.nested_field_name", "type": "nested_field_type2"}])
