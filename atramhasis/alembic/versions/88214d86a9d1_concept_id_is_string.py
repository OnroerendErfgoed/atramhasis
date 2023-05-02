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
    with op.batch_alter_table('concept') as batch_op:
        batch_op.alter_column('concept_id', type_=sa.String, existing_type=sa.Integer)


def downgrade():
    # Drop concepts which have non-integer concept_id
    op.execute("DELETE FROM concept WHERE cast(cast(concept_id AS INTEGER) AS TEXT) != concept_id")
    with op.batch_alter_table('concept') as batch_op:
        batch_op.alter_column('concept_id', existing_type=sa.String, type_=sa.Integer)
