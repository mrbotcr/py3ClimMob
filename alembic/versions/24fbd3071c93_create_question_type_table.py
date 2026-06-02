"""create question type table

Revision ID: 24fbd3071c93
Revises: deadd5384475
Create Date: 2026-05-27 09:16:25.379772

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "24fbd3071c93"
down_revision = "deadd5384475"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "question_type",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Unicode(length=64), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_question_type")),
    )


def downgrade():
    op.drop_table("question_type")
