# -*- coding: utf-8 -*-


# There is obviously naming collision between standard library's csv module and this module,
# but I really didn't want to come up with a different name. For further explanation of this
# statement, see http://docs.python.org/whatsnew/2.5.html#pep-328-absolute-and-relative-imports.
from __future__ import absolute_import


import csv as csv_parser
from datetime import datetime
import codecs
from oleander import Entity


try:
    import cStringIO
except ImportError:
    import StringIO


# following code taken directly from Python Docs http://docs.python.org/library/csv.html#examples


class UTF8Recoder(object):
    """Iterator that reads an encoded stream and reencodes the input to UTF-8."""

    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf-8')


class UnicodeReader(object):
    """A CSV reader which will iterate over lines in the CSV file 'f', which is encoded in the given encoding."""

    def __init__(self, f, dialect=csv_parser.excel, encoding='utf-8', **kwargs):
        f = UTF8Recoder(f, encoding)
        self.reader = csv_parser.reader(f, dialect=dialect, **kwargs)

    def next(self):
        row = self.reader.next()
        return [unicode(s, 'utf-8') for s in row]

    def __iter__(self):
        return self


class UnicodeWriter(object):
    """A CSV writer which will write rows to CSV file 'f', which is encoded in the given encoding."""

    def __init__(self, f, dialect=csv_parser.excel, encoding='utf-8', **kwargs):
        # redirect output to a queue
        self.queue = StringIO.StringIO()
        self.writer = csv_parser.writer(self.queue, dialect=dialect, **kwargs)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode('utf-8') for s in row])
        # fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode('utf-8')
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# adapter's own code


class CSVContactMapper(object):

    def _parse_date(self, date_string):
        try:
            parsed_datetime = datetime.strptime(date_string, '%d.%m.%Y')
            return parsed_datetime.date()
        except ValueError:
            return None

    def _parse_name(self, name, first_name=None, middle_name=None, last_name=None):
        if not name:
            names = []
            if first_name:
                names.append(first_name)
            if middle_name:
                names.append(middle_name)
            if last_name:
                names.append(last_name)
            name = ' '.join(names) or None
        return name

    def source_to_contact(self, contact):
        """Map CSV file rows into contact entities."""
        bday_date = self._parse_date(contact.get('Birthday', ''))
        first_name = contact.get('First Name', None)
        middle_name = contact.get('Middle Name', None)
        last_name = contact.get('Last Name', None)

        # determine name
        name = self._parse_name(
            contact.get('Name', None),
            first_name, middle_name, last_name
        )

        # map values to contact object
        return Entity(
            name=name,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            gender=contact.get('Gender', None),
            birthday=bday_date,
            location=contact.get('Location', None),
            language=contact.get('Language', None),
            website=contact.get('Web Page', None),
            email=contact.get('E-mail Address', None),
            phone=contact.get('Primary Phone', None),
            address=contact.get('Primary Phone', None),
        )


class CSVAdapter(object):
    """Adapter for classic CSV files."""

    def __init__(self, file_name, encoding):
        self.file_name = file_name
        self.encoding = encoding

    def _get_rows(self):
        with open(self.file_name, 'rb') as f:
            reader = UnicodeReader(f, encoding=self.encoding)
            first_row = next(reader)
            for row in reader:
                yield dict(zip(first_row, row))

    @property
    def contacts(self):
        mapper = CSVContactMapper()
        return (mapper.source_to_contact(row) for row in self._get_rows())

