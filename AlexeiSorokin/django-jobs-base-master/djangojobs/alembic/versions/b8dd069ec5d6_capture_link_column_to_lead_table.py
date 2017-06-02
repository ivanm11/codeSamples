"""capture_link column to lead table

Revision ID: b8dd069ec5d6
Revises: 44c105326b2a
Create Date: 2017-05-22 15:12:12.824200

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8dd069ec5d6'
down_revision = '44c105326b2a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('lead', sa.Column('capture_link', sa.String))
    pass


def downgrade():
    pass
