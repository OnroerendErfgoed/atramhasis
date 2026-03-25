import copy
import time
from unittest.mock import Mock

import colander
import pytest
from pyramid import testing
from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import LabelType
from sqlalchemy.exc import NoResultFound

from atramhasis import validators
from atramhasis.data.models import IDGenerationStrategy
from atramhasis.errors import ValidationError
from atramhasis.validators import Concept as ConceptSchema
from atramhasis.validators import ConceptScheme as ConceptSchemeSchema
from atramhasis.validators import LanguageTag
from atramhasis.validators import concept_schema_validator
from atramhasis.validators import conceptscheme_schema_validator
from atramhasis.validators import languagetag_validator


class DummySkosManager:
    def get_thing(self, concept_id, conceptscheme_id):
        concept = Concept(concept_id=concept_id, conceptscheme_id=conceptscheme_id)
        if concept_id == "2":
            broader_concept = Concept(concept_id="1", conceptscheme_id=conceptscheme_id)
            concept.broader_concepts = {broader_concept}
            return concept
        if concept_id == "7":
            narrower_concept = Concept(
                concept_id="14", conceptscheme_id=conceptscheme_id
            )
            concept.narrower_concepts = {narrower_concept}
            return concept
        if concept_id == "666":
            concept = Collection(
                concept_id=concept_id, conceptscheme_id=conceptscheme_id
            )
            return concept
        if concept_id == "667":
            concept = Collection(
                concept_id=concept_id, conceptscheme_id=conceptscheme_id
            )
            memberof = Collection(concept_id="60", conceptscheme_id=conceptscheme_id)
            memberofs = set()
            memberofs.add(memberof)
            concept.member_of = memberofs
            return concept
        if concept_id == "62":
            concept = Collection(
                concept_id=concept_id, conceptscheme_id=conceptscheme_id
            )
            member = Collection(concept_id="666", conceptscheme_id=conceptscheme_id)
            members = set()
            members.add(member)
            concept.members = members
            return concept
        if concept_id == "777":
            if conceptscheme_id != "3":
                raise NoResultFound()
        return concept

    def get_all_label_types(self):
        return [
            LabelType("hiddenLabel", "A hidden label."),
            LabelType("altLabel", "An alternative label."),
            LabelType("prefLabel", "A preferred label."),
        ]


class DummyLanguagesManager:
    def count_languages(self, language_id):
        if language_id in ["af", "flup"]:
            return 0
        else:
            return 1

    def save(self, language):
        return language


_JSON_CONCEPT = {
    "narrower": [{"id": "8"}, {"id": "7"}, {"id": "9"}],
    "label": "Belgium",
    "type": "concept",
    "id": "4",
    "broader": [{"id": "2"}],
    "related": [{"id": "5"}],
    "labels": [{"label": "Belgium", "type": "prefLabel", "language": "en"}],
    "notes": [{"note": "een notitie", "type": "note", "language": "nl"}],
    "sources": [{"citation": "Van Daele K. 2014"}],
    "member_of": [{"id": "666"}],
}

_JSON_COLLECTION = {
    "id": "0",
    "labels": [
        {"language": "nl-BE", "label": "Stijlen en culturen", "type": "prefLabel"}
    ],
    "type": "collection",
    "label": "Stijlen en culturen",
    "members": [{"id": "61"}, {"id": "60"}],
    "notes": [{"note": "een notitie", "type": "note", "language": "nl"}],
    "member_of": [{"id": "666"}],
}

_JSON_CONCEPTSCHEME = {
    "labels": [
        {"language": "nl-BE", "label": "Stijlen en culturen", "type": "prefLabel"}
    ],
    "label": "Stijlen en culturen",
    "notes": [{"note": "een notitie", "type": "note", "language": "nl"}],
    "sources": [{"citation": "Van Daele K. 2014"}],
}


@pytest.fixture(autouse=True)
def pyramid_config():
    config = testing.setUp()
    yield config
    testing.tearDown()


@pytest.fixture
def dummy_request():
    request = testing.DummyRequest()
    request.data_managers = {
        "skos_manager": DummySkosManager(),
        "languages_manager": DummyLanguagesManager(),
    }
    return request


