"""climmobShare - Prjcombination - add project_id

Revision ID: 4ffed1d2857a
Revises: 2f5506c68d26
Create Date: 2021-08-03 15:55:58.683745

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm.session import Session
from climmob.models.climmobv4 import Prjcombination, Project

# revision identifiers, used by Alembic.
revision = "4ffed1d2857a"
down_revision = "2f5506c68d26"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "prjcombination", sa.Column("project_id", sa.Unicode(length=64), nullable=True)
    )

    session = Session(bind=op.get_bind())
    try:
        projects = session.execute("Select * from project")
        for project in projects:
            session.execute(
                "UPDATE prjcombination SET project_id = '"
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
    op.drop_column("prjcombination", "project_id")
    # ### end Alembic commands ###