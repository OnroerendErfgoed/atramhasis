"""
This module adds DataManagers for Atramhasis. These are service layer objects
that abstract all interactions with the database away from the views.

:versionadded: 0.4.1
"""
import uuid
from datetime import date
from datetime import datetime
from typing import List

import dateutil.relativedelta
import sqlalchemy as sa
from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import Label
from skosprovider_sqlalchemy.models import LabelType
from skosprovider_sqlalchemy.models import Language
from skosprovider_sqlalchemy.models import Match
from skosprovider_sqlalchemy.models import MatchType
from skosprovider_sqlalchemy.models import Thing
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from atramhasis.data import popular_concepts
from atramhasis.data.models import ConceptVisitLog
from atramhasis.data.models import ConceptschemeCounts
from atramhasis.data.models import IDGenerationStrategy
from atramhasis.data.models import Provider
from atramhasis.scripts import delete_scheme


class DataManager:
    """
    A DataManager abstracts all interactions with the database for a certain model.
    """

    def __init__(self, session: Session) -> None:
        self.session: Session = session


class ConceptSchemeManager(DataManager):
    """
    A :class:`DataManager` for
    :class:`ConceptSchemes <skosprovider_sqlalchemy.models.ConceptScheme>.`
    """

    def __init__(self, session):
        super().__init__(session)

    def get(self, conceptscheme_id):
        """

        :param conceptscheme_id: a concepscheme id
        :return: the concepscheme for the given id
        """
        return self.session.execute(
            select(ConceptScheme)
            .filter(ConceptScheme.id == conceptscheme_id)
        ).scalar_one()

    def find(self, conceptscheme_id, query):
        """
        Find concepts and collections in this concept scheme.

        :param conceptscheme_id: a concepscheme id
        :param query: A python dictionary containing query parameters.
        :returns: A :class:`list` of
            :class:`skosprovider_sqlalchemy.models.Thing` instances.
        """
        db_query = (
            select(Thing)
            .options(joinedload(Thing.labels))
            .filter(Thing.conceptscheme_id == conceptscheme_id)
        )
        if 'type' in query and query['type'] in ['concept', 'collection']:
            db_query = db_query.filter(Thing.type == query['type'])
        if 'label' in query:
            db_query = db_query.filter(
                Thing.labels.any(
                    Label.label.ilike('%' + query['label'].lower() + '%')
                )
            )
        return self.session.execute(db_query).unique().scalars().all()

    def get_concepts_for_scheme_tree(self, conceptscheme_id):
        """

        :param conceptscheme_id:  a concepscheme id
        :return: all concepts for the scheme_tree
        """
        return self.session.execute(
            select(Concept)
            .filter(
                Concept.conceptscheme_id == conceptscheme_id,
                ~Concept.broader_concepts.any(),
                ~Collection.member_of.any()
            )
        ).scalars().all()

    def get_collections_for_scheme_tree(self, conceptscheme_id):
        """

        :param conceptscheme_id: a concepscheme id
        :return: all collections for the scheme_tree
        """
        return self.session.execute(
            select(Collection)
            .filter(
                Collection.conceptscheme_id == conceptscheme_id,
                ~Collection.broader_concepts.any(),
                ~Collection.member_of.any(),
            )
        ).scalars().all()

    def get_all(self, conceptscheme_id):
        """
        Get all concepts and collections in this concept scheme.

        :param conceptscheme_id: a concepscheme id
        :returns: A :class:`list` of
            :class:`skosprovider_sqlalchemy.models.Thing` instances.
        """
        all_results = self.session.execute(
            select(Thing)
            .options(joinedload(Thing.labels))
            .filter(Thing.conceptscheme_id == conceptscheme_id)
        ).unique().scalars().all()
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
        super().__init__(session)

    def get_thing(self, concept_id, conceptscheme_id):
        """

        :param concept_id: a concept id
        :param conceptscheme_id: a conceptscheme id
        :return: the selected thing (Concept or Collection)
        """
        return self.session.execute(
            select(Thing)
            .filter(
                Thing.concept_id == concept_id,
                Thing.conceptscheme_id == conceptscheme_id
            )
        ).scalar_one()

    def save(self, thing):
        """

        :param thing: thing to save
        :return: saved thing
        """
        self.session.add(thing)
        self.session.flush()
        return thing

    def change_type(self, thing, concept_id, conceptscheme_id, new_type, uri):
        self.delete_thing(thing)
        self.session.flush()
        thing = Concept() if new_type == 'concept' else Collection()
        thing.type = new_type
        thing.concept_id = concept_id
        thing.conceptscheme_id = conceptscheme_id
        thing.uri = uri
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
        return self.session.execute(select(list_type)).scalars().all()

    def get_match_type(self, match_type):
        return self.session.execute(
            select(MatchType)
            .filter(MatchType.name == match_type)
        ).scalar_one()

    def get_match(self, uri, matchtype_id, concept_id):
        return self.session.execute(
            select(Match)
            .filter(
                Match.uri == uri,
                Match.matchtype_id == matchtype_id,
                Match.concept_id == concept_id
            )
        ).scalar_one()

    def get_all_label_types(self):
        return self.session.execute(select(LabelType)).scalars().all()

    def get_next_cid(self, conceptscheme_id, id_generation_strategy):
        if id_generation_strategy == IDGenerationStrategy.NUMERIC:
            max_id = self.session.execute(
               select(func.max(sa.cast(Thing.concept_id, sa.Integer)))
               .filter_by(conceptscheme_id=conceptscheme_id)
            ).scalar_one()
            return max_id + 1 if max_id else 1
        elif id_generation_strategy == IDGenerationStrategy.GUID:
            return str(uuid.uuid4())
        else:
            raise ValueError("unsupported id_generation_strategy")


