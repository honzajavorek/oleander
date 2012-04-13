# -*- coding: utf-8 -*-


try:
    import unittest2 as unittest
except ImportError:
    import unittest


from oleander import Oleander


class TestOleander(unittest.TestCase):

    def test_request(self):
        pass

    def test_api_for_humans(self):
        pass


if __name__ == '__main__':
    unittest.main()