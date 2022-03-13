import random
from string import ascii_lowercase
from unittest import TestCase

from elastic_dql.exceptions import SchemaError
from elastic_dql.schema import SchemaFactory


class SchemaFactoryTestCase(TestCase):

    def test_instance_type(self):
        schema_factory = SchemaFactory.get_instance()
        self.assertIsInstance(schema_factory, SchemaFactory)

    def test_child_schemafactory_instance_type(self):
        class CustomSchemaFactory(SchemaFactory):
            pass

        schema_factory = CustomSchemaFactory.get_instance()
        self.assertIsInstance(schema_factory, CustomSchemaFactory)

    def test_include_exclude_not_specified(self):
        class TestingSchemaFactory(SchemaFactory):
            include_indices = ()
            exclude_indices = ()

        try:
            schema_factory = TestingSchemaFactory.get_instance()
        except SchemaError as exception:
            self.assertEqual(str(exception), 'One of include_indices or exclude_indices must be specified')

    def test_include_exclude_are_both_specified(self):
        class TestingSchemaFactory(SchemaFactory):
            include_indices = ('index1')
            exclude_indices = ('index2')

        try:
            schema_factory = TestingSchemaFactory.get_instance()
        except SchemaError as exception:
            self.assertEqual(str(exception), 'Either include_indices or exclude_indices can be specified, but not both')

    def test_start_in_include_indices(self):
        class TestingSchemaFactory(SchemaFactory):
            include_indices = ('*')
            exclude_indices = ()

        schema_factory = TestingSchemaFactory.get_instance()
        random_index_names = [''.join(random.choices(ascii_lowercase, k=5)) for _ in range(10)]
        for index_name in random_index_names:
            self.assertFalse(schema_factory.excluded(index_name))

    def test_index_is_included(self):
        class TestingSchemaFactory(SchemaFactory):
            include_indices = ('index_1', 'index_2', 'index_3')
            exclude_indices = ()

        schema_factory = TestingSchemaFactory.get_instance()
        index_name = "index_1"
        self.assertFalse(schema_factory.excluded(index_name))

    def test_index_is_is_not_included(self):
        class TestingSchemaFactory(SchemaFactory):
            include_indices = ('index_1', 'index_2', 'index_3')
            exclude_indices = ()

        schema_factory = TestingSchemaFactory.get_instance()
        index_name = "index_20"
        self.assertTrue(schema_factory.excluded(index_name))

    def test_index_is_excluded(self):
        class TestingSchemaFactory(SchemaFactory):
            include_indices = ()
            exclude_indices = ("index_1", "index_2", "index_3")

        schema_factory = TestingSchemaFactory.get_instance()
        index_name = "index_1"
        self.assertTrue(schema_factory.excluded(index_name))

    def test_index_is_not_excluded(self):
        class TestingSchemaFactory(SchemaFactory):
            include_indices = ()
            exclude_indices = ("index_1", "index_2", "index_3")

        schema_factory = TestingSchemaFactory.get_instance()
        index_name = "index_20"
        self.assertFalse(schema_factory.excluded(index_name))
