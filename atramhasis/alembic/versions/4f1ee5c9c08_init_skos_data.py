"""init SKOS data

Revision ID: 4f1ee5c9c08
Revises: 3924a7ad2f8
Create Date: 2014-04-15 16:12:09.144433

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column
from sqlalchemy.sql import table

# revision identifiers, used by Alembic.
revision = "4f1ee5c9c08"
down_revision = "3924a7ad2f8"


notetype_table = table(
    "notetype", column("name", sa.String), column("description", sa.String)
)

labeltype_table = table(
    "labeltype", column("name", sa.String), column("description", sa.String)
)

language_table = table("language", column("id", sa.String), column("name", sa.String))


def upgrade():
    op.bulk_insert(
        notetype_table,
        [
            {"name": "changeNote", "description": "A change note."},
            {"name": "definition", "description": "A definition."},
            {"name": "editorialNote", "description": "An editorial note."},
            {"name": "example", "description": "An example."},
            {"name": "historyNote", "description": "A historynote."},
            {"name": "scopeNote", "description": "A scopenote."},
            {"name": "note", "description": "A note."},
        ],
    )

    op.bulk_insert(
        labeltype_table,
        [
            {"name": "hiddenLabel", "description": "A hidden label."},
            {"name": "altLabel", "description": "An alternative label."},
            {"name": "prefLabel", "description": "A preferred label."},
        ],
    )

    op.bulk_insert(
        language_table,
        [
            {"id": "la", "name": "Latin"},
            {"id": "nl", "name": "Dutch"},
            {"id": "vls", "name": "Flemish"},
            {"id": "en", "name": "English"},
            {"id": "fr", "name": "French"},
            {"id": "de", "name": "German"},
        ],
    )
    pass


def downgrade():
    op.execute(notetype_table.delete())
    op.execute(labeltype_table.delete())
    op.execute(language_table.delete())
    pass
