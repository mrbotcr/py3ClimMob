"""Fix extras

Revision ID: 818e37fbf3e1
Revises: ac44678ec11e
Create Date: 2021-01-27 09:19:21.867289

"""
from alembic import op
from sqlalchemy.orm.session import Session

# revision identifiers, used by Alembic.
revision = '818e37fbf3e1'
down_revision = 'ac44678ec11e'
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())
    conn = op.get_bind()
    try:
        conn.execute(
            "CREATE TRIGGER user_update_extra BEFORE UPDATE ON user "
            "FOR EACH ROW BEGIN IF IFnull(OLD.extra,'{}') <> IFNULL(NEW.extra,'{}') THEN "
            "IF ISNULL(NEW.extra) = 0 THEN SET "
            "NEW.extra= JSON_MERGE_PATCH(IFnull(OLD.extra,'{}'),IFNULL(NEW.extra,'{}')); "
            "END IF; END IF; END;"
        )

        conn.execute(
            "CREATE TRIGGER project_update_extra BEFORE UPDATE ON project "
            "FOR EACH ROW BEGIN IF IFnull(OLD.extra,'{}') <> IFNULL(NEW.extra,'{}') THEN "
            "IF ISNULL(NEW.extra) = 0 THEN SET "
            "NEW.extra = JSON_MERGE_PATCH(IFnull(OLD.extra,'{}'),IFNULL(NEW.extra,'{}')); "
            "END IF; END IF; END;"
        )

        conn.execute(
            "CREATE TRIGGER question_update_extra BEFORE UPDATE ON question "
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
        conn.execute("DROP TRIGGER user_update_extra")
        conn.execute("DROP TRIGGER project_update_extra")
        conn.execute("DROP TRIGGER question_update_extra")
    except Exception as e:
        print(str(e))
        exit(1)
    session.commit()

