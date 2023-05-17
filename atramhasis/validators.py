"""
Module that validates incoming JSON.
"""

import copy

import bleach
import colander
from language_tags import tags
from skosprovider_sqlalchemy.models import (
    Language
)
from sqlalchemy.exc import NoResultFound

from atramhasis.errors import ValidationError
from atramhasis.data.models import IDGenerationStrategy


class ForcedString(colander.String):
    """
    Acts just like colander.String but anything it gets will be turned into a string.

    eg. Passing a number 1 will treat it as "1". null/None remains null/None
    """

    def deserialize(self, node, cstruct):
        if (
            not isinstance(cstruct, str)
            and not isinstance(cstruct, bytes)
            and cstruct is not colander.null
        ):
            cstruct = str(cstruct)
        return super().deserialize(node, cstruct)


class Label(colander.MappingSchema):
    label = colander.SchemaNode(
        colander.String()
    )
    type = colander.SchemaNode(
        colander.String()
    )
    language = colander.SchemaNode(
        colander.String()
    )


def html_preparer(value):
    """
    Prepare the value by stripping all html except certain tags.

    :param value: The value to be cleaned. 
    :rtype: str
    """
    try:
        return bleach.clean(value, tags=['strong', 'em', 'a'], strip=True)
    except TypeError:
        # Trying to clean a non-string
        # Ignore for now so it can be caught later on
        return value


class Note(colander.MappingSchema):
    note = colander.SchemaNode(
        colander.String(),
        preparer=html_preparer
    )
    type = colander.SchemaNode(
        colander.String()
    )
    language = colander.SchemaNode(
        colander.String()
    )


class Source(colander.MappingSchema):
    citation = colander.SchemaNode(
        colander.String(),
        preparer=html_preparer
    )


class Labels(colander.SequenceSchema):
    label = Label()


class Notes(colander.SequenceSchema):
    note = Note()


class Sources(colander.SequenceSchema):
    source = Source()


class RelatedConcept(colander.MappingSchema):
    id = colander.SchemaNode(
        ForcedString()
    )


class Concepts(colander.SequenceSchema):
    concept = RelatedConcept()


class MatchList(colander.SequenceSchema):
    match = colander.SchemaNode(
        colander.String(),
        missing=None
    )


class Matches(colander.MappingSchema):
    broad = MatchList(missing=[])
    close = MatchList(missing=[])
    exact = MatchList(missing=[])
    narrow = MatchList(missing=[])
    related = MatchList(missing=[])


class Concept(colander.MappingSchema):
    id = colander.SchemaNode(
        ForcedString(),
        missing=None
    )
    type = colander.SchemaNode(
        colander.String(),
        missing='concept'
    )
    labels = Labels(missing=[])
    notes = Notes(missing=[])
    sources = Sources(missing=[])
    broader = Concepts(missing=[])
    narrower = Concepts(missing=[])
    related = Concepts(missing=[])
    members = Concepts(missing=[])
    member_of = Concepts(missing=[])
    subordinate_arrays = Concepts(missing=[])
    superordinates = Concepts(missing=[])
    matches = Matches(missing={})
    infer_concept_relations = colander.SchemaNode(
        colander.Boolean(),
        missing=colander.drop
    )

    def preparer(self, concept):
        return concept


class ConceptScheme(colander.MappingSchema):
    labels = Labels(missing=[])
    notes = Notes(missing=[])
    sources = Sources(missing=[])


class LanguageTag(colander.MappingSchema):
    id = colander.SchemaNode(
        colander.String()
    )
    name = colander.SchemaNode(
        colander.String()
    )


