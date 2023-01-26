"""Add new crop taxonomy code to technology table

Revision ID: 7ff68391b854
Revises: 2ddf6c71fa74
Create Date: 2023-01-25 08:12:16.353888

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "7ff68391b854"
down_revision = "2ddf6c71fa74"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "technology",
        sa.Column(
            "croptaxonomy_code",
            sa.Integer(),
            server_default=sa.text("'0'"),
            nullable=False,
        ),
    )
    op.create_index(
        op.f("ix_technology_croptaxonomy_code"),
        "technology",
        ["croptaxonomy_code"],
        unique=False,
    )
    op.create_foreign_key(
        op.f("fk_technology_croptaxonomy_code_croptaxonomy"),
        "technology",
        "croptaxonomy",
        ["croptaxonomy_code"],
        ["taxonomy_code"],
        ondelete="RESTRICT",
    )


def downgrade():
    op.drop_constraint(
        op.f("fk_technology_croptaxonomy_code_croptaxonomy"),
        "technology",
        type_="foreignkey",
    )
    op.drop_column("technology", "croptaxonomy_code")
