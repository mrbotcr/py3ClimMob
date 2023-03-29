"""Add field user_admin to user

Revision ID: 96a20bc8d5fe
Revises: 0202a70622fb
Create Date: 2023-03-15 14:07:01.257680

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "96a20bc8d5fe"
down_revision = "0202a70622fb"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user",
        sa.Column(
            "user_admin", sa.Integer(), server_default=sa.text("'0'"), nullable=True
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "user_admin")
    # ### end Alembic commands ###