class LanguagesManager(DataManager):
    """
    A :class:`DataManager` for
    :class:`Languages <skosprovider_sqlalchemy.models.Language>.`
    """

    def __init__(self, session):
        super().__init__(session)

    def get(self, language_id):
        return self.session.execute(
            select(Language)
            .filter(Language.id == language_id)
        ).scalar_one()

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
        return self.session.execute(select(Language)).scalars().all()

    def get_all_sorted(self, sort_coll, sort_desc):
        """

        :param sort_coll: sort on this column
        :param sort_desc: descending or not
        :return: sorted list of languages
        """
        if sort_desc:
            return self.session.execute(
                select(Language)
                .order_by(desc(sort_coll))
            ).scalars().all()
        else:
            return self.session.execute(
                select(Language)
                .order_by(sort_coll)
            ).scalars().all()

    def count_languages(self, language_tag):
        return self.session.execute(
            select(func.count(Language.id))
            .filter(Language.id == language_tag)
        ).scalar_one()


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
    def get_most_popular_concepts_for_conceptscheme(
        self, conceptscheme_id, max_results=5, period='last_month'
    ):
        """
        get the most popular concepts for a conceptscheme
        :param conceptscheme_id: id of the conceptscheme
        :param max_results: maximum number of results, default 5
        :param period: 'last_day' or 'last_week' or 'last_month' or 'last_year', default 'last_mont h'
        :return: List of the most popular concepts of a conceptscheme over a certain period
        """

        start_date = self._get_first_day(period)
        rows = self.session.execute(
            select(
                ConceptVisitLog.concept_id,
                func.count(ConceptVisitLog.concept_id).label('count')
            )
            .filter(
                ConceptVisitLog.conceptscheme_id == str(conceptscheme_id),
                ConceptVisitLog.visited_at >= start_date
            )
            .group_by(ConceptVisitLog.concept_id)
            .order_by(desc('count'))
            .limit(max_results)
        ).all()
        results = []
        for row in rows:
            results.append({'concept_id': row.concept_id, 'scheme_id': conceptscheme_id})
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
        recent = self.session.execute(
            select(ConceptschemeCounts)
            .filter(ConceptschemeCounts.conceptscheme_id == conceptscheme_id)
            .order_by(desc('counted_at'))
        ).scalar_one()
        return recent


class ProviderDataManager(DataManager):
    """A data manager for managing Providers."""

    def get_provider_by_id(self, provider_id) -> Provider:
        return self.session.execute(
            select(Provider)
            .filter(Provider.id == provider_id)
        ).scalar_one()

    def get_all_providers(self) -> List[Provider]:
        """
        Retrieve all providers from the database.

        :return: All providers
        """
        return self.session.execute(select(Provider)).scalars().all()
