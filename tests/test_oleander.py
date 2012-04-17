# -*- coding: utf-8 -*-


try:
    import unittest2 as unittest
except ImportError:
    import unittest


from oleander import Oleander


package_import = 'tests.test_oleander'


class FacebookAdapter(object):

    get_contacts_called = 0
    send_contacts_called = 0

    @property
    def contacts(self):
        self.get_contacts_called += 1

    @contacts.setter
    def contacts(self, data=None):
        self.send_contacts_called += 1


class TestOleander(unittest.TestCase):

    def test_missing_adapter(self):
        o = Oleander()
        with self.assertRaises(LookupError):
            o.facebook.contacts

    def test_reqister_by_import_string(self):
        o = Oleander()
        o.register_adapter('facebook', package_import + '.FacebookAdapter')
        o.facebook.contacts
        self.assertEquals(o._adapters['facebook'].get_contacts_called, 1)

    def test_get(self):
        o = Oleander()
        a = FacebookAdapter()
        o.register_adapter('facebook', a)
        o.facebook.contacts
        self.assertEquals(a.get_contacts_called, 1)

    def test_send(self):
        o = Oleander()
        a = FacebookAdapter()
        o.register_adapter('facebook', a)
        o.facebook.contacts = [2, 4, 6, 8, 10]
        self.assertEquals(a.send_contacts_called, 1)

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
    package_import = 'test_oleander'
    unittest.main()