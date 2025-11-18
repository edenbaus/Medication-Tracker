"""add regimens

Revision ID: add_regimens
Revises: add_third_parties
Create Date: 2025-11-16 21:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_regimens'
down_revision = 'add_third_parties'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create regimens table
    op.create_table(
        'regimens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.String(), nullable=True),
        sa.Column('updated_at', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_regimens_id'), 'regimens', ['id'], unique=False)
    op.create_index(op.f('ix_regimens_user_id'), 'regimens', ['user_id'], unique=False)

    # Create regimen_medications junction table
    op.create_table(
        'regimen_medications',
        sa.Column('regimen_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('medication_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['regimen_id'], ['regimens.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['medication_id'], ['medications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('regimen_id', 'medication_id')
    )


def downgrade() -> None:
    # Drop regimen_medications junction table
    op.drop_table('regimen_medications')

    # Drop regimens table
    op.drop_index(op.f('ix_regimens_user_id'), table_name='regimens')
    op.drop_index(op.f('ix_regimens_id'), table_name='regimens')
    op.drop_table('regimens')
