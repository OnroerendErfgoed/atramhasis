"""add skos matches

Revision ID: 441c5a16ef8
Revises: 4f1ee5c9c08
Create Date: 2014-10-24 11:04:10.310845

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column
from sqlalchemy.sql import table

# revision identifiers, used by Alembic.
revision = "441c5a16ef8"
down_revision = "4f1ee5c9c08"


def upgrade():
    op.create_table(
        "matchtype",
        sa.Column("name", sa.String(length=20), nullable=False, primary_key=True),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_table(
        "match",
        sa.Column("uri", sa.String(length=512), nullable=False),
        sa.Column("concept_id", sa.Integer, nullable=False),
        sa.Column("matchtype_id", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(
            ["concept_id"],
            ["concept.id"],
        ),
        sa.ForeignKeyConstraint(
            ["matchtype_id"],
            ["matchtype.name"],
        ),
        sa.PrimaryKeyConstraint("uri", "concept_id", "matchtype_id"),
    )
    op.bulk_insert(
        table(
            "matchtype",
            column("name", sa.String),
            column("description", sa.Text),
        ),
        [
            {
                "name": "closeMatch",
                "description": "Indicates that two concepts are sufficiently similar that they can be used interchangeably in some information retrieval applications.",
            },
            {
                "name": "exactMatch",
                "description": "Indicates that there is a high degree of confidence that two concepts can be used interchangeably across a wide range of information retrieval applications.",
            },
            {
                "name": "broadMatch",
                "description": "Indicates that one concept has a broader match with another one.",
            },
            {
                "name": "narrowMatch",
                "description": "Indicates that one concept has a narrower match with another one.",
            },
            {
                "name": "relatedMatch",
                "description": "Indicates that there is an associative mapping between two concepts.",
            },
        ],
    )


def downgrade():
    op.drop_table("match")
    op.drop_table("matchtype")
