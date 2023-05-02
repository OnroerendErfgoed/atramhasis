"""Add provider table

Revision ID: b2a7d7614973
Revises: 0978347c16f9
Create Date: 2023-03-22 15:10:27.781804

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b2a7d7614973"
down_revision = "0978347c16f9"


def upgrade():
    op.create_table(
        "provider",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("conceptscheme_id", sa.Integer(), nullable=False),
        sa.Column("uri_pattern", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column(
            "expand_strategy",
            sa.Enum("RECURSE", "VISIT", name="expandstrategy"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["conceptscheme_id"],
            ["conceptscheme.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("provider")
