import copy
from unittest.mock import Mock

import pytest
from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import Label
from skosprovider_sqlalchemy.models import Match
from skosprovider_sqlalchemy.models import MatchType
from skosprovider_sqlalchemy.models import Source
from sqlalchemy.exc import NoResultFound

from atramhasis import mappers
from atramhasis.data.models import ExpandStrategy
from atramhasis.data.models import IDGenerationStrategy
from atramhasis.data.models import Provider
from atramhasis.mappers import map_concept
from atramhasis.mappers import map_conceptscheme

_test_json = {
    "narrower": [{"id": 8}, {"id": 7}, {"id": 9}],
    "label": "Belgium",
    "type": "concept",
    "id": 4,
    "broader": [{"id": 2}, {"id": 11}],
    "related": [{"id": 5}, {"id": 12}],
    "member_of": [{"id": 999}],
    "labels": [
        {"label": "Belgium", "type": "prefLabel", "language": "en"},
        {"label": "België", "type": "prefLabel", "language": "nl"},
    ],
    "notes": [{"note": "een notitie", "type": "note", "language": "nl"}],
    "sources": [{"citation": "Atlas."}],
}
_json_collection = {
    "id": 0,
    "labels": [{"language": "nl", "label": "Stijlen en culturen", "type": "prefLabel"}],
    "type": "collection",
    "label": "Stijlen en culturen",
    "members": [{"id": 61}, {"id": 60}, {"id": 12}],
    "member_of": [{"id": 999}, {"id": 7}],
    "notes": [{"note": "een notitie", "type": "note", "language": "nl"}],
}
test_json_conceptscheme = {
    "label": "Stijlen en culturen",
    "labels": [{"language": "nl", "label": "Stijlen en culturen", "type": "prefLabel"}],
    "notes": [{"note": "een notitie", "type": "note", "language": "nl"}],
    "sources": [{"citation": "Atlas."}],
}
test_json_html = {
    "narrower": [{"id": 8}, {"id": 7}, {"id": 9}],
    "label": "Belgium",
    "type": "concept",
    "id": 4,
    "broader": [{"id": 2}, {"id": 11}],
    "related": [{"id": 5}, {"id": 12}],
    "member_of": [{"id": 999}],
    "labels": [
        {"label": "Belgium", "type": "prefLabel", "language": "en"},
        {"label": "België", "type": "prefLabel", "language": "nl"},
    ],
    "notes": [
        {"note": "een <a href='#'>notitie</a>", "type": "note", "language": "nl"}
    ],
    "sources": [{"citation": "<em>Atlas.</em>"}],
}


class DummySkosManager:
    def get_thing(self, concept_id, conceptscheme_id):
        if concept_id in (7, 11, 12):
            raise NoResultFound()
        if concept_id in (999, 19):
            return Collection(
                id=concept_id, concept_id=concept_id, conceptscheme_id=conceptscheme_id
            )
        else:
            return Concept(
                id=concept_id, concept_id=concept_id, conceptscheme_id=conceptscheme_id
            )

    def change_type(self, _, concept_id, conceptscheme_id, new_type, uri):
        thing = Concept() if new_type == "concept" else Collection()
        thing.type = new_type
        thing.concept_id = concept_id
        thing.conceptscheme_id = conceptscheme_id
        thing.uri = uri
        return thing

    def get_match_type(self, *_, **__):
        return Mock()

    def get_match(self, uri, matchtype_id, concept_id):
        if concept_id == -1:
            raise NoResultFound()
        else:
            match = Match()
            match.uri = uri
            match.concept_id = concept_id
            if matchtype_id in [
                "broadMatch",
                "closeMatch",
                "exactMatch",
                "narrowMatch",
                "relatedMatch",
            ]:
                match.matchtype = MatchType(matchtype_id, "test")
                return match
            else:
                raise NoResultFound()


@pytest.fixture()
def skos_manager():
    return DummySkosManager()


@pytest.fixture()
def mapper_concept():
    concept = Concept()
    concept.concept_id = 1
    concept.conceptscheme_id = 1
    member_concept_1 = Concept()
    member_concept_1.concept_id = 5
    member_concept_1.conceptscheme_id = 1
    member_concept_2 = Collection()
    member_concept_2.concept_id = 6
    member_concept_2.conceptscheme_id = 1
    concept.narrower_concepts.add(member_concept_1)
    concept.narrower_collections.add(member_concept_2)
    return concept


@pytest.fixture()
def mapper_collection():
    collection = Collection()
    collection.concept_id = 0
    collection.conceptscheme_id = 1
    collection.uri = "urn:x-skosprovider:trees/3"
    member_concept_1 = Concept()
    member_concept_1.concept_id = 5
    member_concept_1.conceptscheme_id = 1
    member_concept_2 = Collection()
    member_concept_2.concept_id = 6
    member_concept_2.conceptscheme_id = 1
    collection.members.add(member_concept_1)
    collection.members.add(member_concept_2)
    return collection


@pytest.fixture()
def mapper_conceptscheme():
    conceptscheme = ConceptScheme()
    conceptscheme.id = 1
    return conceptscheme


