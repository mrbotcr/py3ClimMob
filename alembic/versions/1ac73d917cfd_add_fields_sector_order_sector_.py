"""Add fields sector_order, sector_available to sector

Revision ID: 1ac73d917cfd
Revises: 53fa2d2caa8a
Create Date: 2023-03-21 15:08:32.198914

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "1ac73d917cfd"
down_revision = "53fa2d2caa8a"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("sector", sa.Column("section_order", sa.Integer(), nullable=True))
    op.add_column("sector", sa.Column("section_available", sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("sector", "section_available")
    op.drop_column("sector", "section_order")
    # ### end Alembic commands ###