def concept_schema_validator(node, cstruct):
    """
    This validator validates an incoming concept or collection

    This validator will run a list of rules against the concept or collection
    to see that there are no validation rules being broken.

    :param colander.SchemaNode node: The schema that's being used while validating.
    :param cstruct: The concept or collection being validated.
    """
    request = node.bindings['request']
    validate_id_generation = node.bindings['validate_id_generation']
    skos_manager = request.data_managers['skos_manager']
    languages_manager = request.data_managers['languages_manager']
    provider = node.bindings['provider']
    conceptscheme_id = provider.conceptscheme_id
    concept_type = cstruct['type']
    collection_id = cstruct['id']
    narrower = None
    broader = None
    related = None
    members = None
    member_of = None
    r_validated = False
    n_validated = False
    b_validated = False
    m_validated = False
    o_validated = False
    errors = []
    min_labels_rule(errors, node, cstruct)
    if 'labels' in cstruct:
        labels = copy.deepcopy(cstruct['labels'])
        label_type_rule(errors, node, skos_manager, labels)
        label_lang_rule(errors, node, languages_manager, labels)
        max_preflabels_rule(errors, node, labels)
    if 'related' in cstruct:
        related = copy.deepcopy(cstruct['related'])
        related = [m['id'] for m in related]
        r_validated = semantic_relations_rule(errors, node['related'], skos_manager,
                                              conceptscheme_id, related, collection_id)
        concept_relations_rule(errors, node['related'], related, concept_type)
    if 'narrower' in cstruct:
        narrower = copy.deepcopy(cstruct['narrower'])
        narrower = [m['id'] for m in narrower]
        n_validated = semantic_relations_rule(errors, node['narrower'], skos_manager,
                                              conceptscheme_id, narrower, collection_id)
        concept_relations_rule(errors, node['narrower'], narrower, concept_type)
    if 'broader' in cstruct:
        broader = copy.deepcopy(cstruct['broader'])
        broader = [m['id'] for m in broader]
        b_validated = semantic_relations_rule(errors, node['broader'], skos_manager,
                                              conceptscheme_id, broader, collection_id)
        concept_relations_rule(errors, node['broader'], broader, concept_type)
    if 'members' in cstruct:
        members = copy.deepcopy(cstruct['members'])
        members = [m['id'] for m in members]
        m_validated = semantic_relations_rule(errors, node['members'], skos_manager,
                                              conceptscheme_id, members, collection_id)
    if 'member_of' in cstruct:
        member_of = copy.deepcopy(cstruct['member_of'])
        member_of = [m['id'] for m in member_of]
        o_validated = semantic_relations_rule(errors, node['member_of'], skos_manager,
                                              conceptscheme_id, member_of, collection_id)
    if r_validated and n_validated and b_validated:
        concept_type_rule(errors, node['narrower'], skos_manager, conceptscheme_id, narrower)
        narrower_hierarchy_rule(errors, node['narrower'], skos_manager, conceptscheme_id, cstruct)
        concept_type_rule(errors, node['broader'], skos_manager, conceptscheme_id, broader)
        broader_hierarchy_rule(errors, node['broader'], skos_manager, conceptscheme_id, cstruct)
        concept_type_rule(errors, node['related'], skos_manager, conceptscheme_id, related)

    if m_validated and o_validated:
        members_only_in_collection_rule(errors, node['members'], concept_type, members)
        collection_members_unique_rule(errors, node['members'], members)
        collection_type_rule(errors, node['member_of'], skos_manager, conceptscheme_id, member_of)
        memberof_hierarchy_rule(errors, node['member_of'], skos_manager, conceptscheme_id, cstruct)
        members_hierarchy_rule(errors, node['members'], skos_manager, conceptscheme_id, cstruct)

    if 'matches' in cstruct:
        matches = copy.deepcopy(cstruct['matches'])
        concept_matches_rule(errors, node['matches'], matches, concept_type)
        concept_matches_unique_rule(errors, node['matches'], matches)

    if 'subordinate_arrays' in cstruct:
        subordinate_arrays = copy.deepcopy(cstruct['subordinate_arrays'])
        subordinate_arrays = [m['id'] for m in subordinate_arrays]
        subordinate_arrays_only_in_concept_rule(errors, node['subordinate_arrays'], concept_type, subordinate_arrays)
        subordinate_arrays_type_rule(errors, node['subordinate_arrays'], skos_manager, conceptscheme_id,
                                     subordinate_arrays)
        subordinate_arrays_hierarchy_rule(errors, node['subordinate_arrays'], skos_manager, conceptscheme_id, cstruct)

    if 'superordinates' in cstruct:
        superordinates = copy.deepcopy(cstruct['superordinates'])
        superordinates = [m['id'] for m in superordinates]
        superordinates_only_in_concept_rule(errors, node['superordinates'], concept_type, superordinates)
        superordinates_type_rule(errors, node['superordinates'], skos_manager, conceptscheme_id, superordinates)
        superordinates_hierarchy_rule(errors, node['superordinates'], skos_manager, conceptscheme_id, cstruct)

    if cstruct['type'] == 'concept' and 'infer_concept_relations' in cstruct:
        msg = "'infer_concept_relations' can only be set for collections."
        errors.append(colander.Invalid(node['infer_concept_relations'], msg=msg))

    if validate_id_generation:
        id_generation_strategy = provider.metadata.get(
            "atramhasis.id_generation_strategy", IDGenerationStrategy.NUMERIC
        )
        if id_generation_strategy == IDGenerationStrategy.MANUAL:
            if not cstruct.get("id"):
                msg = "Required for this provider."
                errors.append(colander.Invalid(node["id"], msg=msg))
            else:
                try:
                    skos_manager.get_thing(cstruct["id"], conceptscheme_id)
                except NoResultFound:
                    # this is desired
                    pass
                else:
                    msg = f"{cstruct['id']} already exists."
                    errors.append(colander.Invalid(node["id"], msg=msg))

    if len(errors) > 0:
        raise ValidationError(
            'Concept could not be validated',
            [e.asdict() for e in errors]
        )


