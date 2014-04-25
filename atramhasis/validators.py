import colander


def sqlalchemy_validator(node, value, model, session=None, msg='%s is invalid'):
    '''
    Validate a sqlalchemy object or identifier.

    Function checks if value is an instance of sqlalchemy model
    or an id of one.

    :param node: A colander SchemaNode.
    :param value: The value to be validated. Can be an instance of the
        SQLAlchemy model or a key of one.
    :param model: A SQLAlchemy model.
    :param session: A SQLAlchemy session. Is required if value is not an
        instance of a SQLAlchemy model.
    :param msg: A msg to attach to a `colander.Invalid` exception.
    :raises colander.Invalid: If not a valid sqlalchemy model.
    '''
    if isinstance(value, model):
        return

    m = session.query(model).get(value)

    if not m:
        raise colander.Invalid(
            node,
            msg % value
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


class Concepts(colander.SequenceSchema):
    concept = Concept()


Concept.broader = Concepts(missing=[])
Concept.narrower = Concepts(missing=[])
Concept.related = Concepts(missing=[])
