from skosprovider.skos import Concept, Collection, Label, Note


def from_thing(thing):
        '''
        Map a :class:`skosprovider_sqlalchemy.models.Thing` to a :class:`skosprovider.skos.Concept` or
        a :class:`skosprovider.skos.Collection`, depending on the type

        :param :class:`skosprovider_sqlalchemy.models.Thing` thing: Thing
            to map.
        '''
        if thing.type and thing.type == 'collection':
            return Collection(
                id=thing.concept_id,
                uri=thing.uri,
                labels=[
                    Label(l.label, l.labeltype_id, l.language_id)
                    for l in thing.labels
                ],
                members=[member.concept_id for member in thing.members] if hasattr(thing, 'members') else []
            )
        else:
            return Concept(
                id=thing.concept_id,
                uri=thing.uri,
                labels=[
                    Label(l.label, l.labeltype_id, l.language_id)
                    for l in thing.labels
                ],
                notes=[
                    Note(n.note, n.notetype_id, n.language_id)
                    for n in thing.notes
                ],
                broader=[c.concept_id for c in thing.broader_concepts],
                narrower=[c.concept_id for c in thing.narrower_concepts],
                related=[c.concept_id for c in thing.related_concepts],
            )
