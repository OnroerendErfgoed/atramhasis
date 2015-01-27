import copy

import colander
from skosprovider_sqlalchemy.models import (
    Concept as DomainConcept,
    Collection as DomainCollection,
    Thing, LabelType, Language)
from sqlalchemy.orm.exc import NoResultFound
from atramhasis.errors import ValidationError
from language_tags import tags


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


class Note(colander.MappingSchema):
    note = colander.SchemaNode(
        colander.String()
    )
    type = colander.SchemaNode(
        colander.String()
    )
    language = colander.SchemaNode(
        colander.String()
    )


class Labels(colander.SequenceSchema):
    label = Label()


class Notes(colander.SequenceSchema):
    note = Note()


class RelatedConcept(colander.MappingSchema):
    id = colander.SchemaNode(
        colander.Int()
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
        colander.Int(),
        missing=None
    )
    type = colander.SchemaNode(
        colander.String(),
        missing='concept'
    )
    labels = Labels(missing=[])
    notes = Notes(missing=[])
    broader = Concepts(missing=[])
    narrower = Concepts(missing=[])
    related = Concepts(missing=[])
    members = Concepts(missing=[])
    member_of = Concepts(missing=[])
    subordinate_arrays = Concepts(missing=[])
    superordinates = Concepts(missing=[])
    matches = Matches(missing={})


class LanguageTag(colander.MappingSchema):
    id = colander.SchemaNode(
        colander.String()
    )
    name = colander.SchemaNode(
        colander.String()
    )


def concept_schema_validator(node, cstruct):
    request = node.bindings['request']
    skos_manager = request.data_managers['skos_manager']
    languages_manager = request.data_managers['languages_manager']
    conceptscheme_id = node.bindings['conceptscheme_id']
    concept_type = cstruct['type']
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
        r_validated = concept_exists_andnot_different_conceptscheme_rule(errors, node['related'], skos_manager,
                                                                         conceptscheme_id, related)
        concept_relations_rule(errors, node['related'], related, concept_type)
    if 'narrower' in cstruct:
        narrower = copy.deepcopy(cstruct['narrower'])
        narrower = [m['id'] for m in narrower]
        n_validated = concept_exists_andnot_different_conceptscheme_rule(errors, node['narrower'], skos_manager,
                                                                         conceptscheme_id, narrower)
        concept_relations_rule(errors, node['narrower'], narrower, concept_type)
    if 'broader' in cstruct:
        broader = copy.deepcopy(cstruct['broader'])
        broader = [m['id'] for m in broader]
        b_validated = concept_exists_andnot_different_conceptscheme_rule(errors, node['broader'], skos_manager,
                                                                         conceptscheme_id, broader)
        concept_relations_rule(errors, node['broader'], broader, concept_type)
    if 'members' in cstruct:
        members = copy.deepcopy(cstruct['members'])
        members = [m['id'] for m in members]
        m_validated = concept_exists_andnot_different_conceptscheme_rule(errors, node['members'], skos_manager,
                                                                         conceptscheme_id, members)
    if 'member_of' in cstruct:
        member_of = copy.deepcopy(cstruct['member_of'])
        member_of = [m['id'] for m in member_of]
        o_validated = concept_exists_andnot_different_conceptscheme_rule(errors, node['member_of'], skos_manager,
                                                                         conceptscheme_id, member_of)
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
        subordinate_arrays_type_rule(errors, node['subordinate_arrays'], skos_manager, conceptscheme_id, subordinate_arrays)
        subordinate_arrays_hierarchy_rule(errors, node['subordinate_arrays'], skos_manager, conceptscheme_id, cstruct)

    if 'superordinates' in cstruct:
        superordinates = copy.deepcopy(cstruct['superordinates'])
        superordinates = [m['id'] for m in superordinates]
        superordinates_only_in_concept_rule(errors, node['superordinates'], concept_type, superordinates)
        superordinates_type_rule(errors, node['superordinates'], skos_manager, conceptscheme_id, superordinates)
        superordinates_hierarchy_rule(errors, node['superordinates'], skos_manager, conceptscheme_id, cstruct)

    if len(errors) > 0:
        raise ValidationError(
            'Concept could not be validated',
            [e.asdict() for e in errors]
        )


