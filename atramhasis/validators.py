import colander
from skosprovider_sqlalchemy.models import (
    Concept as DomainConcept
)


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


def concept_schema_validator(node, cstruct):
    request = node.bindings['request']
    conceptscheme_id = node.bindings['conceptscheme_id']
    if 'labels' in cstruct:
        labels = cstruct['labels']
        max_preflabels_rule(node, labels)
    if 'related' in cstruct:
        related = cstruct['related']
        different_conceptscheme_rule(node['related'], request, conceptscheme_id, related)
        concept_type_rule(node['related'], request, conceptscheme_id, related)
    if 'narrower' in cstruct:
        narrower = cstruct['narrower']
        different_conceptscheme_rule(node['narrower'], request, conceptscheme_id, narrower)
        concept_type_rule(node['narrower'], request, conceptscheme_id, narrower)
    if 'broader' in cstruct:
        broader = cstruct['broader']
        different_conceptscheme_rule(node['broader'], request, conceptscheme_id, broader)
        concept_type_rule(node['broader'], request, conceptscheme_id, broader)


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


def different_conceptscheme_rule(node_location, request, conceptscheme_id, members):
    for member_concept_id in members:
        stored_concept = request.db.query(DomainConcept).filter_by(concept_id=member_concept_id,
                                                                   conceptscheme_id=conceptscheme_id).one()
        if stored_concept is None:
            raise colander.Invalid(
                node_location,
                'Concept not found, check concept_id. Please be aware members should be within one scheme'
            )