import copy

import colander
from skosprovider_sqlalchemy.models import (
    Concept as DomainConcept,
    Collection as DomainCollection,
    Thing, LabelType, Language)
from sqlalchemy.orm.exc import NoResultFound
from atramhasis.errors import ValidationError


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


class Concepts(colander.SequenceSchema):
    concept = colander.SchemaNode(
        colander.Int(),
        missing=None
    )


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


def concept_schema_validator(node, cstruct):
    request = node.bindings['request']
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
    if 'labels' in cstruct:
        labels = copy.deepcopy(cstruct['labels'])
        label_type_rule(errors, node, request, labels)
        label_lang_rule(errors, node, request, labels)
        max_preflabels_rule(errors, node, labels)
    if 'related' in cstruct:
        related = copy.deepcopy(cstruct['related'])
        r_validated = concept_exists_andnot_different_conceptscheme_rule(errors, node['related'], request,
                                                                         conceptscheme_id, related)
        concept_relations_rule(errors, node, related, concept_type)
    if 'narrower' in cstruct:
        narrower = copy.deepcopy(cstruct['narrower'])
        n_validated = concept_exists_andnot_different_conceptscheme_rule(errors, node['narrower'], request,
                                                                         conceptscheme_id, narrower)
        concept_relations_rule(errors, node, narrower, concept_type)
    if 'broader' in cstruct:
        broader = copy.deepcopy(cstruct['broader'])
        b_validated = concept_exists_andnot_different_conceptscheme_rule(errors, node['broader'], request,
                                                                         conceptscheme_id, broader)
        concept_relations_rule(errors, node, broader, concept_type)
    if 'members' in cstruct:
        members = copy.deepcopy(cstruct['members'])
        m_validated = concept_exists_andnot_different_conceptscheme_rule(errors, node['members'], request,
                                                                         conceptscheme_id, members)
    if 'member_of' in cstruct:
        member_of = copy.deepcopy(cstruct['member_of'])
        o_validated = concept_exists_andnot_different_conceptscheme_rule(errors, node['member_of'], request,
                                                                         conceptscheme_id, member_of)
    if r_validated and n_validated and b_validated:
        concept_type_rule(errors, node['narrower'], request, conceptscheme_id, narrower)
        narrower_hierarchy_rule(errors, node['narrower'], request, conceptscheme_id, cstruct)
        concept_type_rule(errors, node['broader'], request, conceptscheme_id, broader)
        broader_hierarchy_rule(errors, node['broader'], request, conceptscheme_id, cstruct)
        concept_type_rule(errors, node['related'], request, conceptscheme_id, related)

    if m_validated and o_validated:
        members_only_in_collection_rule(errors, node, concept_type, members)
        collection_members_unique_rule(errors, node['members'], members)
        collection_type_rule(errors, node['member_of'], request, conceptscheme_id, member_of)
        memberof_hierarchy_rule(errors, node['member_of'], request, conceptscheme_id, cstruct)
        members_hierarchy_rule(errors, node['members'], request, conceptscheme_id, cstruct)

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


def label_type_rule(errors, node, request, labels):
    label_types = request.db.query(LabelType).all()
    label_types = [label_type.name for label_type in label_types]
    for label in labels:
        if label['type'] not in label_types:
            errors.append(colander.Invalid(
                node['labels'],
                'Invalid labeltype.'
            ))


def label_lang_rule(errors, node, request, labels):
    languages = request.db.query(Language).all()
    languages = [language.id for language in languages]
    for label in labels:
        if label['language'] not in languages:
            errors.append(colander.Invalid(
                node['labels'],
                'Invalid language.'
            ))


def concept_type_rule(errors, node_location, request, conceptscheme_id, members):
    for member_concept_id in members:
        member_concept = request.db.query(Thing).filter_by(concept_id=member_concept_id,
                                                                   conceptscheme_id=conceptscheme_id).one()
        if member_concept.type != 'concept':
            errors.append(colander.Invalid(
                node_location,
                'A member should always be a concept, not a collection'
            ))


def collection_type_rule(errors, node_location, request, conceptscheme_id, members):
    for member_collection_id in members:
        member_collection = request.db.query(Thing).filter_by(concept_id=member_collection_id,
                                                                         conceptscheme_id=conceptscheme_id).one()
        if member_collection.type != 'collection':
            errors.append(colander.Invalid(
                node_location,
                'A member_of parent should always be a collection'
            ))


def concept_exists_andnot_different_conceptscheme_rule(errors, node_location, request, conceptscheme_id, members):
    for member_concept_id in members:
        try:
            stored_concept = request.db.query(Thing).filter_by(concept_id=member_concept_id,
                                                               conceptscheme_id=conceptscheme_id).one()
        except NoResultFound:
            errors.append(colander.Invalid(
                node_location,
                'Concept not found, check concept_id. Please be aware members should be within one scheme'
            ))
            return False
    return True