@pytest.fixture
def provider():
    return Mock(conceptscheme_id=1, metadata={})


@pytest.fixture
def concept_schema(dummy_request, provider):
    return ConceptSchema(validator=concept_schema_validator).bind(
        request=dummy_request,
        provider=provider,
        validate_id_generation=True,
    )


@pytest.fixture
def language_schema(dummy_request):
    return LanguageTag(validator=languagetag_validator).bind(
        request=dummy_request, new=True
    )


@pytest.fixture
def conceptscheme_schema(dummy_request):
    return ConceptSchemeSchema(validator=conceptscheme_schema_validator).bind(
        request=dummy_request
    )


@pytest.fixture
def json_concept():
    return copy.deepcopy(_JSON_CONCEPT)


@pytest.fixture
def json_collection():
    return copy.deepcopy(_JSON_COLLECTION)


@pytest.fixture
def json_conceptscheme():
    return copy.deepcopy(_JSON_CONCEPTSCHEME)


class TestValidation:
    def test_validation_conceptscheme(self, conceptscheme_schema, json_conceptscheme):
        validated_conceptscheme = conceptscheme_schema.deserialize(json_conceptscheme)
        assert validated_conceptscheme is not None
        assert 1 == len(validated_conceptscheme["labels"])
        assert 1 == len(validated_conceptscheme["notes"])
        assert 1 == len(validated_conceptscheme["sources"])

    def test_invalid_conceptscheme(self, conceptscheme_schema, json_conceptscheme):
        json_conceptscheme.pop("labels")
        with pytest.raises(ValidationError):
            conceptscheme_schema.deserialize(json_conceptscheme)

    def test_validation_concept(self, concept_schema, json_concept):
        validated_concept = concept_schema.deserialize(json_concept)
        assert validated_concept is not None
        assert 1 == len(validated_concept["labels"])
        assert 1 == len(validated_concept["notes"])
        assert 1 == len(validated_concept["sources"])
        assert 3 == len(validated_concept["narrower"])
        assert 1 == len(validated_concept["broader"])
        assert 1 == len(validated_concept["related"])
        assert 1 == len(validated_concept["member_of"])

    def test_max_preflabels_2_en(self, concept_schema, json_concept):
        json_concept["labels"].append(
            {"label": "B", "type": "prefLabel", "language": "en"}
        )
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)

        assert {
            "labels": "Only one prefLabel per language allowed."
        } in exc_info.value.errors

    def test_max_preflabels_1_en_1_nl(self, concept_schema, json_concept):
        json_concept["labels"].append(
            {"label": "B", "type": "prefLabel", "language": "nl"}
        )
        validated_concept = concept_schema.deserialize(json_concept)
        assert validated_concept is not None

    def test_related_concept_type_collection(self, concept_schema, json_concept):
        json_concept["related"].append({"id": 666})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "related": "A narrower, broader or related concept should "
            "always be a concept, not a collection"
        } in exc_info.value.errors

    def test_collection_with_related(self, concept_schema, json_collection):
        # Collections can not have related relations
        json_collection["related"] = []
        json_collection["related"].append({"id": 2})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_collection)
        assert {
            "related": "Only concepts can have narrower/broader/related relations"
        } in exc_info.value.errors

    def test_narrower_concept_type_collection(self, concept_schema, json_concept):
        json_concept["narrower"].append({"id": 666})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "narrower": "A narrower, broader or related concept should "
            "always be a concept, not a collection"
        } in exc_info.value.errors

    def test_infer_concept_relations(
        self, concept_schema, json_concept, json_collection
    ):
        json_concept["infer_concept_relations"] = True
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "infer_concept_relations": "'infer_concept_relations' can only "
            "be set for collections."
        } in exc_info.value.errors
        json_collection["infer_concept_relations"] = True
        concept_schema.deserialize(json_collection)

    def test_collection_with_narrower(self, concept_schema, json_collection):
        # Collections can not have narrower relations
        json_collection["narrower"] = []
        json_collection["narrower"].append({"id": 2})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_collection)
        assert {
            "narrower": "Only concepts can have narrower/broader/related relations"
        } in exc_info.value.errors

    def test_broader_concept_type_collection(self, concept_schema, json_concept):
        json_concept["broader"].append({"id": 666})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "broader": "A narrower, broader or related concept should "
            "always be a concept, not a collection"
        } in exc_info.value.errors

    def test_collection_with_broader(self, concept_schema, json_collection):
        # Collections can not have broader relations
        json_collection["broader"] = []
        json_collection["broader"].append({"id": 2})
        with pytest.raises(ValidationError):
            concept_schema.deserialize(json_collection)

    def test_related_concept_different_conceptscheme(
        self, concept_schema, json_concept
    ):
        json_concept["related"].append({"id": 777})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "related": "Concept not found, check concept_id. Please be aware "
            "members should be within one scheme"
        } in exc_info.value.errors

    def test_narrower_concept_different_conceptscheme(
        self, concept_schema, json_concept
    ):
        json_concept["narrower"].append({"id": 777})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "narrower": "Concept not found, check concept_id. Please be aware "
            "members should be within one scheme"
        } in exc_info.value.errors

    def test_narrower_concept_to_self(self, concept_schema, json_concept):
        json_concept["narrower"].append({"id": 4})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "narrower": "A concept or collection cannot be related to itself"
        } in exc_info.value.errors

    def test_broader_concept_different_conceptscheme(
        self, concept_schema, json_concept
    ):
        json_concept["broader"].append({"id": 777})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "broader": "Concept not found, check concept_id. Please be aware "
            "members should be within one scheme"
        } in exc_info.value.errors

    def test_broader_concept_hierarchy(self, concept_schema, json_concept):
        json_concept["broader"].append({"id": 14})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "broader": "The broader concept of a concept must not itself "
            "be a narrower concept of the concept being edited."
        } in exc_info.value.errors

    def test_broader_concept_hierarchy_no_narrower(self, concept_schema, json_concept):
        json_concept["broader"].append({"id": 8})
        json_concept["narrower"] = []
        validated_concept = concept_schema.deserialize(json_concept)
        assert validated_concept is not None

    def test_narrower_concept_hierarchy(self, concept_schema, json_concept):
        json_concept["narrower"].append({"id": 1})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "narrower": "The narrower concept of a concept must not itself "
            "be a broader concept of the concept being edited."
        } in exc_info.value.errors

    def test_narrower_concept_hierarchy_no_broader(self, concept_schema, json_concept):
        json_concept["narrower"].append({"id": 1})
        json_concept["broader"] = []
        validated_concept = concept_schema.deserialize(json_concept)
        assert validated_concept is not None

    def test_validation_collection(self, concept_schema, json_collection):
        validated_collection = concept_schema.deserialize(json_collection)
        assert validated_collection is not None
        assert 2 == len(validated_collection["members"])
        assert 1 == len(validated_collection["labels"])
        assert 1 == len(validated_collection["notes"])

    def test_member_concept_different_conceptscheme(
        self, concept_schema, json_collection
    ):
        json_collection["members"].append({"id": 777})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_collection)
        assert {
            "members": "Concept not found, check concept_id. Please be aware "
            "members should be within one scheme"
        } in exc_info.value.errors

    def test_label_type(self, concept_schema, json_concept):
        json_concept["labels"].append(
            {"label": "Belgium", "type": "altLabel", "language": "en"}
        )
        validated_concept = concept_schema.deserialize(json_concept)
        assert validated_concept is not None

    def test_label_type_invalid(self, concept_schema, json_concept):
        json_concept["labels"].append(
            {"label": "Belgium", "type": "testLabelInvalid", "language": "en"}
        )
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {"labels": "Invalid labeltype."} in exc_info.value.errors

    def test_label_language_invalid(self, concept_schema, json_concept):
        json_concept["labels"].append(
            {"label": "Belgium", "type": "altLabel", "language": "eng"}
        )
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "labels": "Invalid language tag: Unknown code 'eng', "
            "Missing language tag in 'eng'."
        } in exc_info.value.errors

    def test_label_language_missing(self, concept_schema, json_concept):
        json_concept["labels"].append(
            {"label": "Belgium", "type": "altLabel", "language": "af"}
        )
        validated_concept = concept_schema.deserialize(json_concept)
        assert validated_concept is not None

    def test_label_invalid(self, concept_schema, json_concept):
        json_concept["labels"].append(
            {"note": "Belgium", "type": "altLabel", "language": "en"}
        )
        with pytest.raises(colander.Invalid):
            concept_schema.deserialize(json_concept)

    def test_note_invalid(self, concept_schema, json_concept):
        json_concept["notes"].append(
            {"label": "een notitie", "type": 5, "language": "nl"}
        )
        with pytest.raises(colander.Invalid):
            concept_schema.deserialize(json_concept)

    def test_memberof_concept_type_collection(self, concept_schema, json_concept):
        # A Collection/Concept can be a member_of a Collection
        validated_concept = concept_schema.deserialize(json_concept)
        assert validated_concept is not None

    def test_memberof_concept_type_concept(self, concept_schema, json_concept):
        # Nothing can be a member_of a Concept
        json_concept["member_of"].append({"id": 2})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "member_of": "A member_of parent should always be a collection"
        } in exc_info.value.errors

    def test_members_collection_unique(self, concept_schema, json_collection):
        # A Collection is a Set (every element of the Collection should be unique).
        json_collection["members"].append({"id": 61})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_collection)
        assert {
            "members": "All members of a collection should be unique."
        } in exc_info.value.errors

    def test_concept_members(self, concept_schema, json_concept):
        # A Concept does not have members.
        json_concept["members"] = []
        json_concept["members"].append({"id": 2})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "members": "Only collections can have members."
        } in exc_info.value.errors

    def test_memberof_concept_hierarchy_simple(self, concept_schema, json_collection):
        # The hierarchy should not contain loops
        json_collection["members"].append({"id": 666})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_collection)
        assert {
            "member_of": "The parent member_of collection of a concept must not "
            "itself be a member of the concept being edited."
        } in exc_info.value.errors

    def test_memberof_concept_hierarchy_deep(self, concept_schema, json_collection):
        # The hierarchy should not contain loops
        json_collection["members"].append({"id": 62})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_collection)
        assert {
            "member_of": "The parent member_of collection of a concept must not "
            "itself be a member of the concept being edited."
        } in exc_info.value.errors

    def test_members_concept_hierarchy_simple(self, concept_schema, json_collection):
        # The hierarchy should not contain loops
        json_collection["member_of"].append({"id": 61})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_collection)
        assert {
            "members": "The item of a members collection must not itself be a "
            "parent of the concept/collection being edited."
        } in exc_info.value.errors

    def test_members_concept_hierarchy_deep(self, concept_schema, json_collection):
        # The hierarchy should not contain loops
        json_collection["member_of"].append({"id": 667})
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_collection)
        assert {
            "members": "The item of a members collection must not itself be a "
            "parent of the concept/collection being edited."
        } in exc_info.value.errors

    def test_min_labels_rule_empty_labels(self, concept_schema, json_concept):
        json_concept["labels"] = []
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {"labels": "At least one label is necessary"} in exc_info.value.errors

    def test_min_labels_rule_no_labels(self, concept_schema):
        json_concept = {
            "narrower": [{"id": 8}, {"id": 7}, {"id": 9}],
            "type": "concept",
            "id": 4,
            "broader": [{"id": 2}],
            "related": [{"id": 5}],
            "notes": [{"note": "een notitie", "type": "note", "language": "nl"}],
            "member_of": [{"id": 666}],
        }
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {"labels": "At least one label is necessary"} in exc_info.value.errors

    def test_concept_matches_rule(self, concept_schema):
        json_concept = {
            "type": "collection",
            "labels": [
                {"language": "nl", "label": "Stijlen en culturen", "type": "prefLabel"}
            ],
            "id": 4,
            "members": [{"id": 666}],
            "matches": {
                "exactMatch": ["urn:sample:666"],
                "broadMatch": ["urn:somewhere:93"],
            },
        }
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {"matches": "Only concepts can have matches"} in exc_info.value.errors

    def test_concept_matches_unique_rule(self, concept_schema):
        json_concept = {
            "type": "concept",
            "labels": [
                {"language": "nl", "label": "Stijlen en culturen", "type": "prefLabel"}
            ],
            "id": 4,
            "member_of": [{"id": 666}],
            "matches": {"exact": ["urn:sample:666"], "broad": ["urn:sample:666"]},
        }
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)

        assert {
            "matches": "All matches of a concept should be unique."
        } in exc_info.value.errors

    def test_concept_matches_unique_rule_pass(self, concept_schema):
        json_concept = {
            "type": "concept",
            "labels": [
                {"language": "nl", "label": "Stijlen en culturen", "type": "prefLabel"}
            ],
            "id": 4,
            "member_of": [{"id": 666}],
            "matches": {
                "exactMatch": ["urn:sample:666"],
                "broadMatch": ["urn:sample:93"],
            },
        }
        validated_concept = concept_schema.deserialize(json_concept)
        assert validated_concept is not None

    def test_languages_pass(self, language_schema):
        json_language = {"id": "af", "name": "Afrikaans"}
        validated_language = language_schema.deserialize(json_language)
        assert validated_language is not None

    def test_languages_duplicate(self, language_schema):
        json_language = {"id": "en", "name": "English"}
        with pytest.raises(ValidationError) as exc_info:
            language_schema.deserialize(json_language)
        assert {"id": "Duplicate language tag: en"} in exc_info.value.errors

    def test_languages_edit_not_raise_duplicate(self, dummy_request):
        json_language = {"id": "en", "name": "English"}
        language = LanguageTag(validator=languagetag_validator).bind(
            request=dummy_request, new=False
        )
        validated_language = language.deserialize(json_language)
        assert validated_language is not None

    def test_languages_invalid(self, language_schema):
        json_language = {"id": "flup", "name": "test"}
        with pytest.raises(ValidationError) as exc_info:
            language_schema.deserialize(json_language)
        assert {
            "id": "Invalid language tag: Unknown code 'flup', Missing "
            "language tag in 'flup'."
        } in exc_info.value.errors

    def test_subordinate_arrays(self, concept_schema, json_concept):
        json_concept["subordinate_arrays"] = [{"id": 667}]
        validated_json = concept_schema.deserialize(json_concept)
        assert validated_json is not None

    def test_subordinate_arrays_no_concept(self, concept_schema, json_collection):
        json_collection["subordinate_arrays"] = [{"id": 666}]
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_collection)
        assert {
            "subordinate_arrays": "Only concept can have subordinate arrays."
        } in exc_info.value.errors

    def test_subordinate_arrays_no_collection(self, concept_schema, json_concept):
        json_concept["subordinate_arrays"] = [{"id": 7}]
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "subordinate_arrays": "A subordinate array should always be a collection"
        } in exc_info.value.errors

    def test_subordinate_arrays_hierarchy(self, concept_schema, json_concept):
        json_concept["subordinate_arrays"] = [{"id": 666}]
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "subordinate_arrays": "The subordinate_array collection of a concept must "
            "not itself be a parent of the concept being edited."
        } in exc_info.value.errors

    def test_superordinates(self, concept_schema, json_collection):
        json_collection["superordinates"] = [{"id": 7}]
        validated_json = concept_schema.deserialize(json_collection)
        assert validated_json is not None

    def test_superordinates_no_concept(self, concept_schema, json_collection):
        json_collection["superordinates"] = [{"id": 666}]
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_collection)
        assert {
            "superordinates": "A superordinate should always be a concept"
        } in exc_info.value.errors

    def test_superordinates_no_collection(self, concept_schema, json_concept):
        json_concept["superordinates"] = [{"id": 7}]
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {
            "superordinates": "Only collection can have superordinates."
        } in exc_info.value.errors

    def test_superordinates_hierarchy(self, concept_schema, json_collection):
        json_collection["superordinates"] = [{"id": 61}]
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_collection)
        assert {
            "superordinates": "The superordinates of a collection must not itself "
            "be a member of the collection being edited."
        } in exc_info.value.errors

    def test_html_in_notes(self, concept_schema):
        json_concept = {
            "narrower": [{"id": 8}, {"id": 7}, {"id": 9}],
            "label": "Belgium",
            "type": "concept",
            "id": 4,
            "broader": [{"id": 2}],
            "related": [{"id": 5}],
            "labels": [{"label": "Belgium", "type": "prefLabel", "language": "en"}],
            "notes": [
                {
                    "note": "een <strong><h2>notitie</h2></strong>",
                    "type": "note",
                    "language": "nl",
                }
            ],
            "sources": [{"citation": "Van Daele K. 2014"}],
            "member_of": [{"id": 666}],
        }
        validated_json = concept_schema.deserialize(json_concept)
        note = validated_json["notes"][0]
        assert "een <strong>\nnotitie</strong>" == note["note"]

    def test_html_in_sources(self, concept_schema):
        json_concept = {
            "narrower": [{"id": 8}, {"id": 7}, {"id": 9}],
            "label": "Belgium",
            "type": "concept",
            "id": 4,
            "broader": [{"id": 2}],
            "related": [{"id": 5}],
            "labels": [{"label": "Belgium", "type": "prefLabel", "language": "en"}],
            "notes": [{"note": "een notitie", "type": "note", "language": "nl"}],
            "sources": [{"citation": "Van Daele K. <strong><h2>2014</h2></strong>"}],
            "member_of": [{"id": 666}],
        }
        validated_json = concept_schema.deserialize(json_concept)
        source = validated_json["sources"][0]
        assert "Van Daele K. <strong>\n2014</strong>" == source["citation"]

    def test_id_generation_manual_no_id(self, dummy_request, provider, json_concept):
        concept_schema = ConceptSchema(validator=concept_schema_validator).bind(
            request=dummy_request,
            provider=provider,
            validate_id_generation=True,
        )
        provider.metadata["atramhasis.id_generation_strategy"] = (
            IDGenerationStrategy.MANUAL
        )
        del json_concept["id"]
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {"id": "Required for this provider."} in exc_info.value.errors
        concept_schema = ConceptSchema(validator=concept_schema_validator).bind(
            request=dummy_request,
            provider=provider,
            validate_id_generation=False,
        )
        concept_schema.deserialize(json_concept)

    def test_id_generation_manual_not_unique(
        self, dummy_request, provider, json_concept
    ):
        concept_schema = ConceptSchema(validator=concept_schema_validator).bind(
            request=dummy_request,
            provider=provider,
            validate_id_generation=True,
        )
        provider.metadata["atramhasis.id_generation_strategy"] = (
            IDGenerationStrategy.MANUAL
        )
        json_concept["id"] = "1"
        with pytest.raises(ValidationError) as exc_info:
            concept_schema.deserialize(json_concept)
        assert {"id": "1 already exists."} in exc_info.value.errors
        concept_schema = ConceptSchema(validator=concept_schema_validator).bind(
            request=dummy_request,
            provider=provider,
            validate_id_generation=False,
        )
        concept_schema.deserialize(json_concept)

    def test_validate_provider(self):
        """
        This looks like it does not validate much, but openapi validates the majority.

        We only need to manually validate what openapi cannot.
        """
        json_data = {"metadata": {}}
        validators.validate_provider_json(json_data)

    def test_validate_provider_forbidden_keys(self):
        forbidden_metadata_keys = (
            "default_language",
            "subject",
            "force_display_language",
            "atramhasis.force_display_language",
            "id_generation_strategy",
            "atramhasis.id_generation_strategy",
        )
        for bad_key in forbidden_metadata_keys:
            json_data = {"metadata": {bad_key: "value"}}
            with pytest.raises(ValidationError):
                validators.validate_provider_json(json_data)

    def test_validate_provider_bad_language(self):
        json_data = {"default_language": "notalanguage"}
        with pytest.raises(ValidationError):
            validators.validate_provider_json(json_data)
        json_data = {"force_display_language": "notalanguage"}
        with pytest.raises(ValidationError):
            validators.validate_provider_json(json_data)

    def test_validate_provider_update_with_wrong_id(self):
        json_data = {"id": "notanid"}
        with pytest.raises(ValidationError):
            validators.validate_provider_json(json_data, "test")


