import csv
import codecs
from six import StringIO, text_type, PY2


class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.stream = f
        self.writer = csv.writer(self.stream, dialect=dialect, **kwds)
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):  # pragma: no cover
        #some ugly code to support python2
        if PY2:
            encoded_row = []
            for s in row:
                if isinstance(s, text_type):
                    encoded_row.append(self.encoder.encode(s))
                else:
                    encoded_row.append(s)
            self.writer.writerow(encoded_row)
        else:
            self.writer.writerow(row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class CSVRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        f_out = StringIO()
        writer = UnicodeWriter(f_out, delimiter=',', quoting=csv.QUOTE_ALL)

        writer.writerow(value['header'])
        writer.writerows(value['rows'])

        resp = system['request'].response
        resp.content_type = 'text/csv'
        resp.content_disposition = 'attachment;filename="' + value['filename'] + '.csv"'
        return f_out.getvalue()