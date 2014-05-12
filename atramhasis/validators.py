import copy

import colander
from skosprovider_sqlalchemy.models import (
    Concept as DomainConcept
)
from sqlalchemy.orm.exc import NoResultFound


class Label(colander.MappingSchema):
    label = colander.SchemaNode(
        colander.String(),
        missing=''
    )
    type = colander.SchemaNode(
        colander.String(),
        missing=''
    )
    language = colander.SchemaNode(
        colander.String(),
        missing=''
    )


class Note(colander.MappingSchema):
    note = colander.SchemaNode(
        colander.String(),
        missing=''
    )
    type = colander.SchemaNode(
        colander.String(),
        missing=''
    )
    language = colander.SchemaNode(
        colander.String(),
        missing=''
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


def concept_schema_validator(node, cstruct):
    request = node.bindings['request']
    conceptscheme_id = node.bindings['conceptscheme_id']
    narrower = None
    broader = None
    related = None
    r_validated = False
    n_validated = False
    b_validated = False
    if 'labels' in cstruct:
        labels = copy.deepcopy(cstruct['labels'])
        max_preflabels_rule(node, labels)
    if 'related' in cstruct:
        related = copy.deepcopy(cstruct['related'])
        r_validated = concept_exists_andnot_different_conceptscheme_rule(node['related'], request,
                                                                         conceptscheme_id, related)
    if 'narrower' in cstruct:
        narrower = copy.deepcopy(cstruct['narrower'])
        n_validated = concept_exists_andnot_different_conceptscheme_rule(node['narrower'], request,
                                                                         conceptscheme_id, narrower)
    if 'broader' in cstruct:
        broader = copy.deepcopy(cstruct['broader'])
        b_validated = concept_exists_andnot_different_conceptscheme_rule(node['broader'], request,
                                                                         conceptscheme_id, broader)
    if 'members' in cstruct:
        members = copy.deepcopy(cstruct['members'])
        b_validated = concept_exists_andnot_different_conceptscheme_rule(node['members'], request,
                                                                         conceptscheme_id, members)
    if r_validated and n_validated and b_validated:
        concept_type_rule(node['narrower'], request, conceptscheme_id, narrower)
        narrower_hierarchy_rule(node['narrower'], request, conceptscheme_id, cstruct)
        concept_type_rule(node['broader'], request, conceptscheme_id, broader)
        broader_hierarchy_rule(node['broader'], request, conceptscheme_id, cstruct)
        concept_type_rule(node['related'], request, conceptscheme_id, related)


def max_preflabels_rule(node, labels):
    preflabel_found = []
    for label in labels:
        if label['type'] == 'prefLabel':
            if label['language'] in preflabel_found:
                raise colander.Invalid(
                    node['labels'],
                    'A concept or collection can have only one prefLabel per language.'
                )
            else:
                preflabel_found.append(label['language'])


def concept_type_rule(node_location, request, conceptscheme_id, members):
    for member_concept_id in members:
        member_concept = request.db.query(DomainConcept).filter_by(concept_id=member_concept_id,
                                                                   conceptscheme_id=conceptscheme_id).one()
        if member_concept.type != 'concept':
            raise colander.Invalid(
                node_location,
                'A member should always be a concept, not a collection'
            )


def concept_exists_andnot_different_conceptscheme_rule(node_location, request, conceptscheme_id, members):
    for member_concept_id in members:
        try:
            stored_concept = request.db.query(DomainConcept).filter_by(concept_id=member_concept_id,
                                                                       conceptscheme_id=conceptscheme_id).one()
        except NoResultFound:
            raise colander.Invalid(
                node_location,
                'Concept not found, check concept_id. Please be aware members should be within one scheme'
            )
    return True


def broader_hierarchy_rule(node_location, request, conceptscheme_id, cstruct):
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
            raise colander.Invalid(
                node_location,
                'The broader concept of a concept must not itself be a narrower concept of the concept being edited.'
            )


def narrower_hierarchy_build(request, conceptscheme_id, narrower, narrower_hierarchy):
    for narrower_concept_id in narrower:
        narrower_concept = request.db.query(DomainConcept).filter_by(concept_id=narrower_concept_id,
                                                                     conceptscheme_id=conceptscheme_id).one()
        if narrower_concept is not None:
            narrower_concepts = [n.concept_id for n in narrower_concept.narrower_concepts]
            for narrower_id in narrower_concepts:
                narrower_hierarchy.append(narrower_id)
            narrower_hierarchy_build(request, conceptscheme_id, narrower_concepts, narrower_hierarchy)


def narrower_hierarchy_rule(node_location, request, conceptscheme_id, cstruct):
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
            raise colander.Invalid(
                node_location,
                'The narrower concept of a concept must not itself be a broader concept of the concept being edited.'
            )


def broader_hierarchy_build(request, conceptscheme_id, broader, broader_hierarchy):
    for broader_concept_id in broader:
        broader_concept = request.db.query(DomainConcept).filter_by(concept_id=broader_concept_id,
                                                                    conceptscheme_id=conceptscheme_id).one()
        if broader_concept is not None:
            broader_concepts = [n.concept_id for n in broader_concept.broader_concepts]
            for broader_id in broader_concepts:
                broader_hierarchy.append(broader_id)
            broader_hierarchy_build(request, conceptscheme_id, broader_concepts, broader_hierarchy)