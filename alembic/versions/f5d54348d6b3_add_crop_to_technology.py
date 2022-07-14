"""Add crop to technology

Revision ID: f5d54348d6b3
Revises: 5194a5f1ab00
Create Date: 2022-07-14 08:29:26.540781

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "f5d54348d6b3"
down_revision = "5194a5f1ab00"
branch_labels = None
depends_on = None


def upgrade():
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


def downgrade():
    op.drop_column("technology", "crop_code")
