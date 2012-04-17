# -*- coding: utf-8 -*-


try:
    import unittest2 as unittest
except ImportError:
    import unittest


import os
from oleander.adapters.csv import CSVAdapter


class TestCSVAdapter(unittest.TestCase):

    file_path = os.path.join(os.path.dirname(__file__), 'mock_csv.csv')

    def test_get_results(self):
        csv = CSVAdapter(self.file_path, 'cp1250')
        result = list(csv.contacts)
        self.assertEquals(len(result), 26)

    def test_get_right_encoding(self):
        csv = CSVAdapter(self.file_path, 'cp1250')
        result = list(csv.contacts)
        self.assertEquals(result[8].last_name, u'Štěpanovský')


if __name__ == '__main__':
    unittest.main()