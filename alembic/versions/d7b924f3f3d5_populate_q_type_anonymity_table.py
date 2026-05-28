"""populate q-type-anonymity table

Revision ID: d7b924f3f3d5
Revises: e3f8c1e34723
Create Date: 2026-05-27 09:22:28.664206

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "d7b924f3f3d5"
down_revision = "e3f8c1e34723"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    conn = bind.connect()

    question_types = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        27,
    ]

    # all types - remove
    values = [{"type": q_type, "anonymity": 1} for q_type in question_types]

    # integer - range
    values.append({"type": 3, "anonymity": 3})
    # decimal - range
    values.append({"type": 2, "anonymity": 3})
    # text - pseudonym
    values.append({"type": 1, "anonymity": 2})
    # geo point - noise
    values.append({"type": 4, "anonymity": 4})
    # date - month year
    values.append({"type": 13, "anonymity": 6})
    # datetime - month year
    values.append({"type": 15, "anonymity": 6})

    conn.execute(
        sa.text("INSERT INTO question_type_anonymity VALUES (:type, :anonymity)"),
        values,
    )


def downgrade():
    bind = op.get_bind()
    conn = bind.connect()

    conn.execute(sa.text("DELETE FROM question_type_anonymity"))
