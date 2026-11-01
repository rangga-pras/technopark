from datetime import date, datetime, time, timezone
from sqlalchemy import (BigInteger, Boolean, Column, Computed, Date, DateTime, Enum,
                        ForeignKey, Integer, String, Table, Text, Time, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

room_facilities = Table('room_facilities', Base.metadata,
    Column('room_id', ForeignKey('rooms.id', ondelete='CASCADE'), primary_key=True),
    Column('facility_id', ForeignKey('facilities.id', ondelete='CASCADE'), primary_key=True))

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(Enum('user', 'admin'), default='user', server_default='user')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='1')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class Room(Base):
    __tablename__ = 'rooms'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    capacity: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    thumbnail: Mapped[str] = mapped_column(String(255))
    visual_variant: Mapped[int] = mapped_column(default=0, server_default='0')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='1')
    facilities: Mapped[list['Facility']] = relationship(secondary=room_facilities, lazy='selectin')

class Facility(Base):
    __tablename__ = 'facilities'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)

class TimeSlot(Base):
    __tablename__ = 'time_slots'
    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

class Holiday(Base):
    __tablename__ = 'holidays'
    holiday_date: Mapped[date] = mapped_column(Date, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))

class Booking(Base):
    __tablename__ = 'bookings'
    __table_args__ = (
        UniqueConstraint('user_id', 'active_date_key', name='uq_booking_user_active_date'),
        UniqueConstraint('room_id', 'usage_date', 'active_slot_key', name='uq_booking_room_date_slot'),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'))
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id', ondelete='RESTRICT'))
    time_slot_id: Mapped[int] = mapped_column(ForeignKey('time_slots.id', ondelete='RESTRICT'))
    usage_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Enum('upcoming', 'completed', 'cancelled'), default='upcoming', server_default='upcoming')
    active_date_key: Mapped[date | None] = mapped_column(Date, Computed("CASE WHEN status = 'cancelled' THEN NULL ELSE usage_date END", persisted=True))
    active_slot_key: Mapped[int | None] = mapped_column(Integer, Computed("CASE WHEN status = 'cancelled' THEN NULL ELSE time_slot_id END", persisted=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime)
    room: Mapped[Room] = relationship(lazy='joined')
    time_slot: Mapped[TimeSlot] = relationship(lazy='joined')
    user: Mapped[User] = relationship(lazy='joined')
