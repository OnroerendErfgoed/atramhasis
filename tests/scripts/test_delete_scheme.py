from skosprovider_sqlalchemy.models import Collection
from skosprovider_sqlalchemy.models import Concept
from skosprovider_sqlalchemy.models import ConceptScheme
from skosprovider_sqlalchemy.models import Label
from skosprovider_sqlalchemy.models import LabelType
from skosprovider_sqlalchemy.models import Language
from skosprovider_sqlalchemy.models import Note
from skosprovider_sqlalchemy.models import NoteType
from skosprovider_sqlalchemy.models import Source
from skosprovider_sqlalchemy.models import Visitation
from sqlalchemy import select

from atramhasis.scripts import delete_scheme
from tests import DbTest


class DeleteSchemeTest(DbTest):

    def test_delete(self):
        query = select(ConceptScheme.id)
        scheme_ids = self.session.execute(query).scalars().all()
        for scheme_id in scheme_ids:
            delete_scheme.delete_scheme(self.session, scheme_id)

        assert len(self.session.execute(select(ConceptScheme)).all()) == 0
        assert len(self.session.execute(select(Concept)).all()) == 0
        assert len(self.session.execute(select(Collection)).all()) == 0
        assert len(self.session.execute(select(Note)).all()) == 0
        assert len(self.session.execute(select(Source)).all()) == 0
        assert len(self.session.execute(select(Visitation)).all()) == 0
        assert len(self.session.execute(select(Label)).all()) == 0
        assert len(self.session.execute(select(LabelType)).all()) != 0
        assert len(self.session.execute(select(NoteType)).all()) != 0
        assert len(self.session.execute(select(Language)).all()) != 0
