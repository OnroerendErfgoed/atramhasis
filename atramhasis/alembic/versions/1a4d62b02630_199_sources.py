"""199 Sources.

Revision ID: 1a4d62b02630
Revises: 2a38d364113b
Create Date: 2015-12-08 12:06:20.303601

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1a4d62b02630"
down_revision = "2a38d364113b"


def upgrade():

    op.create_table(
        "source",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("citation", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "conceptscheme_source",
        sa.Column("conceptscheme_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["conceptscheme_id"],
            ["conceptscheme.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["source.id"],
        ),
        sa.PrimaryKeyConstraint("conceptscheme_id", "source_id"),
    )

    op.create_table(
        "concept_source",
        sa.Column("concept_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["concept_id"],
            ["concept.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["source.id"],
        ),
        sa.PrimaryKeyConstraint("concept_id", "source_id"),
    )


def downgrade():

    op.drop_table("conceptscheme_source")
    op.drop_table("concept_source")
    op.drop_table("source")
