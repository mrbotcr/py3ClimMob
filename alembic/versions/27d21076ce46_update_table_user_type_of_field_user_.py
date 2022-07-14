"""Update table User type of field user_password

Revision ID: 27d21076ce46
Revises: 6dc0b538ef4c
Create Date: 2022-03-18 12:29:06.851744

"""
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = "27d21076ce46"
down_revision = "6dc0b538ef4c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "user",
        "user_password",
        existing_type=mysql.VARCHAR(
            charset="utf8mb4", collation="utf8mb4_unicode_ci", length=80
        ),
        type_=mysql.MEDIUMTEXT(collation="utf8mb4_unicode_ci"),
        existing_nullable=True,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "user",
        "user_password",
        existing_type=mysql.MEDIUMTEXT(collation="utf8mb4_unicode_ci"),
        type_=mysql.VARCHAR(
            charset="utf8mb4", collation="utf8mb4_unicode_ci", length=80
        ),
        existing_nullable=True,
    )
    # ### end Alembic commands ###
