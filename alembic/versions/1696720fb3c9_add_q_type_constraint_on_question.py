"""add q-type constraint on question

Revision ID: 1696720fb3c9
Revises: b9d419da22c8
Create Date: 2026-05-27 09:20:18.411711

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "1696720fb3c9"
down_revision = "b9d419da22c8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        op.f("fk_question_question_dtype_question_type"),
        "question",
        "question_type",
        ["question_dtype"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        op.f("fk_question_question_dtype_question_type"), "question", type_="foreignkey"
    )
