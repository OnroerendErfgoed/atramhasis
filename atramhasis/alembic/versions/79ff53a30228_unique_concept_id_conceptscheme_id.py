"""unique concept.id + conceptscheme.id

Revision ID: 79ff53a30228
Revises: 3e9675b35dfc
Create Date: 2020-09-14 12:23:22.546226

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "79ff53a30228"
down_revision = "3e9675b35dfc"


def upgrade():
    with op.batch_alter_table("concept") as batch_op:
        batch_op.create_unique_constraint(
            "uq_concept_concept_id_conceptscheme_id", ["concept_id", "conceptscheme_id"]
        )


def downgrade():
    with op.batch_alter_table("concept") as batch_op:
        batch_op.drop_constraint("uq_concept_concept_id_conceptscheme_id")
