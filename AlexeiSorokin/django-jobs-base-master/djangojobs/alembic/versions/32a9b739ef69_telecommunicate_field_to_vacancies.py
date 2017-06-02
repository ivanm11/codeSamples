"""telecommunicate field to vacancies

Revision ID: 32a9b739ef69
Revises: 9955a3872b7e
Create Date: 2017-05-23 13:52:47.075112

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32a9b739ef69'
down_revision = '9955a3872b7e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('vacancy', sa.Column('telecommunicate', sa.Boolean))
    pass


def downgrade():
    pass
