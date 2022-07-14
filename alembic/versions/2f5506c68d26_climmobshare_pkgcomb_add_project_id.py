"""climmobShare - Pkgcomb - add project_id

Revision ID: 2f5506c68d26
Revises: 7597dde01af1
Create Date: 2021-08-03 15:51:23.541628

"""
import sqlalchemy as sa
from sqlalchemy.orm.session import Session

from alembic import op

# revision identifiers, used by Alembic.
revision = "2f5506c68d26"
down_revision = "7597dde01af1"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "pkgcomb", sa.Column("project_id", sa.Unicode(length=64), nullable=True)
    )
    op.add_column(
        "pkgcomb", sa.Column("comb_project_id", sa.Unicode(length=64), nullable=False)
    )

    session = Session(bind=op.get_bind())
    try:
        projects = session.execute("Select * from project")
        for project in projects:
            session.execute(
                "UPDATE pkgcomb SET project_id = '"
                + project.project_id
                + "', comb_project_id= '"
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
    op.drop_column("pkgcomb", "project_id")
    op.drop_column("pkgcomb", "comb_project_id")
    # ### end Alembic commands ###
