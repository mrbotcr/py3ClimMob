"""climmobShare - Asssection - add project_id

Revision ID: 7954263d0aa1
Revises: 169df9ac9d29
Create Date: 2021-08-03 12:02:52.220755

"""
import sqlalchemy as sa
from sqlalchemy.orm.session import Session

from alembic import op

# revision identifiers, used by Alembic.
revision = "7954263d0aa1"
down_revision = "169df9ac9d29"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "asssection", sa.Column("project_id", sa.Unicode(length=64), nullable=True)
    )

    session = Session(bind=op.get_bind())
    try:
        projects = session.execute("Select * from project")
        for project in projects:
            session.execute(
                "UPDATE asssection SET project_id = '"
                + project.project_id
                + "' WHERE (user_name = '"
                + project.user_name
                + "') and (project_cod = '"
                + project.project_cod
                + "');"
            )
    except Exception as e:
        print(str(e))
        exit(1)

    session.commit()
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("asssection", "project_id")
    # ### end Alembic commands ###
