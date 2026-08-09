"""Add otp_last_used column to user table

Revision ID: d2e3f4a5b6c7
Revises: b24bf17725d2
Create Date: 2023-03-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2e3f4a5b6c7'
down_revision = 'b24bf17725d2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user',
                  sa.Column('otp_last_used', sa.BigInteger(), nullable=True))


def downgrade():
    op.drop_column('user', 'otp_last_used')
