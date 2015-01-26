# -*- coding: utf-8 -*-
from skosprovider_sqlalchemy.models import ConceptScheme, Thing, Label, Concept, Collection
from sqlalchemy.orm import joinedload
from atramhasis.data.data_transfer_objects import ResultDTO


class DataManager(object):
    @staticmethod
    def process_ranged_query(query, result_range):
        total = query.count()
        if result_range is not None:
            data = query \
                .offset(result_range.start) \
                .limit(result_range.get_page_size()) \
                .all()
        else:
            data = query.all()
        return ResultDTO(data, total)


class ConceptSchemeManager(DataManager):
    def __init__(self, session):
        self.session = session

    def get(self, conceptscheme_id):
        '''

        :param conceptscheme_id: a concepscheme id
        :return: the concepscheme for the given id
        '''
        return self.session.query(ConceptScheme).filter_by(id=conceptscheme_id).one()

    def find(self, conceptscheme_id, query):
        '''
        Find concepts and collections in this concept scheme.

        :param conceptscheme_id: a concepscheme id
        :param query: A python dictionary containing query parameters.
        :returns: A :class:`list` of
            :class:`skosprovider_sqlalchemy.models.Thing` instances.
        '''
        q = self.session \
            .query(Thing) \
            .options(joinedload('labels')) \
            .filter(Thing.conceptscheme_id == conceptscheme_id)
        if 'type' in query and query['type'] in ['concept', 'collection']:
            q = q.filter(Thing.type == query['type'])
        if 'label' in query:
            q = q.filter(
                Thing.labels.any(
                    Label.label.ilike('%' + query['label'].lower() + '%')
                )
            )
        return q.all()

    def get_concepts_for_scheme_tree(self, conceptscheme_id):
        '''

        :param conceptscheme_id:  a concepscheme id
        :return: all concepts for the scheme_tree
        '''
        return self.session \
            .query(Concept) \
            .filter(
            Concept.conceptscheme_id == conceptscheme_id,
            ~Concept.broader_concepts.any(),
            ~Collection.member_of.any()
        ).all()

    def get_collections_for_scheme_tree(self, conceptscheme_id):
        '''

        :param conceptscheme_id: a concepscheme id
        :return: all collections for the scheme_tree
        '''
        return self.session \
            .query(Collection) \
            .filter(
            Collection.conceptscheme_id == conceptscheme_id,
            ~Collection.broader_concepts.any(),
            ~Collection.member_of.any()
        ).all()

    def get_all(self, conceptscheme_id):
        '''
        Get all concepts and collections in this concept scheme.

        :param conceptscheme_id: a concepscheme id
        :returns: A :class:`list` of
            :class:`skosprovider_sqlalchemy.models.Thing` instances.
        '''
        all_results = self.session \
            .query(Thing) \
            .options(joinedload('labels')) \
            .filter(Thing.conceptscheme_id == conceptscheme_id) \
            .all()
        return all_results


class SkosManager(DataManager):
    def __init__(self, session):
        self.session = session

    def get_thing(self, concept_id, conceptscheme_id):
        '''

        :param concept_id: a concept id
        :param conceptscheme_id: a conceptscheme id
        :return: the selected thing (Concept or Collection)
        '''
        return self.session.query(Thing) \
            .filter_by(concept_id=concept_id, conceptscheme_id=conceptscheme_id) \
            .one()

    def get_by_list_type(self, list_type):
        '''

        :param list_type: a specific list type
        :return: all results for the specific list type
        '''
        return self.session.query(list_type).all()