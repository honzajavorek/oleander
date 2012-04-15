# -*- coding: utf-8 -*-


import csv
import codecs


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
    """A CSV reader which will iterate over lines in the CSV file "f", which is encoded in the given encoding."""

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', **kwargs):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwargs)

    def next(self):
        row = self.reader.next()
        return [unicode(s, 'utf-8') for s in row]

    def __iter__(self):
        return self


class UnicodeWriter(object):
    """A CSV writer which will write rows to CSV file "f", which is encoded in the given encoding."""

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', **kwargs):
        # redirect output to a queue
        self.queue = StringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwargs)
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


class CSVFileAdapter(object):
    """Adapter for classic CSV files."""

    def __init__(self, file_name, encoding):
        self.file_name = file_name
        self.encoding = encoding

    def get_contacts(self):
        with open(self.file_name, 'rb') as f:
            reader = UnicodeReader(f, encoding=self.encoding)
            first_row = next(reader)

            for row in reader:
                yield dict(zip(first_row, row))