def concept_relations_rule(errors, node_location, relations, concept_type):
    if relations is not None and len(relations) > 0 and concept_type != 'concept':
        errors.append(colander.Invalid(
            node_location,
            'Only concepts can have narrower/broader/related relations'
        ))


def max_preflabels_rule(errors, node, labels):
    preflabel_found = []
    for label in labels:
        if label['type'] == 'prefLabel':
            if label['language'] in preflabel_found:
                errors.append(colander.Invalid(
                    node['labels'],
                    'A concept or collection can have only one prefLabel per language.'
                ))
            else:
                preflabel_found.append(label['language'])


def min_labels_rule(errors, node, cstruct):
    if 'labels' in cstruct:
        labels = copy.deepcopy(cstruct['labels'])
        if len(labels) == 0:
            errors.append(colander.Invalid(
                node['labels'],
                'A concept or collection should have at least one label'
            ))


def label_type_rule(errors, node, skos_manager, labels):
    label_types = skos_manager.get_all_label_types()
    label_types = [label_type.name for label_type in label_types]
    for label in labels:
        if label['type'] not in label_types:
            errors.append(colander.Invalid(
                node['labels'],
                'Invalid labeltype.'
            ))


def label_lang_rule(errors, node, languages_manager, labels):
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


def concept_type_rule(errors, node_location, skos_manager, conceptscheme_id, members):
    for member_concept_id in members:
        member_concept = skos_manager.get_thing(member_concept_id, conceptscheme_id)
        if member_concept.type != 'concept':
            errors.append(colander.Invalid(
                node_location,
                'A member should always be a concept, not a collection'
            ))


def collection_type_rule(errors, node_location, skos_manager, conceptscheme_id, members):
    for member_collection_id in members:
        member_collection = skos_manager.get_thing(member_collection_id, conceptscheme_id)
        if member_collection.type != 'collection':
            errors.append(colander.Invalid(
                node_location,
                'A member_of parent should always be a collection'
            ))


def concept_exists_andnot_different_conceptscheme_rule(errors, node_location, skos_manager, conceptscheme_id, members):
    for member_concept_id in members:
        try:
            skos_manager.get_thing(member_concept_id, conceptscheme_id)
        except NoResultFound:
            errors.append(colander.Invalid(
                node_location,
                'Concept not found, check concept_id. Please be aware members should be within one scheme'
            ))
            return False
    return True


def broader_hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct):
    narrower_hierarchy = []
    broader = []
    if 'broader' in cstruct:
        broader = copy.deepcopy(cstruct['broader'])
        broader = [m['id'] for m in broader]
    if 'narrower' in cstruct:
        narrower = copy.deepcopy(cstruct['narrower'])
        narrower = [m['id'] for m in narrower]
        narrower_hierarchy = narrower
        narrower_hierarchy_build(skos_manager, conceptscheme_id, narrower, narrower_hierarchy)
    for broader_concept_id in broader:
        if broader_concept_id in narrower_hierarchy:
            errors.append(colander.Invalid(
                node_location,
                'The broader concept of a concept must not itself be a narrower concept of the concept being edited.'
            ))


def narrower_hierarchy_build(skos_manager, conceptscheme_id, narrower, narrower_hierarchy):
    for narrower_concept_id in narrower:
        narrower_concept = skos_manager.get_thing(narrower_concept_id, conceptscheme_id)
        if narrower_concept is not None and narrower_concept.type == 'concept':
            narrower_concepts = [n.concept_id for n in narrower_concept.narrower_concepts]
            for narrower_id in narrower_concepts:
                narrower_hierarchy.append(narrower_id)
            narrower_hierarchy_build(skos_manager, conceptscheme_id, narrower_concepts, narrower_hierarchy)


