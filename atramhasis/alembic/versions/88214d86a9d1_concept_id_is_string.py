"""concept_id is string

Revision ID: 88214d86a9d1
Revises: 79ff53a30228
Create Date: 2023-01-18 13:17:21.700138

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88214d86a9d1'
down_revision = '79ff53a30228'


def upgrade():
    op.alter_column('concept', 'concept_id', _type=sa.String)


def downgrade():
    op.alter_column('concept', 'concept_id', _type=sa.Integer)