def conceptscheme_schema_validator(node, cstruct):
    """
    This validator validates the incoming conceptscheme labels

    :param colander.SchemaNode node: The schema that's being used while validating.
    :param cstruct: The conceptscheme being validated.
    """
    request = node.bindings['request']
    skos_manager = request.data_managers['skos_manager']
    languages_manager = request.data_managers['languages_manager']
    errors = []
    min_labels_rule(errors, node, cstruct)
    if 'labels' in cstruct:
        labels = copy.deepcopy(cstruct['labels'])
        label_type_rule(errors, node, skos_manager, labels)
        label_lang_rule(errors, node, languages_manager, labels)
        max_preflabels_rule(errors, node, labels)
    if len(errors) > 0:
        raise ValidationError(
            'ConceptScheme could not be validated',
            [e.asdict() for e in errors]
        )


def concept_relations_rule(errors, node_location, relations, concept_type):
    """
    Checks that only concepts have narrower, broader and related relations.
    """
    if relations is not None and len(relations) > 0 and concept_type != 'concept':
        errors.append(colander.Invalid(
            node_location,
            'Only concepts can have narrower/broader/related relations'
        ))


def max_preflabels_rule(errors, node, labels):
    """
    Checks that there's only one prefLabel for a certain language.
    """
    preflabel_found = []
    for label in labels:
        if label['type'] == 'prefLabel':
            if label['language'] in preflabel_found:
                errors.append(colander.Invalid(
                    node['labels'],
                    'Only one prefLabel per language allowed.'
                ))
            else:
                preflabel_found.append(label['language'])


def min_labels_rule(errors, node, cstruct):
    """
    Checks that a label or collection always has a least one label.
    """
    if 'labels' in cstruct:
        labels = copy.deepcopy(cstruct['labels'])
        if len(labels) == 0:
            errors.append(colander.Invalid(
                node['labels'],
                'At least one label is necessary'
            ))


def label_type_rule(errors, node, skos_manager, labels):
    """
    Checks that a label has the correct type.
    """
    label_types = skos_manager.get_all_label_types()
    label_types = [label_type.name for label_type in label_types]
    for label in labels:
        if label['type'] not in label_types:
            errors.append(colander.Invalid(
                node['labels'],
                'Invalid labeltype.'
            ))


def label_lang_rule(errors, node, languages_manager, labels):
    """
    Checks that languages of a label are valid.

    Checks that they are valid IANA language tags. If the language tag was not
    already present in the database, it adds them.
    """
    for label in labels:
        language_tag = label['language']
        if not tags.check(language_tag):
            errors.append(colander.Invalid(
                node['labels'],
                'Invalid language tag: %s' % ", ".join([err.message for err in tags.tag(language_tag).errors])
            ))
        else:
            languages_present = languages_manager.count_languages(language_tag)
            if not languages_present:
                descriptions = ', '.join(tags.description(language_tag))
                language_item = Language(id=language_tag, name=descriptions)
                languages_manager.save(language_item)


def concept_type_rule(errors, node_location, skos_manager, conceptscheme_id, items):
    """
    Checks that the targets of narrower, broader and related are concepts and
    not collections.
    """
    for item_concept_id in items:
        item_concept = skos_manager.get_thing(item_concept_id, conceptscheme_id)
        if item_concept.type != 'concept':
            errors.append(colander.Invalid(
                node_location,
                'A narrower, broader or related concept should always be a concept, not a collection'
            ))


def collection_type_rule(errors, node_location, skos_manager, conceptscheme_id, members):
    """
    Checks that the targets of member_of are collections and not concepts.
    """
    for member_collection_id in members:
        member_collection = skos_manager.get_thing(member_collection_id, conceptscheme_id)
        if member_collection.type != 'collection':
            errors.append(colander.Invalid(
                node_location,
                'A member_of parent should always be a collection'
            ))


