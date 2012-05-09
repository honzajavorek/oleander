# -*- coding: utf-8 -*-


from . import TestCase, AppMixin
from oleander.letters import alphabet, first_letter, Letter, groupby
import operator


class TestAlphabet(AppMixin, TestCase):

    def test_ascii(self):
        try:
            map(str, alphabet())
        except UnicodeEncodeError:
            self.fail()

    def test_26_chars(self):
        self.assertEqual(len(alphabet()), 26)

    def test_uppercase_letters(self):
        map(lambda item: self.assertRegexpMatches(item, r'^[A-Z]$'), alphabet())


class TestFirstLetter(AppMixin, TestCase):

    def test_ascii(self):
        try:
            str(first_letter(u'úpění'))
        except UnicodeEncodeError:
            self.fail()

    def test_single_char(self):
        self.assertEqual(len(first_letter(u'úpění')), 1)

    def test_uppercase(self):
        self.assertEqual(first_letter('honza'), 'H')
        self.assertEqual(first_letter('ZUZKA'), 'Z')

    def test_empty(self):
        self.assertEqual(first_letter(''), '')

    def test_number(self):
        self.assertEqual(first_letter(u'40 loupežníků'), '4')

    def test_hash(self):
        tricky_words = [
            u'řeřicha',
            u'ÁMOS',
            u'✈✈✈ všichni jsou blázni, jen já jsem letadlo',
        ]
        map(lambda word: self.assertEqual(first_letter(word), '#'), tricky_words)


class TestLetter(AppMixin, TestCase):

    def _test_op(self, op, cases):
        for letter_1, letter_2 in cases:
            self.assertTrue(op(Letter(letter_1), Letter(letter_2)))

    def test_lt(self):
        op = operator.lt
        cases = [
            ('A', 'B'),
            ('A', 'X'),
            ('Z', '#'),
        ]
        self._test_op(op, cases)

    def test_le(self):
        op = operator.le
        cases = [
            ('A', 'B'),
            ('N', '#'),
            ('#', '#'),
        ]
        self._test_op(op, cases)

    def test_gt(self):
        op = operator.gt
        cases = [
            ('B', 'A'),
            ('R', 'C'),
            ('#', 'G'),
        ]
        self._test_op(op, cases)

    def test_ge(self):
        op = operator.ge
        cases = [
            ('B', 'A'),
            ('#', 'H'),
            ('#', '#'),
        ]
        self._test_op(op, cases)

    def test_eq(self):
        op = operator.eq
        cases = [
            ('A', 'A'),
            ('H', 'H'),
            ('#', '#'),
        ]
        self._test_op(op, cases)


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class TestGroupby(AppMixin, TestCase):

    sample = [
        Struct(**{'name': u'áhoj'}),
        Struct(**{'name': u'ýháá'}),
        Struct(**{'name': u'nazdar'}),
        Struct(**{'name': u'nanuk'}),
        Struct(**{'name': u'xenie'}),
    ]

    def test_groupby(self):
        grouped = groupby(self.sample, 'name')
        self.assertEqual(grouped[0].grouper, 'N')
        self.assertTrue(grouped[0].list)

        self.assertEqual(grouped[1].grouper, 'X')
        self.assertTrue(grouped[1].list)

        self.assertEqual(grouped[2].grouper, '#')
        self.assertTrue(grouped[2].list)

    def test_full_alphabet(self):
        grouped = groupby(self.sample, 'name', full_alphabet=True)
        self.assertEqual(grouped[13].grouper, 'N')
        self.assertTrue(grouped[13].list)

        self.assertEqual(grouped[23].grouper, 'X')
        self.assertTrue(grouped[23].list)

        self.assertEqual(grouped[26].grouper, '#')
        self.assertTrue(grouped[26].list)

    def test_no_hash(self):
        grouped = groupby(self.sample[2:], 'name', full_alphabet=True)
        self.assertEqual(len(grouped), 26)

    def test_number(self):
        grouped = groupby([Struct(**{'name': u'40 loupežníků'})], 'name', full_alphabet=True)
        self.assertEqual(len(grouped), 27)
        self.assertEqual(grouped[0].grouper, '4')
        self.assertTrue(grouped[0].list)