def narrower_hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct):
    broader_hierarchy = []
    narrower = []
    if 'narrower' in cstruct:
        narrower = copy.deepcopy(cstruct['narrower'])
        narrower = [m['id'] for m in narrower]
    if 'broader' in cstruct:
        broader = copy.deepcopy(cstruct['broader'])
        broader = [m['id'] for m in broader]
        broader_hierarchy = broader
        broader_hierarchy_build(skos_manager, conceptscheme_id, broader, broader_hierarchy)
    for narrower_concept_id in narrower:
        if narrower_concept_id in broader_hierarchy:
            errors.append(colander.Invalid(
                node_location,
                'The narrower concept of a concept must not itself be a broader concept of the concept being edited.'
            ))


def broader_hierarchy_build(skos_manager, conceptscheme_id, broader, broader_hierarchy):
    for broader_concept_id in broader:
        broader_concept = skos_manager.get_thing(broader_concept_id, conceptscheme_id)
        if broader_concept is not None and broader_concept.type == 'concept':
            broader_concepts = [n.concept_id for n in broader_concept.broader_concepts]
            for broader_id in broader_concepts:
                broader_hierarchy.append(broader_id)
            broader_hierarchy_build(skos_manager, conceptscheme_id, broader_concepts, broader_hierarchy)


def collection_members_unique_rule(errors, node_location, members):
    if len(members) > len(set(members)):
        errors.append(colander.Invalid(
            node_location,
            'All members of a collection should be unique.'
        ))


def members_only_in_collection_rule(errors, node, concept_type, members):
    if concept_type != 'collection' and len(members) > 0:
        errors.append(colander.Invalid(
            node,
            'Only collections can have members.'
        ))


def memberof_hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct):
    members_hierarchy = []
    memberof = []
    if 'member_of' in cstruct:
        memberof = copy.deepcopy(cstruct['member_of'])
        memberof = [m['id'] for m in memberof]
    if 'members' in cstruct:
        members = copy.deepcopy(cstruct['members'])
        members = [m['id'] for m in members]
        members_hierarchy = members
        members_hierarchy_build(skos_manager, conceptscheme_id, members, members_hierarchy)
    for memberof_concept_id in memberof:
        if memberof_concept_id in members_hierarchy:
            errors.append(colander.Invalid(
                node_location,
                'The parent member_of collection of a concept must not itself be a member of the concept being edited.'
            ))


def members_hierarchy_build(skos_manager, conceptscheme_id, members, members_hierarchy):
    for members_concept_id in members:
        try:
            members_concept = skos_manager.get_thing(members_concept_id, conceptscheme_id)
        except NoResultFound:
            members_concept = None
        if members_concept is not None and members_concept.type == 'collection':
            members_concepts = [n.concept_id for n in members_concept.members]
            for members_id in members_concepts:
                members_hierarchy.append(members_id)
            members_hierarchy_build(skos_manager, conceptscheme_id, members_concepts, members_hierarchy)


def members_hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct):
    memberof_hierarchy = []
    members = []
    if 'members' in cstruct:
        members = copy.deepcopy(cstruct['members'])
        members = [m['id'] for m in members]
    if 'member_of' in cstruct:
        member_of = copy.deepcopy(cstruct['member_of'])
        member_of = [m['id'] for m in member_of]
        memberof_hierarchy = member_of
        memberof_hierarchy_build(skos_manager, conceptscheme_id, member_of, memberof_hierarchy)
    for member_concept_id in members:
        if member_concept_id in memberof_hierarchy:
            errors.append(colander.Invalid(
                node_location,
                'The item of a members collection must not itself be a parent of the concept/collection being edited.'
            ))


