"""add third parties

Revision ID: add_third_parties
Revises: 720e7d29eb17
Create Date: 2025-11-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_third_parties'
down_revision = '720e7d29eb17'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create third_parties table
    op.create_table(
        'third_parties',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('relationship_type', sa.String(length=100), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.String(), nullable=True),
        sa.Column('updated_at', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_third_parties_user_id'), 'third_parties', ['user_id'], unique=False)

    # Add third_party_id column to medications table
    op.add_column('medications', sa.Column('third_party_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f('ix_medications_third_party_id'), 'medications', ['third_party_id'], unique=False)
    op.create_foreign_key('fk_medications_third_party_id', 'medications', 'third_parties', ['third_party_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    # Remove third_party_id from medications
    op.drop_constraint('fk_medications_third_party_id', 'medications', type_='foreignkey')
    op.drop_index(op.f('ix_medications_third_party_id'), table_name='medications')
    op.drop_column('medications', 'third_party_id')

    # Drop third_parties table
    op.drop_index(op.f('ix_third_parties_user_id'), table_name='third_parties')
    op.drop_table('third_parties')
