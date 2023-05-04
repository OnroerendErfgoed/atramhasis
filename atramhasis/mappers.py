"""
Module containing mapping functions used by Atramhasis.
"""

from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import Label
from skosprovider_sqlalchemy.models import Match
from skosprovider_sqlalchemy.models import Note
from skosprovider_sqlalchemy.models import Source
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from sqlalchemy.exc import NoResultFound

from atramhasis.data.models import ExpandStrategy
from atramhasis.data.models import IDGenerationStrategy
from atramhasis.data.models import Provider


def is_html(value):
    """
    Check if a value has html inside. Only tags checked <strong> <em> <a>.

    :param value: a string
    :return: a boolean (True, HTML present | False, no HTML present)
    """
    tag_list = ['<strong>', '<em>', '<a>', '</strong>', '</em>', '</a>', '<a']
    return any(tag in value for tag in tag_list)


def map_concept(concept, concept_json, skos_manager):
    """
    Map a concept from json to the database.

    :param skosprovider_sqlalchemy.models.Thing concept: A concept or
        collection as known to the database.
    :param dict concept_json: A dict representing the json sent to our REST
        service.
    :param skos_manager: A skos_manager to acces db operations
    :returns: The :class:`skosprovider_sqlalchemy.models.Thing` enhanced
        with the information from the json object.
    """
    concept_json_type = concept_json.get('type', None)
    if concept.type != concept_json_type:

        if concept_json_type == 'concept':
            members = concept.members
            concept = skos_manager.change_type(
                concept,
                concept.concept_id,
                concept.conceptscheme_id,
                concept_json_type,
                concept.uri
            )
            for member in members:
                if member.type == 'concept':
                    concept.narrower_concepts.add(member)
                elif member.type == 'collection':
                    concept.narrower_collections.add(member)
        elif concept_json_type == 'collection':
            narrower_concepts = concept.narrower_concepts
            narrower_collections = concept.narrower_collections
            concept = skos_manager.change_type(
                concept,
                concept.concept_id,
                concept.conceptscheme_id,
                concept_json_type,
                concept.uri
            )
            for narrower_concept in narrower_concepts:
                concept.members.add(narrower_concept)
            for narrower_collection in narrower_collections:
                concept.members.add(narrower_collection)
    elif concept_json_type == 'collection':
        concept.members.clear()
    elif concept_json_type == 'concept':
        concept.narrower_collections.clear()
        concept.narrower_concepts.clear()
    if concept.type in ('concept', 'collection'):
        concept.labels[:] = []
        labels = concept_json.get('labels', [])
        for label in labels:
            label = Label(
                label=label.get('label', ''),
                labeltype_id=label.get('type', ''),
                language_id=label.get('language', ''),
            )
            concept.labels.append(label)
        concept.notes[:] = []
        notes = concept_json.get('notes', [])
        for n in notes:
            note = Note(note=n.get('note', ''), notetype_id=n.get('type', ''), language_id=n.get('language', ''))
            if is_html(note.note):
                note.markup = 'HTML'
            concept.notes.append(note)
        concept.sources[:] = []
        sources = concept_json.get('sources', [])
        for s in sources:
            source = Source(citation=s.get('citation', ''))
            if is_html(source.citation):
                source.markup = 'HTML'
            concept.sources.append(source)

        concept.member_of.clear()
        member_of = concept_json.get('member_of', [])
        for memberof in member_of:
            try:
                memberof_collection = skos_manager.get_thing(
                    concept_id=memberof['id'],
                    conceptscheme_id=concept.conceptscheme_id)
            except NoResultFound:
                memberof_collection = Collection(concept_id=memberof['id'], conceptscheme_id=concept.conceptscheme_id)
            concept.member_of.add(memberof_collection)

        if concept.type == 'concept':
            concept.related_concepts.clear()
            related = concept_json.get('related', [])
            for related in related:
                try:
                    related_concept = skos_manager.get_thing(
                        concept_id=related['id'],
                        conceptscheme_id=concept.conceptscheme_id)
                except NoResultFound:
                    related_concept = Concept(concept_id=related['id'], conceptscheme_id=concept.conceptscheme_id)
                concept.related_concepts.add(related_concept)

            concept.broader_concepts.clear()
            broader = concept_json.get('broader', [])
            for broader in broader:
                try:
                    broader_concept = skos_manager.get_thing(
                        concept_id=broader['id'],
                        conceptscheme_id=concept.conceptscheme_id)
                except NoResultFound:
                    broader_concept = Concept(concept_id=broader['id'], conceptscheme_id=concept.conceptscheme_id)
                concept.broader_concepts.add(broader_concept)
            narrower = concept_json.get('narrower', [])
            for narrower in narrower:
                try:
                    narrower_concept = skos_manager.get_thing(
                        concept_id=narrower['id'],
                        conceptscheme_id=concept.conceptscheme_id)
                except NoResultFound:
                    narrower_concept = Concept(concept_id=narrower['id'], conceptscheme_id=concept.conceptscheme_id)
                concept.narrower_concepts.add(narrower_concept)

            matches = []
            matchdict = concept_json.get('matches', {})
            for match_type, uris in matchdict.items():
                db_type = match_type + "Match"
                match_type = skos_manager.get_match_type(db_type)
                for uri in uris:
                    concept_id = concept_json.get('id', -1)
                    try:
                        match = skos_manager.get_match(uri=uri, matchtype_id=match_type.name,
                                                       concept_id=concept_id)
                    except NoResultFound:
                        match = Match()
                        match.matchtype = match_type
                        match.uri = uri
                    matches.append(match)
            concept.matches = matches

            narrower_collections = concept_json.get('subordinate_arrays', [])
            for narrower in narrower_collections:
                try:
                    narrower_collection = skos_manager.get_thing(
                        concept_id=narrower['id'],
                        conceptscheme_id=concept.conceptscheme_id)
                except NoResultFound:
                    narrower_collection = Collection(concept_id=narrower['id'],
                                                     conceptscheme_id=concept.conceptscheme_id)
                concept.narrower_collections.add(narrower_collection)

        if concept.type == 'collection':
            members = concept_json.get('members', [])
            for member in members:
                try:
                    member_concept = skos_manager.get_thing(
                        concept_id=member['id'],
                        conceptscheme_id=concept.conceptscheme_id)
                except NoResultFound:
                    member_concept = Concept(concept_id=member['id'], conceptscheme_id=concept.conceptscheme_id)
                concept.members.add(member_concept)

            concept.broader_concepts.clear()
            broader_concepts = concept_json.get('superordinates', [])
            for broader in broader_concepts:
                try:
                    broader_concept = skos_manager.get_thing(
                        concept_id=broader['id'],
                        conceptscheme_id=concept.conceptscheme_id)
                except NoResultFound:
                    broader_concept = Concept(concept_id=broader['id'], conceptscheme_id=concept.conceptscheme_id)
                concept.broader_concepts.add(broader_concept)
            if 'infer_concept_relations' in concept_json:
                concept.infer_concept_relations = concept_json['infer_concept_relations']
    return concept