def semantic_relations_rule(errors, node_location, skos_manager, conceptscheme_id, members, collection_id):
    """
    Checks that the elements in a group of concepts or collections are not the
    the group itself, that they actually exist and are within
    the same conceptscheme.
    """
    for member_concept_id in members:
        if member_concept_id == collection_id:
            errors.append(colander.Invalid(
                node_location,
                'A concept or collection cannot be related to itself'
            ))
            return False
        try:
            skos_manager.get_thing(member_concept_id, conceptscheme_id)
        except NoResultFound:
            errors.append(colander.Invalid(
                node_location,
                'Concept not found, check concept_id. Please be aware members should be within one scheme'
            ))
            return False
    return True


def hierarchy_build(skos_manager, conceptscheme_id, property_list, property_hierarchy, property_concept_type,
                    property_list_name):
    for property_concept_id in property_list:
        try:
            property_concept = skos_manager.get_thing(property_concept_id, conceptscheme_id)
        except NoResultFound:
            property_concept = None
        if property_concept is not None and (
                        property_concept.type == property_concept_type or property_concept_type is None):
            property_concepts = [n.concept_id for n in getattr(property_concept, property_list_name)]
            for members_id in property_concepts:
                property_hierarchy.append(members_id)
                hierarchy_build(skos_manager, conceptscheme_id, property_concepts, property_hierarchy,
                                property_concept_type, property_list_name)


def hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct, property1, property2,
                   property2_list_name, concept_type, error_message):
    """
    Checks that the property1 of a concept are not already in property2 hierarchy

    """
    property2_hierarchy = []
    property1_list = []
    if property1 in cstruct:
        property1_value = copy.deepcopy(cstruct[property1])
        property1_list = [m['id'] for m in property1_value]
    if property2 in cstruct:
        property2_value = copy.deepcopy(cstruct[property2])
        property2_list = [m['id'] for m in property2_value]
        property2_hierarchy = property2_list
        hierarchy_build(skos_manager, conceptscheme_id, property2_list, property2_hierarchy, concept_type,
                        property2_list_name)
    for broader_concept_id in property1_list:
        if broader_concept_id in property2_hierarchy:
            errors.append(colander.Invalid(
                node_location,
                error_message
            ))


def broader_hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct):
    """
    Checks that the broader concepts of a concepts are not alreadt narrower
    concepts of that concept.
    """
    hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct, 'broader', 'narrower',
                   'narrower_concepts', 'concept',
                   'The broader concept of a concept must not itself be a narrower concept of the concept being edited.'
                   )


def narrower_hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct):
    """
    Checks that the narrower concepts of a concept are not already broader
    concepts of that concept.
    """
    hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct, 'narrower', 'broader',
                   'broader_concepts', 'concept',
                   'The narrower concept of a concept must not itself be a broader concept of the concept being edited.'
                   )


def collection_members_unique_rule(errors, node_location, members):
    """
    Checks that a collection has no duplicate members.
    """
    if len(members) > len(set(members)):
        errors.append(colander.Invalid(
            node_location,
            'All members of a collection should be unique.'
        ))


def members_only_in_collection_rule(errors, node, concept_type, members):
    """
    Checks that only collections have members.
    """
    if concept_type != 'collection' and len(members) > 0:
        errors.append(colander.Invalid(
            node,
            'Only collections can have members.'
        ))


def memberof_hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct):
    hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct, 'member_of', 'members',
                   'members', 'collection',
                   'The parent member_of collection of a concept must not itself be a member of the concept being edited.'
                   )


def members_hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct):
    """
    Checks that a collection does not have members that are in themselves
    already "parents" of that collection.
    """
    hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct, 'members', 'member_of',
                   'member_of', 'collection',
                   'The item of a members collection must not itself be a parent of the concept/collection being edited.'
                   )


def concept_matches_rule(errors, node_location, matches, concept_type):
    """
    Checks that only concepts have matches.
    """
    if matches is not None and len(matches) > 0 and concept_type != 'concept':
        errors.append(colander.Invalid(
            node_location,
            'Only concepts can have matches'
        ))


def concept_matches_unique_rule(errors, node_location, matches):
    """
    Checks that a concept has not duplicate matches.

    This means that a concept can only have one match (no matter what the type)
    with another concept. We don't allow eg. a concept that has both a broadMatch
    and a relatedMatch with the same concept.
    """
    if matches is not None:
        uri_list = []
        for matchtype in matches:
            uri_list.extend([uri for uri in matches[matchtype]])
        if len(uri_list) > len(set(uri_list)):
            errors.append(colander.Invalid(
                node_location,
                'All matches of a concept should be unique.'
            ))


