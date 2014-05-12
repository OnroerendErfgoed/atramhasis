from skosprovider_sqlalchemy.models import Label, Note, Concept, Thing
from sqlalchemy.orm.exc import NoResultFound


def map_concept(concept, concept_json, db_session):
    concept.type = concept_json.get('type', None)
    if concept.type in ('concept', 'collection'):
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
        if concept.type == 'concept':
            concept.related_concepts.clear()
            related = concept_json.get('related', [])
            for related_id in related:
                try:
                    related_concept = db_session.query(Concept).filter_by(concept_id=related_id,
                                                                          conceptscheme_id=concept.conceptscheme_id).one()
                except NoResultFound:
                    related_concept = Concept(concept_id=related_id, conceptscheme_id=concept.conceptscheme_id)
                concept.related_concepts.add(related_concept)
            concept.broader_concepts.clear()
            broader = concept_json.get('broader', [])
            for broader_id in broader:
                try:
                    broader_concept = db_session.query(Concept).filter_by(concept_id=broader_id,
                                                                          conceptscheme_id=concept.conceptscheme_id).one()
                except NoResultFound:
                    broader_concept = Concept(concept_id=broader_id, conceptscheme_id=concept.conceptscheme_id)
                concept.broader_concepts.add(broader_concept)
            concept.narrower_concepts.clear()
            narrower = concept_json.get('narrower', [])
            for narrower_id in narrower:
                try:
                    narrower_concept = db_session.query(Concept).filter_by(concept_id=narrower_id,
                                                                           conceptscheme_id=concept.conceptscheme_id).one()
                except NoResultFound:
                    narrower_concept = Concept(concept_id=narrower_id, conceptscheme_id=concept.conceptscheme_id)
                concept.narrower_concepts.add(narrower_concept)
        if concept.type == 'collection':
            concept.members.clear()
            members = concept_json.get('members', [])
            for member_id in members:
                try:
                    member_concept = db_session.query(Thing).filter_by(concept_id=member_id,
                                                                           conceptscheme_id=concept.conceptscheme_id).one()
                except NoResultFound:
                    member_concept = Concept(concept_id=member_id, conceptscheme_id=concept.conceptscheme_id)
                concept.members.add(member_concept)
    return concept