class TestHierarchyBuildPerformance:
    """
    Benchmark tests proving the BFS hierarchy_build completes in linear time.

    The old recursive implementation had an exponential duplication bug: for
    each parent with N children, it recursed N times with the *entire* child
    list, causing N^depth processing. A tree with branching factor 3 and depth
    7 (~3,000 nodes) would take minutes. The fixed BFS must finish in under
    1 second.
    """

    def _build_tree_manager(self, branching_factor, depth):
        """
        Build a DummySkosManager-like object backed by a dict of Concepts
        wired into a tree with the given branching factor and depth.

        Returns (manager, root_ids) where root_ids are the top-level
        concept_ids.
        """
        concepts = {}
        next_id = 0

        def make_node(current_depth):
            nonlocal next_id
            node_id = str(next_id)
            next_id += 1
            concept = Concept(concept_id=node_id, conceptscheme_id=1)
            concepts[node_id] = concept
            if current_depth < depth:
                children = []
                for _ in range(branching_factor):
                    child = make_node(current_depth + 1)
                    children.append(child)
                concept.narrower_concepts = set(children)
            else:
                concept.narrower_concepts = set()
            return concept

        root = make_node(0)

        class TreeSkosManager:
            def get_thing(self, concept_id, conceptscheme_id):
                if concept_id in concepts:
                    return concepts[concept_id]
                raise NoResultFound()

        return TreeSkosManager(), [root.concept_id]

    def test_wide_tree_completes_fast(self):
        """
        A tree with branching factor 3, depth 7 (~3,280 nodes).

        The old code would process this in O(3^(2*7)) = ~4.8 million
        iterations. The fixed BFS visits each node once: ~3,280 iterations.
        """

        manager, root_ids = self._build_tree_manager(branching_factor=3, depth=7)
        result = []

        start = time.perf_counter()
        validators.hierarchy_build(
            manager, 1, root_ids, result, "concept", "narrower_concepts"
        )
        elapsed = time.perf_counter() - start

        # Should complete nearly instantly (well under 1 second).
        assert elapsed < 1.0, f"hierarchy_build took {elapsed:.2f}s, expected < 1s"
        # Verify correctness: all non-root nodes should be in the result.
        # Total nodes = (3^8 - 1) / (3 - 1) = 3280, minus 1 root = 3279 descendants.
        assert 3279 == len(result)

    def test_deep_chain_completes_fast(self):
        """
        A linear chain of 500 nodes (depth=500, branching=1).

        Tests that the BFS handles deep hierarchies without stack overflow
        (which the old recursive approach risked).
        """
        manager, root_ids = self._build_tree_manager(branching_factor=1, depth=500)
        result = []

        start = time.perf_counter()
        validators.hierarchy_build(
            manager, 1, root_ids, result, "concept", "narrower_concepts"
        )
        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"hierarchy_build took {elapsed:.2f}s, expected < 1s"
        assert len(result) == 500

    def test_cycle_does_not_loop_forever(self):
        """
        A small hierarchy with a cycle must terminate (not loop forever).
        """

        # Build a cycle: A -> B -> C -> A
        a = Concept(concept_id="A", conceptscheme_id=1)
        b = Concept(concept_id="B", conceptscheme_id=1)
        c = Concept(concept_id="C", conceptscheme_id=1)
        a.narrower_concepts = {b}
        b.narrower_concepts = {c}
        c.narrower_concepts = {a}
        concepts = {"A": a, "B": b, "C": c}

        class CyclicManager:
            def get_thing(self, concept_id, conceptscheme_id):
                return concepts[concept_id]

        manager = CyclicManager()
        result = []

        start = time.perf_counter()
        validators.hierarchy_build(
            manager, 1, ["A"], result, "concept", "narrower_concepts"
        )
        elapsed = time.perf_counter() - start

        assert elapsed < 1.0
        # All three nodes should appear in the result (B, C, A as descendants).
        assert set(result) == {"A", "B", "C"}
