# -*- coding: utf-8 -*-
# This script searches for abbreviations and terms.


import sys
import re
import locale


locale.setlocale(locale.LC_ALL, 'cs_CZ.utf8')


filename = sys.argv[1]
with open(filename) as f:
    lines = f.readlines()


re_word = re.compile(r'[\w]+', re.U)
re_abbr = re.compile(r'[^\s\.]\s([\w]+)', re.U)
re_number = re.compile(r'[0-9]+', re.U)


terms = {}


for ln, line in enumerate(lines):
    ln = ln + 1
    line = line.decode('utf8')

    for word in re_word.findall(line):
        if re_number.match(word):
            continue

        if word == word.upper() and len(word) > 1:
            print '%d:\t%s' % (ln, word.encode('utf-8'))
            terms[word] = terms.get(word, 0) + 1

    for match in re_abbr.finditer(line):
        word = match.group(1)

        if re_number.match(word):
            continue

        if word[0] == word[0].upper():
            print '%d:\t%s' % (ln, word.encode('utf-8'))
            terms[word] = terms.get(word, 0) + 1


print '\n\n'


for word, count in sorted(terms.items(), key=lambda x: x[1], reverse=True):
    print '%s%d' % (word.encode('utf-8').ljust(20), count)
