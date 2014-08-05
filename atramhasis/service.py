# -*- coding: utf-8 -*-
'''
Module containing internal service layer used by Atramhasis.
'''
from skosprovider_sqlalchemy.models import (
    Thing,
    Label as LabelModel
)

from sqlalchemy.orm import joinedload


class AtramhasisService(object):
    '''
    A service object that handles queries on the database.

    This service talks directly to the SQL database used by Atramhasis and
    returns objects from the :mod:`skosprovider_sqlalchemy.models` module.

    :param session:  A :class:`sqlalchemy.orm.session.Session`.
    :param int conceptscheme_id: Id of the conceptscheme this service is
        handling.
    '''
    def __init__(self, session, conceptscheme_id):
        self.conceptscheme_id = conceptscheme_id
        self.session = session

    def find(self, query, **kwargs):
        '''
        Find concepts and collections in this concept scheme.

        :param dict query: A python dictionary containing query parameters.
        :returns: A :class:`list` of 
            :class:`skosprovider_sqlalchemy.models.Thing` instances.
        '''
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
        '''
        Get all concepts and collections in this concept scheme.

        :returns: A :class:`list` of 
            :class:`skosprovider_sqlalchemy.models.Thing` instances.
        '''
        all_results = self.session \
            .query(Thing) \
            .options(joinedload('labels')) \
            .filter(Thing.conceptscheme_id == self.conceptscheme_id) \
            .all()
        return all_results