def map_conceptscheme(conceptscheme, conceptscheme_json):
    """
    Map a conceptscheme from json to the database.

    :param skosprovider_sqlalchemy.models.ConceptScheme conceptscheme: A conceptscheme as known to the database.
    :param dict conceptscheme_json: A dict representing the json sent to our REST
        service.
    :returns: The :class:`skosprovider_sqlalchemy.models.ConceptScheme` enhanced
        with the information from the json object.
    """
    conceptscheme.labels[:] = []
    labels = conceptscheme_json.get('labels', [])
    for label in labels:
        label = Label(
            label=label.get('label', ''),
            labeltype_id=label.get('type', ''),
            language_id=label.get('language', ''),
        )
        conceptscheme.labels.append(label)
    conceptscheme.notes[:] = []
    notes = conceptscheme_json.get('notes', [])
    for n in notes:
        note = Note(note=n.get('note', ''), notetype_id=n.get('type', ''), language_id=n.get('language', ''))
        conceptscheme.notes.append(note)
    conceptscheme.sources[:] = []
    sources = conceptscheme_json.get('sources', [])
    for s in sources:
        source = Source(citation=s.get('citation', ''))
        conceptscheme.sources.append(source)
    return conceptscheme


def map_provider(provider_json: dict, provider: Provider = None) -> Provider:
    """
    Create a atramhasis.data.models.Provider from json data.

    An existing provider can optionally be passed. When passed this one will be updated.

    :param provider_json: JSON data as a dict.
    :param provider: A provider which will be updated with the JSON data. When None
       a new Provider instance will be returned.
    :return: A Provider set with data from the JSON.
    """
    if provider is None:
        # Only executed on creation.
        provider = Provider()
        provider.conceptscheme = ConceptScheme(uri=provider_json['conceptscheme_uri'])
        provider.id = provider_json.get("id")

    provider.meta = provider_json.get("metadata") or {}
    provider.default_language = provider_json.get("default_language")
    provider.force_display_language = provider_json.get("force_display_language")
    provider.id_generation_strategy = IDGenerationStrategy[
        provider_json.get("id_generation_strategy") or 'NUMERIC'
    ]
    provider.subject = provider_json.get("subject") or []
    provider.uri_pattern = provider_json["uri_pattern"]
    provider.expand_strategy = ExpandStrategy[
        (provider_json.get("expand_strategy") or 'RECURSE').upper()
    ]
    return provider
