"""note_markup

Revision ID: 3ac8aca026fd
Revises: 1ad2b6fbcf22
Create Date: 2015-08-17 10:46:02.444677

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3ac8aca026fd"
down_revision = "1ad2b6fbcf22"


def upgrade():
    op.add_column("note", sa.Column("markup", sa.String(20)))


def downgrade():
    with op.batch_alter_table("note") as batch_op:
        batch_op.drop_column("markup")
