import types
from unittest.mock import Mock

import pytest
from pyramid import testing
from skosprovider.providers import VocabularyProvider
from skosprovider.registry import Registry
from skosprovider_getty.providers import AATProvider
from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import Label
from skosprovider_sqlalchemy.models import Language
from skosprovider_sqlalchemy.models import Match
from skosprovider_sqlalchemy.models import MatchType
from skosprovider_sqlalchemy.models import Note
from skosprovider_sqlalchemy.models import Source
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider

from atramhasis import renderers
from atramhasis.renderers import collection_adapter
from atramhasis.renderers import concept_adapter
from atramhasis.renderers import conceptscheme_adapter
from atramhasis.renderers import label_adapter
from atramhasis.renderers import language_adaptor
from atramhasis.renderers import map_relation
from atramhasis.renderers import note_adapter
from atramhasis.renderers import source_adapter
from fixtures.data import trees


@pytest.fixture()
def renderer_data():
    concept = Concept()
    concept.id = 11
    concept.concept_id = 101
    concept.uri = "urn:x-atramhasis-demo:TREES:101"
    concept.conceptscheme_id = 1

    notes = []
    note = Note(note="test note", notetype_id="example", language_id="en")
    note2 = Note(note="note def", notetype_id="definition", language_id="en")
    notes.append(note)
    notes.append(note2)
    concept.notes = notes

    labels = []
    label = Label(label="een label", labeltype_id="prefLabel", language_id="nl")
    label2 = Label(label="other label", labeltype_id="altLabel", language_id="en")
    label3 = Label(
        label="and some other label", labeltype_id="altLabel", language_id="en"
    )
    labels.append(label)
    labels.append(label2)
    labels.append(label3)
    concept.labels = labels

    sources = []
    source = Source("Van Daele K. 2009")
    sources.append(source)
    concept.sources = sources

    matches = []
    match = Match()
    match.matchtype = MatchType(name="closeMatch", description="test")
    match.uri = "urn:somethingelse:st1"
    matches.append(match)
    match2 = Match()
    match2.matchtype = MatchType(name="closeMatch", description="test")
    match2.uri = "urn:somethingelse:st2"
    matches.append(match2)
    match3 = Match()
    match3.matchtype = MatchType(name="exactMatch", description="test")
    match3.uri = "urn:something:thingy"
    matches.append(match3)
    concept.matches = matches

    collection = Collection()
    collection.id = 12
    collection.concept_id = 102
    collection.uri = "urn:x-atramhasis-demo:TREES:102"
    collection.conceptscheme_id = 1

    conceptscheme = ConceptScheme()
    conceptscheme.id = 1
    conceptscheme.labels = labels
    conceptscheme.notes = notes
    conceptscheme.sources = sources
    conceptscheme.uri = None

    regis = Registry()
    regis.register_provider(trees)
    request = testing.DummyRequest()
    request.skos_registry = regis
    request.matchdict = {"scheme_id": "TREES"}
    request.locale_name = "nl"

    concept.member_of.add(collection)
    collection.members.add(concept)

    return types.SimpleNamespace(
        concept=concept,
        collection=collection,
        conceptscheme=conceptscheme,
        regis=regis,
        request=request,
    )


