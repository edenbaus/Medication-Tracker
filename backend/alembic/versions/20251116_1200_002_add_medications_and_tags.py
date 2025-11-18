"""add medications and tags

Revision ID: 002
Revises: 001
Create Date: 2025-11-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create medications table
    op.create_table(
        'medications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('drug_name', sa.String(), nullable=False),
        sa.Column('pharmacy', sa.String(), nullable=True),
        sa.Column('prescription_type', sa.Enum('long_term', 'short_term', 'otc', name='prescriptiontype'), nullable=False),
        sa.Column('dosing_schedule', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('standard_dose', sa.String(), nullable=False),
        sa.Column('date_prescribed', sa.Date(), nullable=True),
        sa.Column('date_filled', sa.Date(), nullable=True),
        sa.Column('prescribing_doctor', sa.String(), nullable=True),
        sa.Column('prescription_number', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medications_id'), 'medications', ['id'], unique=False)
    op.create_index(op.f('ix_medications_user_id'), 'medications', ['user_id'], unique=False)
    op.create_index(op.f('ix_medications_drug_name'), 'medications', ['drug_name'], unique=False)
    op.create_index(op.f('ix_medications_active'), 'medications', ['active'], unique=False)

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uix_user_tag_name')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)
    op.create_index(op.f('ix_tags_user_id'), 'tags', ['user_id'], unique=False)

    # Create medication_tags junction table
    op.create_table(
        'medication_tags',
        sa.Column('medication_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['medication_id'], ['medications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('medication_id', 'tag_id')
    )

    # Create medication_logs table
    op.create_table(
        'medication_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('medication_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('taken_at', sa.DateTime(), nullable=False),
        sa.Column('dose_taken', sa.String(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['medication_id'], ['medications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medication_logs_id'), 'medication_logs', ['id'], unique=False)
    op.create_index(op.f('ix_medication_logs_medication_id'), 'medication_logs', ['medication_id'], unique=False)
    op.create_index(op.f('ix_medication_logs_user_id'), 'medication_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_medication_logs_taken_at'), 'medication_logs', ['taken_at'], unique=False)

    # Create side_effects table
    op.create_table(
        'side_effects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('medication_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('severity', sa.Enum('mild', 'moderate', 'severe', name='severitylevel'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('occurred_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['medication_id'], ['medications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_side_effects_id'), 'side_effects', ['id'], unique=False)
    op.create_index(op.f('ix_side_effects_medication_id'), 'side_effects', ['medication_id'], unique=False)
    op.create_index(op.f('ix_side_effects_user_id'), 'side_effects', ['user_id'], unique=False)
    op.create_index(op.f('ix_side_effects_occurred_at'), 'side_effects', ['occurred_at'], unique=False)

    # Create symptom_tracking table
    op.create_table(
        'symptom_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('medication_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('symptom_name', sa.String(), nullable=False),
        sa.Column('improvement_level', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['medication_id'], ['medications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_symptom_tracking_id'), 'symptom_tracking', ['id'], unique=False)
    op.create_index(op.f('ix_symptom_tracking_medication_id'), 'symptom_tracking', ['medication_id'], unique=False)
    op.create_index(op.f('ix_symptom_tracking_user_id'), 'symptom_tracking', ['user_id'], unique=False)
    op.create_index(op.f('ix_symptom_tracking_recorded_at'), 'symptom_tracking', ['recorded_at'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_symptom_tracking_recorded_at'), table_name='symptom_tracking')
    op.drop_index(op.f('ix_symptom_tracking_user_id'), table_name='symptom_tracking')
    op.drop_index(op.f('ix_symptom_tracking_medication_id'), table_name='symptom_tracking')
    op.drop_index(op.f('ix_symptom_tracking_id'), table_name='symptom_tracking')
    op.drop_table('symptom_tracking')

    op.drop_index(op.f('ix_side_effects_occurred_at'), table_name='side_effects')
    op.drop_index(op.f('ix_side_effects_user_id'), table_name='side_effects')
    op.drop_index(op.f('ix_side_effects_medication_id'), table_name='side_effects')
    op.drop_index(op.f('ix_side_effects_id'), table_name='side_effects')
    op.drop_table('side_effects')
    op.execute('DROP TYPE IF EXISTS severitylevel')

    op.drop_index(op.f('ix_medication_logs_taken_at'), table_name='medication_logs')
    op.drop_index(op.f('ix_medication_logs_user_id'), table_name='medication_logs')
    op.drop_index(op.f('ix_medication_logs_medication_id'), table_name='medication_logs')
    op.drop_index(op.f('ix_medication_logs_id'), table_name='medication_logs')
    op.drop_table('medication_logs')

    op.drop_table('medication_tags')

    op.drop_index(op.f('ix_tags_user_id'), table_name='tags')
    op.drop_index(op.f('ix_tags_id'), table_name='tags')
    op.drop_table('tags')

    op.drop_index(op.f('ix_medications_active'), table_name='medications')
    op.drop_index(op.f('ix_medications_drug_name'), table_name='medications')
    op.drop_index(op.f('ix_medications_user_id'), table_name='medications')
    op.drop_index(op.f('ix_medications_id'), table_name='medications')
    op.drop_table('medications')
    op.execute('DROP TYPE IF EXISTS prescriptiontype')
