"""Create tables ProjectUnitOfAnalysis and I18nProjectUnitOfAnalysis

Revision ID: 18a87d7851ee
Revises: fa9f3d8cccf8
Create Date: 2024-11-18 10:57:16.725859

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "18a87d7851ee"
down_revision = "fa9f3d8cccf8"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "project_unit_of_analysis",
        sa.Column("puoa_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("puoa_name", sa.Unicode(length=120), nullable=False),
        sa.Column("puoa_lang", sa.Unicode(length=5), nullable=False),
        sa.ForeignKeyConstraint(
            ["puoa_lang"],
            ["i18n.lang_code"],
            name=op.f("fk_project_unit_of_analysis_puoa_lang_i18n"),
        ),
        sa.PrimaryKeyConstraint("puoa_id", name=op.f("pk_project_unit_of_analysis")),
    )
    op.create_table(
        "i18n_project_unit_of_analysis",
        sa.Column("puoa_id", sa.Integer(), nullable=False),
        sa.Column("lang_code", sa.Unicode(length=5), nullable=False),
        sa.Column("puoa_name", sa.Unicode(length=120), nullable=False),
        sa.ForeignKeyConstraint(
            ["lang_code"],
            ["i18n.lang_code"],
            name=op.f("fk_i18n_project_unit_of_analysis_lang_code_i18n"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["puoa_id"],
            ["project_unit_of_analysis.puoa_id"],
            name=op.f(
                "fk_i18n_project_unit_of_analysis_puoa_id_project_unit_of_analysis"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "puoa_id", "lang_code", name=op.f("pk_i18n_project_unit_of_analysis")
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("i18n_project_unit_of_analysis")
    op.drop_table("project_unit_of_analysis")
    # ### end Alembic commands ###
