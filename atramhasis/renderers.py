import copy
import csv
from io import StringIO

from pyramid.renderers import JSON
from pyramid_skosprovider.renderers import collection_adapter as skos_collection_adapter
from pyramid_skosprovider.renderers import concept_adapter as skos_concept_adapter
from pyramid_skosprovider.renderers import label_adapter as skos_label_adapter
from pyramid_skosprovider.renderers import note_adapter as skos_note_adapter
from pyramid_skosprovider.renderers import source_adapter as skos_source_adapter
from skosprovider.providers import VocabularyProvider
from skosprovider.skos import Collection as SkosCollection
from skosprovider.skos import Concept as SkosConcept
from skosprovider.skos import Label as SkosLabel
from skosprovider.skos import Note as SkosNote
from skosprovider.skos import Source as SkosSource
from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import Label
from skosprovider_sqlalchemy.models import Language
from skosprovider_sqlalchemy.models import Note
from skosprovider_sqlalchemy.models import Source
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

from atramhasis.data.models import IDGenerationStrategy


class CSVRenderer:
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


json_renderer_verbose = JSON()


def conceptscheme_adapter(obj, request):
    """
    Adapter for rendering a :class:`skosprovider_sqlalchemy.models.ConceptScheme` to json

    :param skosprovider_sqlalchemy.models.ConceptScheme obj: The conceptscheme to be rendered.
    :param request: the current request
    :rtype: :class:`dict`
    """
    scheme_id = request.matchdict['scheme_id']
    provider = request.skos_registry.get_provider(scheme_id)
    language = request.params.get('language', request.locale_name)
    label = obj.label(language)
    return {
        'id': obj.id,
        'uri': obj.uri,
        'label': label.label if label else None,
        'subject': provider.metadata['subject'] if provider.metadata['subject'] else [],
        'labels': obj.labels,
        'notes': obj.notes,
        'languages': obj.languages,
        'sources': obj.sources
    }


def concept_adapter(obj, request):
    """
    Adapter for rendering a :class:`skosprovider_sqlalchemy.models.Concept` to json with verbose relations.

    :param skosprovider_sqlalchemy.models.Concept obj: The concept to be rendered.
    :param request: the current request
    :rtype: :class:`dict`
    """
    matches = {}
    for m in obj.matches:
        key = m.matchtype.name[:m.matchtype.name.find('Match')]
        if key not in matches:
            matches[key] = []
        matches[key].append(m.uri)
    language = request.params.get('language', request.locale_name)
    label = obj.label(language)
    return {
        'id': obj.concept_id,
        'type': obj.type,
        'uri': obj.uri,
        'label': label.label if label else None,
        'labels': obj.labels,
        'notes': obj.notes,
        'sources': obj.sources,
        'broader': [map_relation(c, language) for c in obj.broader_concepts],
        'narrower': [map_relation(c, language) for c in obj.narrower_concepts],
        'related': [map_relation(c, language) for c in obj.related_concepts],
        'member_of': [map_relation(c, language) for c in obj.member_of],
        'subordinate_arrays': [map_relation(c, language) for c in obj.narrower_collections],
        'matches': matches
    }


def collection_adapter(obj, request):
    """
    Adapter for rendering a :class:`skosprovider_sqlalchemy.models.Collection` to json with verbose relations.

    :param skosprovider_sqlalchemy.models.Collection obj: The collection to be rendered.
    :param request: the current request
    :rtype: :class:`dict`
    """
    language = request.params.get('language', request.locale_name)
    label = obj.label(language)
    return {
        'id': obj.concept_id,
        'type': obj.type,
        'uri': obj.uri,
        'label': label.label if label else None,
        'notes': obj.notes,
        'labels': obj.labels,
        'sources': obj.sources,
        'members': [map_relation(c, language) for c in obj.members],
        'member_of': [map_relation(c, language) for c in obj.member_of],
        'superordinates': [map_relation(c, language) for c in obj.broader_concepts],
        'infer_concept_relations': obj.infer_concept_relations
    }


