# -*- coding: utf-8 -*-


try:
    import unittest2 as unittest
except ImportError:
    import unittest


from oleander.adapters.csv_file import CSVFileAdapter


class TestCSVFileAdapter(unittest.TestCase):

    def test_get_results(self):
        csv = CSVFileAdapter('mock_csv_file.csv', 'cp1250')
        result = list(csv.get_contacts())
        self.assertEquals(len(result), 26)

    def test_get_right_encoding(self):
        csv = CSVFileAdapter('mock_csv_file.csv', 'cp1250')
        result = list(csv.get_contacts())
        self.assertEquals(result[8]['Last Name'], u'Štěpanovský')


if __name__ == '__main__':
    unittest.main()