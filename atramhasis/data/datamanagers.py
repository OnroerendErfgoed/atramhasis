# -*- coding: utf-8 -*-
"""
This module adds DataManagers for Atramhasis. These are service layer objects
that abstract all interactions with the database away from the views.

:versionadded: 0.4.1
"""
from datetime import datetime, date

import dateutil.relativedelta
from skosprovider_sqlalchemy.models import ConceptScheme, Thing, Label, Concept, Collection, Language, MatchType, Match, \
    LabelType
from sqlalchemy import desc, func, and_
from sqlalchemy.orm import joinedload

from atramhasis.data import popular_concepts
from atramhasis.data.models import ConceptVisitLog, ConceptschemeCounts


class DataManager(object):
    """
    A DataManager abstracts all interactions with the database for a certain model.
    """

    def __init__(self, session):
        self.session = session


class ConceptSchemeManager(DataManager):
    """
    A :class:`DataManager` for
    :class:`ConceptSchemes <skosprovider_sqlalchemy.models.ConceptScheme>.`
    """

    def __init__(self, session):
        super(ConceptSchemeManager, self).__init__(session)

    def get(self, conceptscheme_id):
        """

        :param conceptscheme_id: a concepscheme id
        :return: the concepscheme for the given id
        """
        return self.session.query(ConceptScheme).filter_by(id=conceptscheme_id).one()

    def find(self, conceptscheme_id, query):
        """
        Find concepts and collections in this concept scheme.

        :param conceptscheme_id: a concepscheme id
        :param query: A python dictionary containing query parameters.
        :returns: A :class:`list` of
            :class:`skosprovider_sqlalchemy.models.Thing` instances.
        """
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
        """

        :param conceptscheme_id:  a concepscheme id
        :return: all concepts for the scheme_tree
        """
        return self.session \
            .query(Concept) \
            .filter(Concept.conceptscheme_id == conceptscheme_id,
                    ~Concept.broader_concepts.any(),
                    ~Collection.member_of.any()
                    ).all()

    def get_collections_for_scheme_tree(self, conceptscheme_id):
        """

        :param conceptscheme_id: a concepscheme id
        :return: all collections for the scheme_tree
        """
        return self.session \
            .query(Collection) \
            .filter(Collection.conceptscheme_id == conceptscheme_id,
                    ~Collection.broader_concepts.any(),
                    ~Collection.member_of.any()
                    ).all()

    def get_all(self, conceptscheme_id):
        """
        Get all concepts and collections in this concept scheme.

        :param conceptscheme_id: a concepscheme id
        :returns: A :class:`list` of
            :class:`skosprovider_sqlalchemy.models.Thing` instances.
        """
        all_results = self.session \
            .query(Thing) \
            .options(joinedload('labels')) \
            .filter(Thing.conceptscheme_id == conceptscheme_id) \
            .all()
        return all_results

    def save(self, conceptscheme):
        """

        :param conceptscheme: conceptscheme to save
        :return: saved conceptscheme
        """
        self.session.merge(conceptscheme)
        self.session.flush()
        return conceptscheme


