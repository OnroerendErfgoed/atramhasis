"""rename flemish vlaams


Revision ID: 0978347c16f9
Revises: 88214d86a9d1
Create Date: 2023-02-06 13:23:27.009952

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = '0978347c16f9'
down_revision = '88214d86a9d1'

def upgrade():
    op.execute("UPDATE language SET name = 'Vlaams' WHERE id = 'vls'")
    
def downgrade():
    op.execute("UPDATE language SET name = 'Flemish' WHERE id = 'vls'")
