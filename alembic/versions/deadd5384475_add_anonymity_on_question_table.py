"""add anonymity on question table

Revision ID: deadd5384475
Revises: f9e025940eeb
Create Date: 2026-05-26 15:36:18.292971

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "deadd5384475"
down_revision = "f9e025940eeb"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "question", sa.Column("question_anonymity", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        op.f("fk_question_question_anonymity_question_anonymity"),
        "question",
        "question_anonymity",
        ["question_anonymity"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        op.f("fk_question_question_anonymity_question_anonymity"),
        "question",
        type_="foreignkey",
    )
    op.drop_column("question", "question_anonymity")
