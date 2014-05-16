from skosprovider_sqlalchemy.models import (
    Thing,
    Label as LabelModel
)

from sqlalchemy.orm import joinedload


class AtramhasisService(object):
    def __init__(self, session, conceptscheme_id):
        self.conceptscheme_id = conceptscheme_id
        self.session = session

    def find(self, query, **kwargs):
        q = self.session \
            .query(Thing) \
            .options(joinedload('labels')) \
            .filter(Thing.conceptscheme_id == self.conceptscheme_id)
        if 'type' in query and query['type'] in ['concept', 'collection']:
            q = q.filter(Thing.type == query['type'])
        if 'label' in query:
            q = q.filter(
                Thing.labels.any(
                    LabelModel.label.ilike('%' + query['label'].lower() + '%')
                )
            )
        return q.all()

    def get_all(self, **kwargs):
        all_results = self.session \
            .query(Thing) \
            .options(joinedload('labels')) \
            .filter(Thing.conceptscheme_id == self.conceptscheme_id) \
            .all()
        return all_results
