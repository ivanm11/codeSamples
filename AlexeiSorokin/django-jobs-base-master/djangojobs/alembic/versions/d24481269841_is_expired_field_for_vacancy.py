"""is_expired field for vacancy

Revision ID: d24481269841
Revises: 32a9b739ef69
Create Date: 2017-05-23 14:15:19.270711

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd24481269841'
down_revision = '32a9b739ef69'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('vacancy', sa.Column('is_expired', sa.Boolean))
    pass


def downgrade():
    pass
