"""Add extra to projec_enumerators

Revision ID: 03e0cf2a2675
Revises: fab613014586
Create Date: 2022-09-21 10:08:08.324690

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "03e0cf2a2675"
down_revision = "fab613014586"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "prjenumerator",
        sa.Column(
            "extra", mysql.MEDIUMTEXT(collation="utf8mb4_unicode_ci"), nullable=True
        ),
    )


def downgrade():
    op.drop_column("prjenumerator", "extra")
