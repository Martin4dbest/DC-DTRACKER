"""Make email nullable

Revision ID: abfbbc92b5f2
Revises: de41e92a2f9c
Create Date: 2024-12-07 03:38:51.548829

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abfbbc92b5f2'
down_revision = 'de41e92a2f9c'
branch_labels = None
depends_on = None


def upgrade():
    # Alter the email column to make it nullable
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('email', existing_type=sa.String(length=255), nullable=True)

def downgrade():
    # Revert the email column back to NOT NULL
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('email', existing_type=sa.String(length=255), nullable=False)
