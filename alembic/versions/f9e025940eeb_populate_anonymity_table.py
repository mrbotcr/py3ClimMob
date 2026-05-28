"""populate anonymity table

Revision ID: f9e025940eeb
Revises: 5f5f7e519aa0
Create Date: 2026-05-26 15:34:21.989997

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "f9e025940eeb"
down_revision = "5f5f7e519aa0"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    conn = bind.connect()

    values = [
        {"id": 1, "name": "Remove"},
        {"id": 2, "name": "Pseudonym"},
        {"id": 3, "name": "Range"},
        {"id": 4, "name": "Noise"},
        {"id": 5, "name": "Mask"},
        {"id": 6, "name": "Month-year"},
    ]

    conn.execute(sa.text("INSERT INTO question_anonymity VALUES (:id, :name)"), values)


def downgrade():
    bind = op.get_bind()
    conn = bind.connect()

    conn.execute(sa.text("DELETE FROM question_anonymity"))
