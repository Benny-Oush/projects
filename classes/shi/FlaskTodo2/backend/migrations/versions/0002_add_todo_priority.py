"""add priority to todo

Revision ID: 0002_add_todo_priority
Revises: 0001_initial_todo
Create Date: 2026-07-30 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_add_todo_priority"
down_revision = "0001_initial_todo"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "todo",
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )


def downgrade():
    op.drop_column("todo", "priority")
