from unittest import TestCase

from elastic_dql.field import ElasticDjangoQlField
from ..utils import generate_random_string


class FieldTestCase(TestCase):

    def setUp(self) -> None:
        pass

    def test_get_lookup_name(self):
        field_name = generate_random_string()
        field = ElasticDjangoQlField(field_name)
        self.assertEqual(field.get_lookup_name(), field_name)

    def test_format_value(self):
        field_name = generate_random_string()
        field_type = int
        field = ElasticDjangoQlField(field_name, field_type=field_type)
        value = field.format_value(2.6)
        self.assertIsInstance(value, field_type)

    def test_format_value_raise_exception(self):
        field_name = generate_random_string()
        field_type = int
        field = ElasticDjangoQlField(field_name, field_type=field_type)
        self.assertRaises(ValueError, field.format_value, "asdasdasd")
