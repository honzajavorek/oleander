# -*- coding: utf-8 -*-


try:
    import unittest2 as unittest
except ImportError:
    import unittest


from oleander.mappers.contacts import ContactsMapper


class Entity(object):
    """Simple data container."""

    def __init__(self, **properties):
        self.__dict__.update(properties)

    def __getattr__(self, property):
        return None


class TestContactsMapper(unittest.TestCase):

    csv_rows = [{u'Priority': u'Normal', u'E-mail Address': u'6a6@example.com',
        u'Categories': u'6a6;Moje kontakty', u'First Name': u'6A6'}]

    def test_set_entity_class(self):
        m = ContactsMapper(entity_class=Entity)
        contacts = list(m.from_csv_file(self.csv_rows))
        self.assertEqual(len(contacts), 1)
        self.assertTrue(isinstance(contacts[0], Entity))
        self.assertEqual(contacts[0].email, '6a6@example.com')

    def test_from_csv_file(self):
        m = ContactsMapper()
        contacts = list(m.from_csv_file(self.csv_rows))
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]['email'], '6a6@example.com')


if __name__ == '__main__':
    unittest.main()