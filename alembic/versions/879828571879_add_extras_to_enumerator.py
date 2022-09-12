"""Add extras to Enumerator

Revision ID: 879828571879
Revises: f5d54348d6b3
Create Date: 2022-09-12 10:10:44.112826

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "879828571879"
down_revision = "f5d54348d6b3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "enumerator",
        sa.Column(
            "extra", mysql.MEDIUMTEXT(collation="utf8mb4_unicode_ci"), nullable=True
        ),
    )


def downgrade():
    op.drop_column("enumerator", "extra")
