from skosprovider_sqlalchemy.models import Label, Note, Concept


def map_concept(concept, concept_json):
    concept.type = concept_json.get('type', None)
    for label in concept.labels:
        concept.labels.remove(label)
    labels = concept_json.get('labels', [])
    for l in labels:
            label = Label(label=l.get('label', ''), labeltype_id=l.get('type', ''), language_id=l.get('language', ''))
            concept.labels.append(label)
    for note in concept.notes:
        concept.notes.remove(note)
    notes = concept_json.get('notes', [])
    for n in notes:
            note = Note(note=n.get('note', ''), notetype_id=n.get('type', ''), language_id=n.get('language', ''))
            concept.notes.append(note)
    # for rc in concept.related_concepts:
    #     concept.related_concepts.remove(rc)
    # related = concept_json.get('related', [])
    # for related_c in related:
    #     rc = Concept()
    #     concept.related_concepts.append(rc)
    return concept