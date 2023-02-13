"""Languages for conceptschemes.

Revision ID: 2a38d364113b
Revises: 3ac8aca026fd
Create Date: 2015-11-19 15:03:45.587093

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2a38d364113b"
down_revision = "3ac8aca026fd"


def upgrade():

    op.create_table(
        "conceptscheme_language",
        sa.Column("conceptscheme_id", sa.Integer(), nullable=False),
        sa.Column("language_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ["conceptscheme_id"],
            ["conceptscheme.id"],
        ),
        sa.ForeignKeyConstraint(
            ["language_id"],
            ["language.id"],
        ),
        sa.PrimaryKeyConstraint("conceptscheme_id", "language_id"),
    )


def downgrade():

    op.drop_table("conceptscheme_language")