def map_relation(thing, language='any'):
    """
    Map thing in a relation, leaving out the relations (to avoid circular dependencies)
    :param thing: the thing to map
    :param language: language to use for the label
    :rtype: :class:`dict`
    """
    label = thing.label(language)
    return {
        'id': thing.concept_id,
        'type': thing.type,
        'uri': thing.uri,
        'label': label.label if label else None
    }


def label_adapter(obj, request):
    """
    Adapter for rendering a :class:`skosprovider_sqlalchemy.models.Label` to json.

    :param skosprovider_sqlalchemy.models.Label obj: The label to be rendered.
    :param request: the current request
    :rtype: :class:`dict`
    """
    return {
        'label': obj.label,
        'type': obj.labeltype_id,
        'language': obj.language_id
    }


def note_adapter(obj, request):
    """
    Adapter for rendering a :class:`skosprovider_sqlalchemy.models.Note` to json.

    :param skosprovider_sqlalchemy.models.Note obj: The note to be rendered.
    :param request: the current request
    :rtype: :class:`dict`
    """
    return {
        'note': obj.note,
        'type': obj.notetype_id,
        'language': obj.language_id
    }


def source_adapter(obj, request):
    """
    Adapter for rendering a :class:`skosprovider_sqlalchemy.models.Source` to json.

    :param skosprovider_sqlalchemy.models.Source obj: The source to be rendered.
    :param request: the current request
    :rtype: :class:`dict`
    """
    return {
        'citation': obj.citation
    }


def language_adaptor(obj, request):
    """
    Adapter for rendering a :class:`skosprovider_sqlalchemy.models.Language` to json.

    :param skosprovider_sqlalchemy.models.Language obj: The language to be rendered.
    :param request: the current request
    :rtype: :class:`dict`
    """
    return {
        'id': obj.id,
        'name': obj.name
    }


def provider_adapter(provider: VocabularyProvider, *_):
    if provider.uri_generator:
        uri_pattern = provider.uri_generator.pattern
    else:
        uri_pattern = None

    metadata = copy.deepcopy(provider.metadata)
    metadata.pop('id', None)
    metadata.pop('conceptscheme_id', None)
    data = {
        'id': provider.metadata['id'],
        'type': provider.__class__.__name__,
        'conceptscheme_uri': provider.concept_scheme.uri,
        'uri_pattern': uri_pattern,
        'default_language': metadata.pop("default_language", None),
        'subject': metadata.pop("subject", None),
        'force_display_language': metadata.pop("atramhasis.force_display_language", None),
        'metadata': metadata,
    }
    return data


def sa_provider_adapter(provider: SQLAlchemyProvider, *args):
    data = provider_adapter(provider, *args)
    strategy = data["metadata"].pop(
       "atramhasis.id_generation_strategy", IDGenerationStrategy.NUMERIC
    )
    data['id_generation_strategy'] = strategy.name
    data['expand_strategy'] = provider.expand_strategy
    return data


json_renderer_verbose.add_adapter(ConceptScheme, conceptscheme_adapter)
json_renderer_verbose.add_adapter(Concept, concept_adapter)
json_renderer_verbose.add_adapter(Collection, collection_adapter)
json_renderer_verbose.add_adapter(Label, label_adapter)
json_renderer_verbose.add_adapter(Note, note_adapter)
json_renderer_verbose.add_adapter(Source, source_adapter)
json_renderer_verbose.add_adapter(Language, language_adaptor)
json_renderer_verbose.add_adapter(SkosConcept, skos_concept_adapter)
json_renderer_verbose.add_adapter(SkosCollection, skos_collection_adapter)
json_renderer_verbose.add_adapter(SkosLabel, skos_label_adapter)
json_renderer_verbose.add_adapter(SkosNote, skos_note_adapter)
json_renderer_verbose.add_adapter(SkosSource, skos_source_adapter)
json_renderer_verbose.add_adapter(VocabularyProvider, provider_adapter)
json_renderer_verbose.add_adapter(SQLAlchemyProvider, sa_provider_adapter)