class SkosManager(DataManager):
    """
    A :class:`DataManager` for
    :class:`Concepts and Collections <skosprovider_sqlalchemy.models.Thing>.`
    """

    def __init__(self, session):
        super(SkosManager, self).__init__(session)

    def get_thing(self, concept_id, conceptscheme_id):
        """

        :param concept_id: a concept id
        :param conceptscheme_id: a conceptscheme id
        :return: the selected thing (Concept or Collection)
        """
        return self.session.query(Thing) \
            .filter_by(concept_id=concept_id, conceptscheme_id=conceptscheme_id) \
            .one()

    def save(self, thing):
        """

        :param thing: thing to save
        :return: saved thing
        """
        self.session.add(thing)
        self.session.flush()
        return thing

    def change_type(self, thing, concept_id, conceptscheme_id, new_type):
        self.delete_thing(thing)
        self.session.flush()
        thing = Concept() if new_type == 'concept' else Collection()
        thing.type = new_type
        thing.concept_id = concept_id
        thing.conceptscheme_id = conceptscheme_id
        self.save(thing)
        return thing

    def delete_thing(self, thing):
        """

        :param thing: the thing to delete
        """
        self.session.delete(thing)

    def get_by_list_type(self, list_type):
        """

        :param list_type: a specific list type
        :return: all results for the specific list type
        """
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
    """
    A :class:`DataManager` for
    :class:`Languages <skosprovider_sqlalchemy.models.Language>.`
    """

    def __init__(self, session):
        super(LanguagesManager, self).__init__(session)

    def get(self, language_id):
        return self.session.query(Language).filter_by(id=language_id).one()

    def save(self, language):
        """

        :param language: language to save
        :return: saved language
        """
        self.session.add(language)
        self.session.flush()
        return language

    def delete(self, language):
        """

        :param language: the language to delete
        """
        self.session.delete(language)

    def get_all(self):
        """

        :return: list of all languages
        """
        return self.session.query(Language).all()

    def get_all_sorted(self, sort_coll, sort_desc):
        """

        :param sort_coll: sort on this column
        :param sort_desc: descending or not
        :return: sorted list of languages
        """
        if sort_desc:
            languages = self.session.query(Language).order_by(desc(sort_coll)).all()
        else:
            languages = self.session.query(Language).order_by(sort_coll).all()
        return languages

    def count_languages(self, language_tag):
        return self.session.query(Language).filter_by(id=language_tag).count()


class AuditManager(DataManager):
    """
    A data manager for logging the visit.
    """

    def save(self, visit_log):
        """
        save a certain visit
        :param visit_log: log of visit to save
        :return: The saved visit log
        """
        self.session.add(visit_log)
        self.session.flush()
        return visit_log

    @popular_concepts.cache_on_arguments(expiration_time=86400)
    def get_most_popular_concepts_for_conceptscheme(self, conceptscheme_id, max=5, period='last_month'):
        """
        get the most popular concepts for a conceptscheme
        :param conceptscheme_id: id of the conceptscheme
        :param max: maximum number of results, default 5
        :param period: 'last_day' or 'last_week' or 'last_month' or 'last_year', default 'last_month'
        :return: List of the most popular concepts of a conceptscheme over a certain period
        """

        start_date = self._get_first_day(period)
        popular_concepts = self.session.query(
            ConceptVisitLog.concept_id,
            func.count(ConceptVisitLog.concept_id).label('count')
        ).filter(
            and_(ConceptVisitLog.conceptscheme_id == conceptscheme_id,
                 ConceptVisitLog.visited_at >= start_date)
        ).group_by(
            ConceptVisitLog.concept_id
        ).order_by(
            desc('count')
        ).limit(
            max
        ).all()
        results = []
        for concept in popular_concepts:
            results.append({'concept_id': concept.concept_id, 'scheme_id': conceptscheme_id})
        return results

    @staticmethod
    def _get_first_day(period):
        """
        get the first day of a certain period until now
        :param period: 'last_day' or 'last_week' or 'last_month' or 'last_year'
        :return: (string) the first day of the period
        """
        d = date.today()
        datetime.combine(d, datetime.min.time())
        start_date = d - dateutil.relativedelta.relativedelta(
            days=1 if period == 'last_day' else 0,
            weeks=1 if period == 'last_week' else 0,
            months=1 if period == 'last_month' else 0,
            years=1 if period == 'last_year' else 0
        )
        return start_date.strftime("%Y-%m-%d")


class CountsManager(DataManager):
    """
    A data manager that deals with triple counts.
    """

    def save(self, counts):
        """
        Save a certain counts object

        :param atramhasis.data.models.ConceptschemeCounts counts: Counts object to save

        :return: The saved count
        """
        self.session.add(counts)
        self.session.flush()
        return counts

    def get_most_recent_count_for_scheme(self, conceptscheme_id):
        recent = self.session.query(
            ConceptschemeCounts
        ).filter_by(
            conceptscheme_id=conceptscheme_id
        ).order_by(
            desc('counted_at')
        ).one()
        return recent
