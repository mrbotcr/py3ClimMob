"""Fix extras in updates

Revision ID: 0056f2fe1256
Revises: 915e1e3bc787
Create Date: 2022-02-17 19:04:55.008216

"""
from sqlalchemy.orm.session import Session

from alembic import op

# revision identifiers, used by Alembic.
revision = "0056f2fe1256"
down_revision = "915e1e3bc787"
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())
    conn = op.get_bind()
    try:
        conn.execute(
            "CREATE TRIGGER assessment_update_extra BEFORE UPDATE ON assessment "
            "FOR EACH ROW BEGIN IF IFnull(OLD.extra,'{}') <> IFNULL(NEW.extra,'{}') THEN "
            "IF ISNULL(NEW.extra) = 0 THEN SET "
            "NEW.extra = JSON_MERGE_PATCH(IFnull(OLD.extra,'{}'),IFNULL(NEW.extra,'{}')); "
            "END IF; END IF; END;"
        )

    except Exception as e:
        print(str(e))
        exit(1)

    session.commit()


def downgrade():

    session = Session(bind=op.get_bind())
    conn = op.get_bind()
    try:
        conn.execute("DROP TRIGGER assessment_update_extra")
    except Exception as e:
        print(str(e))
        exit(1)
    session.commit()
