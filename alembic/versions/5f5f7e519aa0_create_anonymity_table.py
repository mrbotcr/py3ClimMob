"""create anonymity table

Revision ID: 5f5f7e519aa0
Revises: a43877478276
Create Date: 2026-05-26 15:32:36.146875

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "5f5f7e519aa0"
down_revision = "a43877478276"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "question_anonymity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Unicode(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_question_anonymity")),
    )


def downgrade():
    op.drop_table("question_anonymity")
