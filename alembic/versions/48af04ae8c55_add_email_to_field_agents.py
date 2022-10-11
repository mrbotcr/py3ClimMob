"""Add email to field agents

Revision ID: 48af04ae8c55
Revises: 6c0b8e792e2d
Create Date: 2022-10-11 08:17:07.448488

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '48af04ae8c55'
down_revision = '6c0b8e792e2d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('enumerator', sa.Column('enum_email', sa.Unicode(length=120), server_default=sa.text("''"), nullable=True))


def downgrade():
    op.drop_column('enumerator', 'enum_email')
