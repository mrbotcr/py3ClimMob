"""Control extras in Enumerators

Revision ID: fab613014586
Revises: 879828571879
Create Date: 2022-09-12 10:25:04.831139

"""
from alembic import op
from sqlalchemy.orm.session import Session

# revision identifiers, used by Alembic.
revision = "fab613014586"
down_revision = "879828571879"
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())
    conn = op.get_bind()
    try:
        conn.execute(
            "CREATE TRIGGER enumerator_update_extra BEFORE UPDATE ON enumerator "
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
        conn.execute("DROP TRIGGER enumerator_update_extra")
    except Exception as e:
        print(str(e))
        exit(1)
    session.commit()
