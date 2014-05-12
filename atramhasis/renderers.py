import csv
from six import StringIO, text_type


class CSVRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        f_out = StringIO()
        writer = csv.writer(f_out, delimiter=',', quoting=csv.QUOTE_ALL)

        writer.writerow(value['header'])
        #writer.writerows(value['rows'])
        for row in value['rows']:
            r = []
            for item in row:
                # Ensure item is an object and not an empty unicode string
                if item and isinstance(item, text_type) and item != u'':
                    r.append(item.encode("UTF-8"))
            writer.writerow(r)

        resp = system['request'].response
        resp.content_type = 'text/csv'
        resp.content_disposition = 'attachment;filename="' + value['filename'] + '.csv"'
        return f_out.getvalue()