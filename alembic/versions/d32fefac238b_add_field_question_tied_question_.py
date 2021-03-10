"""add field question_tied - question_notobserved to question

Revision ID: d32fefac238b
Revises: 818e37fbf3e1
Create Date: 2021-03-09 08:34:14.607848

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd32fefac238b'
down_revision = '818e37fbf3e1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('question', sa.Column('question_notobserved', sa.Integer(), server_default=sa.text("'0'"), nullable=True))
    op.add_column('question', sa.Column('question_tied', sa.Integer(), server_default=sa.text("'0'"), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('question', 'question_tied')
    op.drop_column('question', 'question_notobserved')
    # ### end Alembic commands ###
