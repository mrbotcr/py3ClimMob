"""climmobShare - Regsection - Remove user_name and project_cod

Revision ID: 10cd82efb58d
Revises: 1d20c409a2f8
Create Date: 2021-08-19 13:47:54.977942

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "10cd82efb58d"
down_revision = "1d20c409a2f8"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("regsection", "user_name")
    op.drop_column("regsection", "project_cod")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "regsection", sa.Column("project_cod", mysql.VARCHAR(length=80), nullable=False)
    )
    op.add_column(
        "regsection", sa.Column("user_name", mysql.VARCHAR(length=80), nullable=False)
    )
    # ### end Alembic commands ###