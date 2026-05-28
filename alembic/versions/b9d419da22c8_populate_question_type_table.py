"""populate question type table

Revision ID: b9d419da22c8
Revises: 24fbd3071c93
Create Date: 2026-05-27 09:19:27.758703

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "b9d419da22c8"
down_revision = "24fbd3071c93"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    conn = bind.connect()

    values = [
        {"id": 1, "name": "Text", "order": 1},
        {"id": 9, "name": "Ranking of options", "order": 2},
        {"id": 10, "name": "Comparison with check", "order": 3},
        {"id": 27, "name": "Location", "order": 4},
        {"id": 2, "name": "Decimal", "order": 5},
        {"id": 3, "name": "Integer", "order": 6},
        {"id": 4, "name": "GeoPoint", "order": 7},
        {"id": 5, "name": "Select one", "order": 8},
        {"id": 6, "name": "Select multiple", "order": 9},
        {"id": 11, "name": "GeoTrace", "order": 10},
        {"id": 12, "name": "GeoShape", "order": 11},
        {"id": 13, "name": "Date", "order": 12},
        {"id": 14, "name": "Time", "order": 13},
        {"id": 15, "name": "DateTime", "order": 14},
        {"id": 16, "name": "Image", "order": 15},
        {"id": 17, "name": "Audio", "order": 16},
        {"id": 18, "name": "Video", "order": 17},
        {"id": 19, "name": "Barcode/QR", "order": 18},
        {"id": 7, "name": "Package code", "order": -1},
        {"id": 8, "name": "Farmer", "order": -1},
    ]

    conn.execute(
        sa.text("INSERT INTO question_type VALUES (:id, :name, :order)"),
        values,
    )


def downgrade():
    bind = op.get_bind()
    conn = bind.connect()

    conn.execute(sa.text("DELETE FROM question_type"))
