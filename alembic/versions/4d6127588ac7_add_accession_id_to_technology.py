"""Add accession ID to technology

Revision ID: 4d6127588ac7
Revises: 1f4057c63fb9
Create Date: 2023-05-03 10:58:24.421159

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "4d6127588ac7"
down_revision = "1f4057c63fb9"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "technology",
        sa.Column("tech_accession_id", sa.Unicode(length=255), nullable=True),
    )


def downgrade():
    op.drop_column("technology", "tech_accession_id")
