"""Create anonymized values table

Revision ID: a43877478276
Revises: ac96c89a6cf7
Create Date: 2026-05-26 13:37:32.978499

"""
from sqlalchemy.orm.session import Session

from alembic import op
from climmob.models.climmobv4 import Project, userProject

# revision identifiers, used by Alembic.
revision = "a43877478276"
down_revision = "ac96c89a6cf7"
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())
    projects = (
        session.query(userProject.user_name, Project.project_cod)
        .filter(userProject.access_type == 1)
        .filter(userProject.project_id == Project.project_id)
        .filter(Project.project_regstatus > 0)
        .all()
    )

    for project in projects:
        user_project = f"{project.user_name}_{project.project_cod}"
        query = (
            f"CREATE TABLE IF NOT EXISTS {user_project}.anonymized "
            "(`form_id` varchar(255) NOT NULL,"
            "`reg_id` int NOT NULL,"
            "`col_name` varchar(255) NOT NULL,"
            "`value` varchar(255) DEFAULT NULL,"
            "PRIMARY KEY (`form_id`,`reg_id`,`col_name`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        )
        session.execute(query)


def downgrade():
    session = Session(bind=op.get_bind())
    projects = (
        session.query(userProject.user_name, Project.project_cod)
        .filter(userProject.access_type == 1)
        .filter(userProject.project_id == Project.project_id)
        .filter(Project.project_regstatus > 0)
        .all()
    )

    for project in projects:
        user_project = f"{project.user_name}_{project.project_cod}"
        query = f"DROP TABLE IF EXISTS {user_project}.anonymized"
        session.execute(query)
