"""climmobShare - Products - table relationship

Revision ID: 314451ce468b
Revises: 379b6800b8a4
Create Date: 2021-08-10 11:06:44.527193

"""
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = "314451ce468b"
down_revision = "379b6800b8a4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "products", "project_id", existing_type=mysql.VARCHAR(length=64), nullable=False
    )
    op.create_foreign_key(
        op.f("fk_products_project_id_project"),
        "products",
        "project",
        ["project_id"],
        ["project_id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        op.f("fk_products_project_id_project"), "products", type_="foreignkey"
    )
    op.alter_column(
        "products", "project_id", existing_type=mysql.VARCHAR(length=64), nullable=True
    )
    # ### end Alembic commands ###
