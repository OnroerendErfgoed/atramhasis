"""alter ConceptVisitLog concept_id to string

Revision ID: 29306f749043
Revises: b2a7d7614973
Create Date: 2024-07-30 09:12:37.521748

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29306f749043'
down_revision = 'b2a7d7614973'


def upgrade():
    with op.batch_alter_table('concept_visit_log') as batch_op:
        batch_op.alter_column('concept_id', type_=sa.String, existing_type=sa.Integer)


def downgrade():
    # Drop concept_visit_log which have non-integer concept_id
    op.execute(
        "DELETE FROM concept_visit_log "
        "WHERE cast(cast(concept_id AS INTEGER) AS TEXT) != concept_id"
    )
    with op.batch_alter_table('concept_visit_log') as batch_op:
        batch_op.alter_column('concept_id', type_=sa.Integer, existing_type=sa.String)