@pytest.fixture()
def test_json():
    return copy.deepcopy(_test_json)


@pytest.fixture()
def json_collection():
    return copy.deepcopy(_json_collection)


class TestMappers:
    def test_mapping(self, mapper_concept, test_json, skos_manager):
        result_concept = map_concept(mapper_concept, test_json, skos_manager)
        assert result_concept is not None
        assert 3 == len(result_concept.narrower_concepts)
        assert 2 == len(result_concept.broader_concepts)
        assert 2 == len(result_concept.related_concepts)
        assert 1 == len(result_concept.member_of)
        assert 2 == len(result_concept.labels)
        assert 1 == len(result_concept.notes)
        assert 1 == len(result_concept.sources)
        assert not hasattr(result_concept, "members")
        assert result_concept.notes[0].markup is None

    def test_mapping_collections_filled(self, mapper_concept, test_json, skos_manager):
        label = Label(label="test", labeltype_id="altLabel", language_id="nl")
        mapper_concept.labels.append(label)
        related_concept = Concept(concept_id=6, conceptscheme_id=1)
        mapper_concept.related_concepts.add(related_concept)
        source = Source(citation="testCitation")
        mapper_concept.sources.append(source)
        source = Source(citation="AnotherTestCitation")
        mapper_concept.sources.append(source)
        result_concept = map_concept(mapper_concept, test_json, skos_manager)
        assert 3 == len(result_concept.narrower_concepts)
        assert 2 == len(result_concept.broader_concepts)
        assert 2 == len(result_concept.related_concepts)
        assert 1 == len(result_concept.member_of)
        assert 2 == len(result_concept.labels)
        assert 1 == len(result_concept.notes)
        assert 1 == len(result_concept.sources)

    def test_mapping_check_db_lookup(self, mapper_concept, test_json, skos_manager):
        result_concept = map_concept(mapper_concept, test_json, skos_manager)
        for narrower_concept in result_concept.narrower_concepts:
            assert narrower_concept is not None
            if narrower_concept.concept_id == 7:
                assert narrower_concept.id is None

    def test_mapping_check_db_lookup_member_of(
        self, mapper_concept, test_json, skos_manager
    ):
        result_concept = map_concept(mapper_concept, test_json, skos_manager)
        for member_of in result_concept.member_of:
            assert member_of is not None
            if member_of.concept_id == 7:
                assert member_of.id is None

    def test_mapping_collection(self, mapper_collection, json_collection, skos_manager):
        result_collection = map_concept(
            mapper_collection, json_collection, skos_manager
        )
        assert result_collection is not None
        assert 3 == len(result_collection.members)
        assert 2 == len(result_collection.member_of)
        assert 1 == len(result_collection.labels)
        assert 1 == len(result_collection.notes)
        assert not hasattr(result_collection, "related_concepts")

    def test_mapping_matches(self, mapper_concept, test_json, skos_manager):
        test_json["matches"] = {
            "exact": ["urn:sample:666"],
            "broad": ["urn:somewhere:93"],
        }
        result_concept = map_concept(mapper_concept, test_json, skos_manager)
        assert result_concept is not None
        assert hasattr(result_concept, "matches")
        assert 2 == len(result_concept.matches)
        assert result_concept.matches[0].uri in ["urn:sample:666", "urn:somewhere:93"]

    def test_mapping_matches_new_concept(self, mapper_concept, test_json, skos_manager):
        test_json["matches"] = {
            "exact": ["urn:sample:666"],
            "broad": ["urn:somewhere:93"],
        }
        del test_json["id"]
        result_concept = map_concept(mapper_concept, test_json, skos_manager)
        assert result_concept is not None
        assert hasattr(result_concept, "matches")
        assert 2 == len(result_concept.matches)
        assert result_concept.matches[0].uri in ["urn:sample:666", "urn:somewhere:93"]

    def test_mapping_subordinate_arrays(self, mapper_concept, test_json, skos_manager):
        test_json["subordinate_arrays"] = [{"id": 19}]
        result_concept = map_concept(mapper_concept, test_json, skos_manager)
        assert result_concept is not None
        assert hasattr(result_concept, "narrower_collections")
        assert 1 == len(result_concept.narrower_collections)
        assert [c for c in result_concept.narrower_collections][0].concept_id == 19

    def test_mapping_subordinate_arrays_no_result(
        self, mapper_concept, test_json, skos_manager
    ):
        test_json["subordinate_arrays"] = [{"id": 11}]
        result_concept = map_concept(mapper_concept, test_json, skos_manager)
        assert result_concept is not None
        assert hasattr(result_concept, "narrower_collections")
        assert 1 == len(result_concept.narrower_collections)
        assert [c for c in result_concept.narrower_collections][0].concept_id == 11

    def test_mapping_superordinates(
        self, mapper_collection, json_collection, skos_manager
    ):
        json_collection["superordinates"] = [{"id": 12}]
        result_collection = map_concept(
            mapper_collection, json_collection, skos_manager
        )
        assert result_collection is not None
        assert hasattr(result_collection, "broader_concepts")
        assert 1 == len(result_collection.broader_concepts)
        assert [c for c in result_collection.broader_concepts][0].concept_id == 12

    def test_mapping_concept_to_collection(
        self, mapper_concept, json_collection, skos_manager
    ):
        result_collection = map_concept(mapper_concept, json_collection, skos_manager)
        assert result_collection is not None
        assert hasattr(result_collection, "members")
        assert not hasattr(result_collection, "related_concepts")
        assert not hasattr(result_collection, "narrower_concepts")
        assert not hasattr(result_collection, "narrower_collections")

    def test_mapping_collection_to_concept(
        self, mapper_collection, test_json, skos_manager
    ):
        result_concept = map_concept(mapper_collection, test_json, skos_manager)
        assert result_concept is not None
        assert not hasattr(result_concept, "members")
        assert hasattr(result_concept, "related_concepts")
        assert hasattr(result_concept, "narrower_concepts")
        assert hasattr(result_concept, "narrower_collections")
        assert result_concept.uri == "urn:x-skosprovider:trees/3"

    def test_mapping_conceptscheme(self, mapper_conceptscheme):
        result_conceptscheme = map_conceptscheme(
            mapper_conceptscheme, test_json_conceptscheme
        )
        assert result_conceptscheme is not None
        assert 1 == len(result_conceptscheme.labels)
        assert 1 == len(result_conceptscheme.notes)
        assert 1 == len(result_conceptscheme.sources)

    def test_mapping_html_note(self, mapper_concept, skos_manager):
        result_concept = map_concept(mapper_concept, test_json_html, skos_manager)
        assert result_concept is not None
        assert 3 == len(result_concept.narrower_concepts)
        assert 2 == len(result_concept.broader_concepts)
        assert 2 == len(result_concept.related_concepts)
        assert 1 == len(result_concept.member_of)
        assert 2 == len(result_concept.labels)
        assert 1 == len(result_concept.notes)
        assert 1 == len(result_concept.sources)
        assert not hasattr(result_concept, "members")
        assert "HTML" == result_concept.notes[0].markup
        assert "HTML" == result_concept.sources[0].markup


