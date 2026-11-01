"""Tujuh tabel inti TechnoPark dan dua constraint booking atomik MySQL."""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(254), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('user', 'admin'), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False), mysql_charset='utf8mb4')
    op.create_table('rooms',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('thumbnail', sa.String(255), nullable=False),
        sa.Column('visual_variant', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'), mysql_charset='utf8mb4')
    op.create_table('time_slots',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False))
    op.create_table('facilities',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(80), nullable=False, unique=True), mysql_charset='utf8mb4')
    op.create_table('holidays',
        sa.Column('holiday_date', sa.Date(), primary_key=True),
        sa.Column('name', sa.String(150), nullable=False), mysql_charset='utf8mb4')
    op.create_table('room_facilities',
        sa.Column('room_id', sa.Integer(), sa.ForeignKey('rooms.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('facility_id', sa.Integer(), sa.ForeignKey('facilities.id', ondelete='CASCADE'), primary_key=True))
    op.create_table('bookings',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('room_id', sa.Integer(), sa.ForeignKey('rooms.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('time_slot_id', sa.Integer(), sa.ForeignKey('time_slots.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('usage_date', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('upcoming', 'completed', 'cancelled'), nullable=False, server_default='upcoming'),
        sa.Column('active_date_key', sa.Date(), sa.Computed("CASE WHEN status = 'cancelled' THEN NULL ELSE usage_date END", persisted=True)),
        sa.Column('active_slot_key', sa.Integer(), sa.Computed("CASE WHEN status = 'cancelled' THEN NULL ELSE time_slot_id END", persisted=True)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('user_id', 'active_date_key', name='uq_booking_user_active_date'),
        sa.UniqueConstraint('room_id', 'usage_date', 'active_slot_key', name='uq_booking_room_date_slot'))

def downgrade():
    for table in ['bookings', 'room_facilities', 'holidays', 'facilities', 'time_slots', 'rooms', 'users']:
        op.drop_table(table)
