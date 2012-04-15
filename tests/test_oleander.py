# -*- coding: utf-8 -*-


try:
    import unittest2 as unittest
except ImportError:
    import unittest


from oleander import Oleander, MissingComponentException, MissingMethodException


class ContactsMapper(object):

    from_facebook_called = False
    to_facebook_called = False

    def from_facebook(self, data):
        self.from_facebook_called = True

    def to_facebook(self, data):
        self.to_facebook_called = True


class EventsMapper(object):
    pass


class FacebookAdapter(object):

    get_contacts_called = False
    send_contacts_called = False

    def get_contacts(self):
        self.get_contacts_called = True

    def send_contacts(self, data=None):
        self.send_contacts_called = True


class TestOleander(unittest.TestCase):

    def test_missing_adapter(self):
        o = Oleander()
        o.register_mapper('contacts', ContactsMapper())
        with self.assertRaises(MissingComponentException):
            o.get('contacts', 'facebook')

    def test_missing_mapper(self):
        o = Oleander()
        o.register_adapter('facebook', FacebookAdapter())
        with self.assertRaises(MissingComponentException):
            o.get('contacts', 'facebook')

    def test_reqister_by_import_string(self):
        o = Oleander()

        o.register_mapper('contacts', 'test_oleander.ContactsMapper')
        o.register_adapter('facebook', 'test_oleander.FacebookAdapter')
        o.get('contacts', 'facebook')

        self.assertTrue(o._mappers['contacts'].from_facebook_called)
        self.assertTrue(o._adapters['facebook'].get_contacts_called)

    def test_get(self):
        o = Oleander()
        m = ContactsMapper()
        a = FacebookAdapter()

        o.register_mapper('contacts', m)
        o.register_adapter('facebook', a)

        o.get('contacts', 'facebook')
        self.assertTrue(m.from_facebook_called)
        self.assertTrue(a.get_contacts_called)

    def test_send(self):
        o = Oleander()
        m = ContactsMapper()
        a = FacebookAdapter()

        o.register_mapper('contacts', m)
        o.register_adapter('facebook', a)

        dummy_data = [2, 4, 6, 8, 10]
        o.send('contacts', 'facebook', data=dummy_data)
        self.assertTrue(m.to_facebook_called)
        self.assertTrue(a.send_contacts_called)
        self.assertTrue(m.from_facebook_called)

    def test_missing_methods(self):
        o = Oleander()
        o.register_mapper('events', EventsMapper())
        o.register_adapter('facebook', FacebookAdapter())
        with self.assertRaises(MissingMethodException):
            o.get('events', 'facebook')
        with self.assertRaises(MissingMethodException):
            o.send('events', 'facebook')

        dummy_data = [2, 4, 6, 8, 10]
        with self.assertRaises(MissingMethodException):
            o.send('events', 'facebook', data=dummy_data)

    def test_documentation(self):
        o = Oleander()

        # test class
        self.assertTrue(o.__doc__)

        # test all public methods
        for prop_name in dir(o):
            prop = getattr(o, prop_name)
            if not prop_name.startswith('_') and hasattr(prop, '__call__'):
                self.assertTrue(prop.__doc__)


if __name__ == '__main__':
    unittest.main()