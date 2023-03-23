"""
Module containing utility functions used by Atramhasis.
"""
import contextlib
import copy
from collections import deque

from pyramid.httpexceptions import HTTPMethodNotAllowed
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source
from skosprovider.uri import UriPatternGenerator
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from sqlalchemy import engine_from_config
from sqlalchemy import orm
from sqlalchemy.orm import sessionmaker

from atramhasis.data.models import Provider


def from_thing(thing):
    """
        Map a :class:`skosprovider_sqlalchemy.models.Thing` to a
        :class:`skosprovider.skos.Concept` or
        a :class:`skosprovider.skos.Collection`, depending on the type.

        :param skosprovider_sqlalchemy.models.Thing thing: Thing to map.
        :rtype: :class:`~skosprovider.skos.Concept` or
            :class:`~skosprovider.skos.Collection`.
        """
    if thing.type and thing.type == 'collection':
        return Collection(
            id=thing.concept_id,
            uri=thing.uri,
            concept_scheme=ConceptScheme(thing.conceptscheme.uri),
            labels=[
                Label(label.label, label.labeltype_id, label.language_id)
                for label in thing.labels
            ],
            notes=[
                Note(n.note, n.notetype_id, n.language_id)
                for n in thing.notes
            ],
            sources=[
                Source(s.citation)
                for s in thing.sources
            ],
            members=[member.concept_id for member in thing.members] if hasattr(thing, 'members') else [],
            member_of=[c.concept_id for c in thing.member_of],
            superordinates=[broader_concept.concept_id for broader_concept in thing.broader_concepts],
            infer_concept_relations=thing.infer_concept_relations
        )
    else:
        matches = {}
        for m in thing.matches:
            key = m.matchtype.name[:m.matchtype.name.find('Match')]
            if key not in matches:
                matches[key] = []
            matches[key].append(m.uri)
        return Concept(
            id=thing.concept_id,
            uri=thing.uri,
            concept_scheme=ConceptScheme(thing.conceptscheme.uri),
            labels=[
                Label(label.label, label.labeltype_id, label.language_id)
                for label in thing.labels
            ],
            notes=[
                Note(n.note, n.notetype_id, n.language_id)
                for n in thing.notes
            ],
            sources=[
                Source(s.citation)
                for s in thing.sources
            ],
            broader=[c.concept_id for c in thing.broader_concepts],
            narrower=[c.concept_id for c in thing.narrower_concepts],
            related=[c.concept_id for c in thing.related_concepts],
            member_of=[c.concept_id for c in thing.member_of],
            subordinate_arrays=[narrower_collection.concept_id for narrower_collection in thing.narrower_collections],
            matches=matches,
        )


def internal_providers_only(fn):
    """
    aspect oriented way to check if provider is internal when calling the decorated function

    :param fn: the decorated function
    :return: around advice
    :raises pyramid.httpexceptions.HTTPMethodNotAllowed: when provider is not internal
    """
    def advice(parent_object, *args, **kw):

        if isinstance(parent_object.provider, SQLAlchemyProvider) and \
                'external' not in parent_object.provider.get_metadata()['subject']:
            return fn(parent_object, *args, **kw)
        else:
            raise HTTPMethodNotAllowed()

    return advice


def update_last_visited_concepts(request, concept_data):
    deque_last_visited = deque(maxlen=4)
    deque_last_visited.extend(request.session.get('last_visited', []))
    try:
        # Try to remove concept from the queue to prevent double entries
        deque_last_visited.remove(concept_data)
    except ValueError:
        # Concept is not in the queue
        pass
    # Add concept to the queue
    deque_last_visited.append(concept_data)
    request.session['last_visited'] = list(deque_last_visited)


def label_sort(concepts, language='any'):
    if not concepts:
        return []
    return sorted(
        concepts, key=lambda concept: concept._sortkey(key='sortlabel',
                                                       language=language)
    )


def db_provider_to_skosprovider(db_provider: Provider) -> SQLAlchemyProvider:
    """Create a SQLAlchemyProvider from a atramhasis.data.models.Provider.

    :param db_provider: The Provider to use as basis for the SQLAlchemyProvider.
    :return: An SQLAlchemyProvider with the data from the `db_provider`
    """
    metadata = copy.deepcopy(db_provider.meta)
    metadata["conceptscheme_id"] = db_provider.conceptscheme_id
    metadata['atramhasis.id_generation_strategy'] = db_provider.id_generation_strategy
    metadata["id"] = db_provider.id
    return SQLAlchemyProvider(
        metadata=metadata,
        session=orm.object_session(db_provider),
        expand_strategy=db_provider.expand_strategy.value,
        uri_generator=UriPatternGenerator(db_provider.uri_pattern),
    )


@contextlib.contextmanager
def db_session(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
