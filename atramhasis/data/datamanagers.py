# -*- coding: utf-8 -*-
from skosprovider_sqlalchemy.models import ConceptScheme, Thing, Label, Concept, Collection, Language, MatchType, Match, \
    LabelType
from sqlalchemy import desc, func
from sqlalchemy.orm import joinedload


class DataManager(object):

    def __init__(self, session):
        self.session = session


class ConceptSchemeManager(DataManager):
    def __init__(self, session):
        super(ConceptSchemeManager, self).__init__(session)

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
        super(SkosManager, self).__init__(session)

    def get_thing(self, concept_id, conceptscheme_id):
        '''

        :param concept_id: a concept id
        :param conceptscheme_id: a conceptscheme id
        :return: the selected thing (Concept or Collection)
        '''
        return self.session.query(Thing) \
            .filter_by(concept_id=concept_id, conceptscheme_id=conceptscheme_id) \
            .one()

    def save(self, thing):
        '''

        :param thing: thing to save
        :return: saved thing
        '''
        self.session.add(thing)
        self.session.flush()
        return thing

    def delete_thing(self, thing):
        '''

        :param thing: the thing to delete
        '''
        self.session.delete(thing)

    def get_by_list_type(self, list_type):
        '''

        :param list_type: a specific list type
        :return: all results for the specific list type
        '''
        return self.session.query(list_type).all()

    def get_match_type(self, match_type):
        return self.session.query(MatchType).filter_by(name=match_type).one()

    def get_match(self, uri, matchtype_id, concept_id):
        return self.session.query(Match).filter_by(uri=uri, matchtype_id=matchtype_id,
                                                   concept_id=concept_id).one()

    def get_all_label_types(self):
        return self.session.query(LabelType).all()

    def get_next_cid(self, conceptscheme_id):
        return self.session.query(
            func.max(Thing.concept_id)
        ).filter_by(conceptscheme_id=conceptscheme_id).first()[0]


class LanguagesManager(DataManager):
    def __init__(self, session):
        super(LanguagesManager, self).__init__(session)

    def get(self, language_id):
        return self.session.query(Language).filter_by(id=language_id).one()

    def save(self, language):
        '''

        :param language: language to save
        :return: saved language
        '''
        self.session.add(language)
        self.session.flush()
        return language

    def delete(self, language):
        '''

        :param language: the language to delete
        '''
        self.session.delete(language)

    def get_all(self):
        '''

        :return: list of all languages
        '''
        return self.session.query(Language).all()

    def get_all_sorted(self, sort_coll, sort_desc):
        '''

        :param sort_coll: sort on this column
        :param sort_desc: descending or not
        :return: sorted list of languages
        '''
        if sort_desc:
            languages = self.session.query(Language).order_by(desc(sort_coll)).all()
        else:
            languages = self.session.query(Language).order_by(sort_coll).all()
        return languages

    def count_languages(self, language_tag):
        return self.session.query(Language).filter_by(id=language_tag).count()