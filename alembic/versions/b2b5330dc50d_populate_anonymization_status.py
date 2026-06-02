"""populate anonymization status

Revision ID: b2b5330dc50d
Revises: f173e1661605
Create Date: 2026-05-28 09:15:54.120909

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "b2b5330dc50d"
down_revision = "f173e1661605"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    conn = bind.connect()

    values = [
        {"id": 1, "name": "Not started"},
        {"id": 2, "name": "In progress"},
        {"id": 3, "name": "Completed"},
        {"id": 4, "name": "Error"},
    ]

    conn.execute(
        sa.text("INSERT INTO anonymization_status VALUES (:id, :name)"),
        values,
    )


def downgrade():
    bind = op.get_bind()
    conn = bind.connect()

    conn.execute(sa.text("DELETE FROM anonymization_status"))
