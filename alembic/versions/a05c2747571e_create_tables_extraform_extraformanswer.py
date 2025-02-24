"""Create tables ExtraForm - ExtraFormAnswer

Revision ID: a05c2747571e
Revises: 56897fe827da
Create Date: 2023-11-10 10:05:42.624684

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "a05c2747571e"
down_revision = "56897fe827da"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "extra_form",
        sa.Column("form_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("form_name", sa.Unicode(length=120), nullable=False),
        sa.Column("form_started", sa.DateTime(), nullable=False),
        sa.Column("form_finished", sa.DateTime(), nullable=True),
        sa.Column("form_status", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("form_id", name=op.f("pk_extra_form")),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_table(
        "extra_form_answers",
        sa.Column("form_id", sa.Integer(), nullable=False),
        sa.Column("user_name", sa.Unicode(length=80), nullable=False),
        sa.Column("answer_field", sa.Unicode(length=120), nullable=False),
        sa.Column("answer_date", sa.DateTime(), nullable=True),
        sa.Column("answer_data", sa.Unicode(length=120), nullable=False),
        sa.ForeignKeyConstraint(
            ["form_id"],
            ["extra_form.form_id"],
            name=op.f("fk_extra_form_answers_form_id_extra_form"),
        ),
        sa.ForeignKeyConstraint(
            ["user_name"],
            ["user.user_name"],
            name=op.f("fk_extra_form_answers_user_name_user"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "form_id", "user_name", "answer_field", name=op.f("pk_extra_form_answers")
        ),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
        mysql_collate="utf8mb4_unicode_ci",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("extra_form_answers")
    op.drop_table("extra_form")
    # ### end Alembic commands ###