def languagetag_validator(node, cstruct):
    """
    This validator validates a languagetag.

    The validator will check if a tag is a valid IANA language tag. The the
    validator is informed that this should be a new language tag, it will also
    check if the tag doesn't already exist.

    :param colander.SchemaNode node: The schema that's being used while validating.
    :param cstruct: The value being validated.
    """
    request = node.bindings['request']
    languages_manager = request.data_managers['languages_manager']
    new = node.bindings['new']
    errors = []
    language_tag = cstruct['id']

    if new:
        languagetag_checkduplicate(node['id'], language_tag, languages_manager, errors)
    languagetag_isvalid_rule(node['id'], language_tag, errors)

    if len(errors) > 0:
        raise ValidationError(
            'Language could not be validated',
            [e.asdict() for e in errors]
        )


def languagetag_isvalid_rule(node, language_tag, errors):
    """
    Check that a languagetag is a valid IANA language tag.
    """
    if not tags.check(language_tag):
        errors.append(colander.Invalid(
            node,
            'Invalid language tag: %s' % ", ".join([err.message for err in tags.tag(language_tag).errors])
        ))


def languagetag_checkduplicate(node, language_tag, languages_manager, errors):
    """
    Check that a languagetag isn't duplicated.
    """
    language_present = languages_manager.count_languages(language_tag)
    if language_present:
        errors.append(colander.Invalid(
            node,
            'Duplicate language tag: %s' % language_tag)
        )


def subordinate_arrays_only_in_concept_rule(errors, node, concept_type, subordinate_arrays):
    """
    Checks that only a concept has subordinate arrays.
    """
    if concept_type != 'concept' and len(subordinate_arrays) > 0:
        errors.append(colander.Invalid(
            node,
            'Only concept can have subordinate arrays.'
        ))


def subordinate_arrays_type_rule(errors, node_location, skos_manager, conceptscheme_id, subordinate_arrays):
    """
    Checks that subordinate arrays are always collections.
    """
    for subordinate_id in subordinate_arrays:
        subordinate = skos_manager.get_thing(subordinate_id, conceptscheme_id)
        if subordinate.type != 'collection':
            errors.append(colander.Invalid(
                node_location,
                'A subordinate array should always be a collection'
            ))


def subordinate_arrays_hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct):
    """
    Checks that the subordinate arrays of a concept are not themselves
    parents of that concept.
    """
    hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct, 'subordinate_arrays', 'member_of',
                   'members', 'collection',
                   'The subordinate_array collection of a concept must not itself be a parent of the concept being edited.'
                   )


def superordinates_only_in_concept_rule(errors, node, concept_type, superordinates):
    """
    Checks that only collections have superordinates.
    """
    if concept_type != 'collection' and len(superordinates) > 0:
        errors.append(colander.Invalid(
            node,
            'Only collection can have superordinates.'
        ))


def superordinates_type_rule(errors, node_location, skos_manager, conceptscheme_id, superordinates):
    """
    Checks that superordinates are always concepts.
    """
    for superordinate_id in superordinates:
        superordinate = skos_manager.get_thing(superordinate_id, conceptscheme_id)
        if superordinate.type != 'concept':
            errors.append(colander.Invalid(
                node_location,
                'A superordinate should always be a concept'
            ))


def superordinates_hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct):
    """
    Checks that the superordinate concepts of a collection are not themselves
    members of that collection.
    """
    hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct, 'superordinates', 'members',
                   'members', 'collection',
                   'The superordinates of a collection must not itself be a member of the collection being edited.'
                   )


def validate_provider_json(json_data, provider_id=None):
    errors = []

    if provider_id:
        if provider_id != json_data.get('id'):
            errors.append(
                {"id": "Id does not match with id parameter in url."},
            )
    # Do not allow keys in the metadata which exist in the root of the json.
    forbidden_metadata_keys = (
        'default_language',
        'subject',
        'force_display_language',  # while not the same, this would just be confusing
        'atramhasis.force_display_language',
        'id_generation_strategy',  # while not the same, this would just be confusing
        'atramhasis.id_generation_strategy',
    )
    metadata = json_data.get('metadata', {})
    if wrong_keys := [k for k in forbidden_metadata_keys if k in metadata]:
        errors.append({'metadata': f'Found disallowed key(s): {", ".join(wrong_keys)}.'})

    if json_data.get('default_language'):
        if not tags.check(json_data['default_language']):
            errors.append({'default_language': 'Invalid language.'})

    if json_data.get('force_display_language'):
        if not tags.check(json_data['force_display_language']):
            errors.append({'force_display_language': 'Invalid language.'})

    if json_data.get('subject'):
        if json_data['subject'] != ['hidden']:
            errors.append({'subject': 'Subject must be one of: "hidden"'})

    if errors:
        raise ValidationError('Provider could not be validated.', errors)
