"""is_managed field to company table


Revision ID: a46da0e4dfdd
Revises: d24481269841
Create Date: 2017-05-23 15:22:57.679063

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression


# revision identifiers, used by Alembic.
revision = 'a46da0e4dfdd'
down_revision = 'd24481269841'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('company', sa.Column('is_managed', sa.Boolean, default=False,
                                       nullable=False,
                                       server_default=expression.false()))
    pass


def downgrade():
    pass