class TestJsonRenderer:
    def test_label_adapter(self, renderer_data):
        label = renderer_data.concept.labels[2]
        label = label_adapter(label, {})
        assert isinstance(label, dict)
        assert label["label"] == "and some other label"
        assert label["type"] == "altLabel"
        assert label["language"] == "en"

    def test_note_adapter(self, renderer_data):
        n = renderer_data.concept.notes[0]
        note = note_adapter(n, {})
        assert isinstance(note, dict)
        assert note["note"] == "test note"
        assert note["type"] == "example"
        assert note["language"] == "en"

    def test_source_adapter(self, renderer_data):
        s = renderer_data.concept.sources[0]
        source = source_adapter(s, {})
        assert isinstance(source, dict)
        assert source["citation"] == "Van Daele K. 2009"

    def test_concept_adapter(self, renderer_data):
        c = renderer_data.concept
        concept = concept_adapter(c, renderer_data.request)
        assert isinstance(concept, dict)
        assert concept["id"] == 101
        assert concept["type"] == "concept"
        assert concept["uri"] == "urn:x-atramhasis-demo:TREES:101"
        assert concept["label"] is not None
        assert isinstance(concept["labels"], list)
        assert len(concept["labels"]) == 3
        assert isinstance(concept["notes"], list)
        assert len(concept["notes"]) == 2
        assert isinstance(concept["sources"], list)
        assert len(concept["sources"]) == 1
        assert isinstance(concept["member_of"], list)
        assert len(concept["member_of"]) == 1
        assert isinstance(concept["narrower"], list)
        assert len(concept["narrower"]) == 0
        assert isinstance(concept["broader"], list)
        assert len(concept["broader"]) == 0
        assert isinstance(concept["related"], list)
        assert len(concept["related"]) == 0
        assert isinstance(concept["matches"], dict)
        assert len(concept["matches"]["exact"]) == 1
        assert len(concept["matches"]["close"]) == 2

    def test_collection_adapter(self, renderer_data):
        c = renderer_data.collection
        collection = collection_adapter(c, renderer_data.request)
        assert isinstance(collection, dict)
        assert collection["id"] == 102
        assert collection["type"] == "collection"
        assert collection["uri"] == "urn:x-atramhasis-demo:TREES:102"
        assert collection["label"] is None
        assert isinstance(collection["labels"], list)
        assert len(collection["labels"]) == 0
        assert isinstance(collection["member_of"], list)
        assert len(collection["member_of"]) == 0
        assert isinstance(collection["members"], list)
        assert len(collection["members"]) == 1

    def test_map_relation_concept(self, renderer_data):
        c = renderer_data.concept
        relation = map_relation(c)
        assert isinstance(relation, dict)
        assert relation["id"] == 101
        assert relation["type"] == "concept"
        assert relation["uri"] == "urn:x-atramhasis-demo:TREES:101"
        assert relation["label"] is not None
        with pytest.raises(KeyError):
            relation["notes"]
        with pytest.raises(KeyError):
            relation["member_of"]
        with pytest.raises(KeyError):
            relation["narrower"]
        with pytest.raises(KeyError):
            relation["broader"]
        with pytest.raises(KeyError):
            relation["related"]

    def test_map_relation_collection(self, renderer_data):
        c = renderer_data.collection
        relation = map_relation(c)
        assert isinstance(relation, dict)
        assert relation["id"] == 102
        assert relation["type"] == "collection"
        assert relation["uri"] == "urn:x-atramhasis-demo:TREES:102"
        assert relation["label"] is None
        with pytest.raises(KeyError):
            relation["members"]
        with pytest.raises(KeyError):
            relation["member_of"]

    def test_language_adaptor(self):
        language = Language(id="af", name="Afrikaans")
        res = language_adaptor(language, None)
        assert res is not None
        assert isinstance(res, dict)
        assert res["id"] == "af"
        assert res["name"] == "Afrikaans"

    def test_conceptscheme_adapter(self, renderer_data):
        c = renderer_data.conceptscheme
        conceptscheme = conceptscheme_adapter(c, renderer_data.request)
        assert len(conceptscheme["notes"]) > 0
        assert len(conceptscheme["labels"]) > 0
        assert len(conceptscheme["sources"]) > 0
        assert conceptscheme["uri"] is None
        assert "een label" == conceptscheme["label"]
        assert 1 == conceptscheme["id"]
        assert 0 == len(conceptscheme["subject"])
        assert isinstance(conceptscheme, dict)

    def test_conceptscheme_language_handling(self, renderer_data):
        c = renderer_data.conceptscheme
        conceptscheme = conceptscheme_adapter(c, renderer_data.request)
        assert "een label" == conceptscheme["label"]
        renderer_data.request.locale_name = "en"
        conceptscheme = conceptscheme_adapter(c, renderer_data.request)
        assert conceptscheme["label"] in ["other label", "and some other label"]

    def test_provider_adapter(self):
        provider = VocabularyProvider(
            metadata={
                "id": "provider-id",
                "default_language": "nl-be",
                "subject": "sub",
                "atramhasis.force_display_language": "force-nl",
            }
        )
        result = renderers.provider_adapter(provider)
        assert {
            "conceptscheme_uri": "urn:x-skosprovider:provider-id",
            "default_language": "nl-be",
            "force_display_language": "force-nl",
            "id": "provider-id",
            "subject": "sub",
            "type": "VocabularyProvider",
            "uri_pattern": "urn:x-skosprovider:%s:%s",
            "metadata": {},
        } == result

    def test_provider_adapter_aat_provider(self):
        provider = AATProvider(
            metadata={
                "id": "provider-id",
                "default_language": "nl-be",
                "subject": "sub",
                "atramhasis.force_display_language": "force-nl",
            }
        )
        result = renderers.provider_adapter(provider)
        assert {
            "conceptscheme_uri": "http://vocab.getty.edu/aat/",
            "default_language": "nl-be",
            "force_display_language": "force-nl",
            "id": "provider-id",
            "subject": "sub",
            "type": "AATProvider",
            "uri_pattern": None,
            "metadata": {"uri": "http://vocab.getty.edu/aat/"},
        } == result

    def test_provider_adapter_sqlalchemy_provider(self):
        sessionmaker = Mock()
        session = sessionmaker()
        session.get.return_value = ConceptScheme(
            id=1,
            uri="urn:x-skosprovider:trees",
            labels=[
                Label("Verschillende soorten bomen", "prefLabel", "nl"),
                Label("Different types of trees", "prefLabel", "en"),
            ],
        )
        provider = SQLAlchemyProvider(
            metadata={
                "id": "provider-id",
                "default_language": "nl-be",
                "subject": "sub",
                "atramhasis.force_display_language": "force-nl",
                "conceptscheme_id": 1,
            },
            session=sessionmaker,
        )
        result = renderers.sa_provider_adapter(provider)
        assert {
            "conceptscheme_uri": "urn:x-skosprovider:trees",
            "default_language": "nl-be",
            "force_display_language": "force-nl",
            "id": "provider-id",
            "expand_strategy": "recurse",
            "id_generation_strategy": "NUMERIC",
            "subject": "sub",
            "type": "SQLAlchemyProvider",
            "uri_pattern": "urn:x-skosprovider:%s:%s",
            "metadata": {},
        } == result
