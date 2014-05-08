import csv
from six import StringIO
from pyramid.renderers import JSON
from skosprovider_sqlalchemy.models import (
    Concept,
    Collection
)


class CSVRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        f_out = StringIO()
        writer = csv.writer(f_out, delimiter=',', quoting=csv.QUOTE_ALL)

        writer.writerow(value['header'])
        writer.writerows(value['rows'])

        resp = system['request'].response
        resp.content_type = 'text/csv'
        resp.content_disposition = 'attachment;filename="' + value['filename'] + '.csv"'
        return f_out.getvalue()