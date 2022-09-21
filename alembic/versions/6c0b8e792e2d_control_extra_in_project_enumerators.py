"""Control extra in project enumerators

Revision ID: 6c0b8e792e2d
Revises: 03e0cf2a2675
Create Date: 2022-09-21 13:23:26.982159

"""
from alembic import op
from sqlalchemy.orm.session import Session

# revision identifiers, used by Alembic.
revision = "6c0b8e792e2d"
down_revision = "03e0cf2a2675"
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())
    conn = op.get_bind()
    try:
        conn.execute(
            "CREATE TRIGGER prjenumerator_update_extra BEFORE UPDATE ON prjenumerator "
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
        conn.execute("DROP TRIGGER prjenumerator_update_extra")
    except Exception as e:
        print(str(e))
        exit(1)
    session.commit()