def memberof_hierarchy_build(skos_manager, conceptscheme_id, member_of, memberof_hierarchy):
    for memberof_concept_id in member_of:
        memberof_concept = skos_manager.get_thing(memberof_concept_id, conceptscheme_id)
        if memberof_concept is not None:
            memberof_concepts = [n.concept_id for n in memberof_concept.member_of]
            for memberof_id in memberof_concepts:
                memberof_hierarchy.append(memberof_id)
            memberof_hierarchy_build(skos_manager, conceptscheme_id, memberof_concepts, memberof_hierarchy)


def concept_matches_rule(errors, node_location, matches, concept_type):
    if matches is not None and len(matches) > 0 and concept_type != 'concept':
        errors.append(colander.Invalid(
            node_location,
            'Only concepts can have matches'
        ))


def concept_matches_unique_rule(errors, node_location, matches):
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
    if not tags.check(language_tag):
        errors.append(colander.Invalid(
            node,
            'Invalid language tag: %s' % ", ".join([err.message for err in tags.tag(language_tag).errors])
        ))


def languagetag_checkduplicate(node, language_tag, languages_manager, errors):
    language_present = languages_manager.count_languages(language_tag)
    if language_present:
        errors.append(colander.Invalid(
            node,
            'Duplicate language tag: %s' % language_tag)
        )


def subordinate_arrays_only_in_concept_rule(errors, node, concept_type, subordinate_arrays):
    if concept_type != 'concept' and len(subordinate_arrays) > 0:
        errors.append(colander.Invalid(
            node,
            'Only concept can have subordinate arrays.'
        ))


def subordinate_arrays_type_rule(errors, node_location, skos_manager, conceptscheme_id, subordinate_arrays):
    for subordinate_id in subordinate_arrays:
        subordinate = skos_manager.get_thing(subordinate_id, conceptscheme_id)
        if subordinate.type != 'collection':
            errors.append(colander.Invalid(
                node_location,
                'A subordinate array should always be a collection'
            ))


def subordinate_arrays_hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct):
    member_of_hierarchy = []
    subordinate_arrays = []
    if 'subordinate_arrays' in cstruct:
        subordinate_arrays = copy.deepcopy(cstruct['subordinate_arrays'])
        subordinate_arrays = [m['id'] for m in subordinate_arrays]
    if 'member_of' in cstruct:
        member_of = copy.deepcopy(cstruct['member_of'])
        member_of = [m['id'] for m in member_of]
        member_of_hierarchy = member_of
        members_hierarchy_build(skos_manager, conceptscheme_id, member_of, member_of_hierarchy)
    for subordinate_array_id in subordinate_arrays:
        if subordinate_array_id in member_of_hierarchy:
            errors.append(colander.Invalid(
                node_location,
                'The subordinate_array collection of a concept must not itself be a parent of the concept being edited.'
            ))


def superordinates_only_in_concept_rule(errors, node, concept_type, superordinates):
    if concept_type != 'collection' and len(superordinates) > 0:
        errors.append(colander.Invalid(
            node,
            'Only collection can have superordinates.'
        ))


def superordinates_type_rule(errors, node_location, skos_manager, conceptscheme_id, superordinates):
    for superordinate_id in superordinates:
        superordinate = skos_manager.get_thing(superordinate_id, conceptscheme_id)
        if superordinate.type != 'concept':
            errors.append(colander.Invalid(
                node_location,
                'A superordinate should always be a concept'
            ))


def superordinates_hierarchy_rule(errors, node_location, skos_manager, conceptscheme_id, cstruct):
    members_hierarchy = []
    superordinates = []
    if 'superordinates' in cstruct:
        superordinates = copy.deepcopy(cstruct['superordinates'])
        superordinates = [m['id'] for m in superordinates]
    if 'members' in cstruct:
        members = copy.deepcopy(cstruct['members'])
        members = [m['id'] for m in members]
        members_hierarchy = members
        members_hierarchy_build(skos_manager, conceptscheme_id, members, members_hierarchy)
    for superordinates_id in superordinates:
        if superordinates_id in members_hierarchy:
            errors.append(colander.Invalid(
                node_location,
                'The superordinates of a collection must not itself be a member of the collection being edited.'
            ))
