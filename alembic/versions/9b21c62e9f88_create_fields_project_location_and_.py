"""Create fields project_location and project_unit_of_analysis table Project

Revision ID: 9b21c62e9f88
Revises: f59051fecf09
Create Date: 2024-12-06 14:57:59.035737

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "9b21c62e9f88"
down_revision = "f59051fecf09"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column("project", sa.Column("project_location", sa.Integer(), nullable=True))
    op.add_column(
        "project", sa.Column("project_unit_of_analysis", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        op.f("fk_project_project_unit_of_analysis_project_unit_of_analysis"),
        "project",
        "project_unit_of_analysis",
        ["project_unit_of_analysis"],
        ["puoa_id"],
    )
    op.create_foreign_key(
        op.f("fk_project_project_location_project_location"),
        "project",
        "project_location",
        ["project_location"],
        ["plocation_id"],
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        op.f("fk_project_project_location_project_location"),
        "project",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_project_project_unit_of_analysis_project_unit_of_analysis"),
        "project",
        type_="foreignkey",
    )
    op.drop_column("project", "project_unit_of_analysis")
    op.drop_column("project", "project_location")
    # ### end Alembic commands ###
