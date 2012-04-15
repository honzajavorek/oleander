# -*- coding: utf-8 -*-


try:
    import unittest2 as unittest
except ImportError:
    import unittest


from oleander.mappers import Mapper


class Entity(object):
    """Simple data container."""

    def __init__(self, **properties):
        self.__dict__.update(properties)

    def __getattr__(self, property):
        return None


class EntityMapper(Mapper):

    def from_service(self, data):
        for row in data:
            yield self.create_entity(
                name=row['name'],
                email=row['email'],
            )


class TestMapper(unittest.TestCase):

    def test_set_entity_class(self):
        m = EntityMapper(entity_class=Entity)
        entities = list(m.from_service([{'name': 'Franta', 'email': 'franta@example.com'}]))
        self.assertEqual(len(entities), 1)
        self.assertTrue(isinstance(entities[0], Entity))
        self.assertEqual(entities[0].email, 'franta@example.com')


if __name__ == '__main__':
    unittest.main()