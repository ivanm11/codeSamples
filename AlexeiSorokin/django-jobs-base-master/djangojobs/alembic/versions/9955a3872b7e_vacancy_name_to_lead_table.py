"""vacancy name to lead table

Revision ID: 9955a3872b7e
Revises: b8dd069ec5d6
Create Date: 2017-05-22 16:28:21.726322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9955a3872b7e'
down_revision = 'b8dd069ec5d6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('lead', sa.Column('vacancy_name', sa.String))
    pass


def downgrade():
    pass
