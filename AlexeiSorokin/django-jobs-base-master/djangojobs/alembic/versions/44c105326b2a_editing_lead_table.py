"""editing lead table

Revision ID: 44c105326b2a
Revises: 
Create Date: 2017-05-22 14:38:35.978427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44c105326b2a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('lead', sa.Column('source', sa.String))
    op.add_column('lead', sa.Column('vacancy_link', sa.String))
    op.add_column('lead', sa.Column('company_link', sa.String))
    op.add_column('lead', sa.Column('company_name', sa.String))
    pass


def downgrade():
    pass