def broader_hierarchy_rule(errors, node_location, request, conceptscheme_id, cstruct):
    narrower_hierarchy = []
    broader = []
    if 'broader' in cstruct:
        broader = copy.deepcopy(cstruct['broader'])
    if 'narrower' in cstruct:
        narrower = copy.deepcopy(cstruct['narrower'])
        narrower_hierarchy = narrower
        narrower_hierarchy_build(request, conceptscheme_id, narrower, narrower_hierarchy)
    for broader_concept_id in broader:
        if broader_concept_id in narrower_hierarchy:
            errors.append(colander.Invalid(
                node_location,
                'The broader concept of a concept must not itself be a narrower concept of the concept being edited.'
            ))


def narrower_hierarchy_build(request, conceptscheme_id, narrower, narrower_hierarchy):
    for narrower_concept_id in narrower:
        narrower_concept = request.db.query(DomainConcept).filter_by(concept_id=narrower_concept_id,
                                                                     conceptscheme_id=conceptscheme_id).one()
        if narrower_concept is not None and narrower_concept.type == 'concept':
            narrower_concepts = [n.concept_id for n in narrower_concept.narrower_concepts]
            for narrower_id in narrower_concepts:
                narrower_hierarchy.append(narrower_id)
            narrower_hierarchy_build(request, conceptscheme_id, narrower_concepts, narrower_hierarchy)


def narrower_hierarchy_rule(errors, node_location, request, conceptscheme_id, cstruct):
    broader_hierarchy = []
    narrower = []
    if 'narrower' in cstruct:
        narrower = copy.deepcopy(cstruct['narrower'])
    if 'broader' in cstruct:
        broader = copy.deepcopy(cstruct['broader'])
        broader_hierarchy = broader
        broader_hierarchy_build(request, conceptscheme_id, broader, broader_hierarchy)
    for narrower_concept_id in narrower:
        if narrower_concept_id in broader_hierarchy:
            errors.append(colander.Invalid(
                node_location,
                'The narrower concept of a concept must not itself be a broader concept of the concept being edited.'
            ))


def broader_hierarchy_build(request, conceptscheme_id, broader, broader_hierarchy):
    for broader_concept_id in broader:
        broader_concept = request.db.query(Thing).filter_by(concept_id=broader_concept_id,
                                                                    conceptscheme_id=conceptscheme_id).one()
        if broader_concept is not None and broader_concept.type == 'concept':
            broader_concepts = [n.concept_id for n in broader_concept.broader_concepts]
            for broader_id in broader_concepts:
                broader_hierarchy.append(broader_id)
            broader_hierarchy_build(request, conceptscheme_id, broader_concepts, broader_hierarchy)


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


def memberof_hierarchy_rule(errors, node_location, request, conceptscheme_id, cstruct):
    members_hierarchy = []
    memberof = []
    if 'member_of' in cstruct:
        memberof = copy.deepcopy(cstruct['member_of'])
    if 'members' in cstruct:
        members = copy.deepcopy(cstruct['members'])
        members_hierarchy = members
        members_hierarchy_build(request, conceptscheme_id, members, members_hierarchy)
    for memberof_concept_id in memberof:
        if memberof_concept_id in members_hierarchy:
            errors.append(colander.Invalid(
                node_location,
                'The parent member_of collection of a concept must not itself be a member of the concept being edited.'
            ))


def members_hierarchy_build(request, conceptscheme_id, members, members_hierarchy):
    for members_concept_id in members:
        members_concept = request.db.query(Thing).filter_by(concept_id=members_concept_id,
                                                            conceptscheme_id=conceptscheme_id).one()
        if members_concept is not None and members_concept.type == 'collection':
            members_concepts = [n.concept_id for n in members_concept.members]
            for members_id in members_concepts:
                members_hierarchy.append(members_id)
            members_hierarchy_build(request, conceptscheme_id, members_concepts, members_hierarchy)


def members_hierarchy_rule(errors, node_location, request, conceptscheme_id, cstruct):
    memberof_hierarchy = []
    members = []
    if 'members' in cstruct:
        members = copy.deepcopy(cstruct['members'])
    if 'member_of' in cstruct:
        member_of = copy.deepcopy(cstruct['member_of'])
        memberof_hierarchy = member_of
        memberof_hierarchy_build(request, conceptscheme_id, member_of, memberof_hierarchy)
    for member_concept_id in members:
        if member_concept_id in memberof_hierarchy:
            errors.append(colander.Invalid(
                node_location,
                'The item of a members collection must not itself be a parent of the concept/collection being edited.'
            ))


def memberof_hierarchy_build(request, conceptscheme_id, member_of, memberof_hierarchy):
    for memberof_concept_id in member_of:
        memberof_concept = request.db.query(Thing).filter_by(concept_id=memberof_concept_id,
                                                             conceptscheme_id=conceptscheme_id).one()
        if memberof_concept is not None:
            memberof_concepts = [n.concept_id for n in memberof_concept.member_of]
            for memberof_id in memberof_concepts:
                memberof_hierarchy.append(memberof_id)
            memberof_hierarchy_build(request, conceptscheme_id, memberof_concepts, memberof_hierarchy)