def test_map_provider_new_provider_full():
    data = {
        "metadata": {"meta": "meta"},
        "default_language": "nl",
        "force_display_language": "nl-force",
        "id_generation_strategy": "GUID",
        "subject": ["hidden"],
        "uri_pattern": "uri-pattern",
        "expand_strategy": "visit",
        "conceptscheme_uri": "conceptscheme-uri",
        "id": "p-id",
    }
    result = mappers.map_provider(data)
    assert result.conceptscheme is not None
    assert result.conceptscheme.uri == "conceptscheme-uri"
    assert result.id == "p-id"
    assert result.meta == {
        "atramhasis.force_display_language": "nl-force",
        "atramhasis.id_generation_strategy": "GUID",
        "default_language": "nl",
        "meta": "meta",
        "subject": ["hidden"],
    }
    assert result.default_language == "nl"
    assert result.force_display_language == "nl-force"
    assert result.id_generation_strategy is IDGenerationStrategy.GUID
    assert result.subject == ["hidden"]
    assert result.uri_pattern == "uri-pattern"
    assert result.expand_strategy is ExpandStrategy.VISIT


def test_map_provider_new_provider_minimal():
    data = {
        "conceptscheme_uri": "conceptscheme-uri",
        "uri_pattern": "uri-pattern",
    }
    result = mappers.map_provider(data)
    assert result.conceptscheme is not None
    assert result.conceptscheme.uri == "conceptscheme-uri"
    assert result.id is None
    assert result.meta == {
        "atramhasis.force_display_language": None,
        "atramhasis.id_generation_strategy": "NUMERIC",
        "default_language": None,
        "subject": [],
    }
    assert result.default_language is None
    assert result.force_display_language is None
    assert result.id_generation_strategy is IDGenerationStrategy.NUMERIC
    assert result.subject == []
    assert result.uri_pattern == "uri-pattern"
    assert result.expand_strategy is ExpandStrategy.RECURSE


def test_map_provider_existing():
    data = {
        "metadata": {"meta": "meta"},
        "default_language": "nl",
        "force_display_language": "nl-force",
        "id_generation_strategy": "GUID",
        "subject": ["hidden"],
        "uri_pattern": "uri-pattern",
        "expand_strategy": "visit",
        "id": "p-id",
    }
    existing = Provider(id="exists")
    result = mappers.map_provider(data, existing)
    assert result is existing
    assert result.conceptscheme is None
    assert result.id == "exists"
    assert result.meta == {
        "atramhasis.force_display_language": "nl-force",
        "atramhasis.id_generation_strategy": "GUID",
        "default_language": "nl",
        "meta": "meta",
        "subject": ["hidden"],
    }
    assert result.default_language == "nl"
    assert result.force_display_language == "nl-force"
    assert result.id_generation_strategy is IDGenerationStrategy.GUID
    assert result.subject == ["hidden"]
    assert result.uri_pattern == "uri-pattern"
    assert result.expand_strategy is ExpandStrategy.VISIT
