"""Remove old crop relationship

Revision ID: ec89eea99566
Revises: de0a6c5ed7b9
Create Date: 2023-01-25 06:53:56.521892

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "ec89eea99566"
down_revision = "de0a6c5ed7b9"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        op.f("fk_technology_crop_code_crop"),
        "technology",
        type_="foreignkey",
    )
    op.drop_column("technology", "crop_code")


def downgrade():
    op.add_column(
        "technology",
        sa.Column(
            "crop_code", sa.Integer(), server_default=sa.text("'0'"), nullable=False
        ),
    )
    op.create_index(
        op.f("ix_technology_crop_code"), "technology", ["crop_code"], unique=False
    )
    op.create_foreign_key(
        op.f("fk_technology_crop_code_crop"),
        "technology",
        "crop",
        ["crop_code"],
        ["crop_code"],
        ondelete="RESTRICT",
    )
