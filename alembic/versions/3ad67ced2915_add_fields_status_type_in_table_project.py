"""Add fields status, type in table Project

Revision ID: 3ad67ced2915
Revises: 7e160694b2f9
Create Date: 2024-05-10 12:17:12.169957

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm.session import Session

# revision identifiers, used by Alembic.
revision = "3ad67ced2915"
down_revision = "7e160694b2f9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column(
        "project",
        sa.Column(
            "project_status",
            sa.Integer(),
            server_default=sa.text("'0'"),
            nullable=False,
        ),
    )
    op.add_column(
        "project",
        sa.Column(
            "project_type", sa.Integer(), server_default=sa.text("'0'"), nullable=False
        ),
    )
    op.create_foreign_key(
        op.f("fk_project_project_type_project_type"),
        "project",
        "project_type",
        ["project_type"],
        ["prjtype_id"],
    )
    op.create_foreign_key(
        op.f("fk_project_project_status_project_status"),
        "project",
        "project_status",
        ["project_status"],
        ["prjstatus_id"],
    )

    session = Session(bind=op.get_bind())
    try:
        projects = session.execute("Select * from project")
        for project in projects:

            if project.project_regstatus == 0:
                value = 1
            else:
                value = 2

            session.execute(
                "UPDATE project SET project_status = '{}' WHERE (`project_id` = '{}');".format(
                    value, project.project_id
                )
            )

    except Exception as e:
        print(str(e))
        exit(1)

    session.commit()
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.drop_constraint(
        op.f("fk_project_project_status_project_status"), "project", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_project_project_type_project_type"), "project", type_="foreignkey"
    )
    op.drop_column("project", "project_type")
    op.drop_column("project", "project_status")
    # ### end Alembic commands ###