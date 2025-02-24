"""Create table MetadaFormLocationUnitOfAnalysis

Revision ID: 1913ec52a5af
Revises: 2fbe0f0d4e88
Create Date: 2024-11-20 10:26:13.197481

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "1913ec52a5af"
down_revision = "2fbe0f0d4e88"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "metadata_form_location_unit_of_analysis",
        sa.Column("metadata_id", sa.Unicode(length=64), nullable=False),
        sa.Column("pluoa_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["metadata_id"],
            ["metadata_form.metadata_id"],
            name=op.f(
                "fk_metadata_form_location_unit_of_analysis_metadata_id_metadata_form"
            ),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["pluoa_id"],
            ["location_unit_of_analysis.pluoa_id"],
            name=op.f(
                "fk_metadata_form_location_unit_of_analysis_pluoa_id_location_unit_of_analysis"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "metadata_id",
            "pluoa_id",
            name=op.f("pk_metadata_form_location_unit_of_analysis"),
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("metadata_form_location_unit_of_analysis")
    # ### end Alembic commands ###
