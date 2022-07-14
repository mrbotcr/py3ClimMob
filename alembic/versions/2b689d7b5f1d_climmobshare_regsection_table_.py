"""climmobShare - Regsection - table relationship

Revision ID: 2b689d7b5f1d
Revises: d33ff297d37a
Create Date: 2021-08-10 10:03:07.493743

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "2b689d7b5f1d"
down_revision = "d33ff297d37a"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("PRIMARY", "regsection", type_="primary")
    op.create_primary_key("pk_regsection", "regsection", ["project_id", "section_id"])

    op.create_foreign_key(
        op.f("fk_regsection_project_id_project"),
        "regsection",
        "project",
        ["project_id"],
        ["project_id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("PRIMARY", "regsection", type_="primary")
    op.create_primary_key(
        "pk_regsection", "regsection", ["user_name", "project_cod", "section_id"]
    )

    op.drop_constraint(
        op.f("fk_regsection_project_id_project"), "regsection", type_="foreignkey"
    )
    # ### end Alembic commands ###
