"""Create tables MetadataForm

Revision ID: 77090b184211
Revises: 7af278cfa339
Create Date: 2024-11-18 11:11:10.044355

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "77090b184211"
down_revision = "7af278cfa339"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "metadata_form",
        sa.Column("metadata_id", sa.Unicode(length=64), nullable=False),
        sa.Column("metadata_name", sa.Unicode(length=200), nullable=False),
        sa.Column("metadata_odk", sa.BLOB(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column(
            "metadata_active",
            sa.Integer(),
            server_default=sa.text("'1'"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("metadata_id", name=op.f("pk_metadata_form")),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("metadata_form")
    # ### end Alembic commands ###
