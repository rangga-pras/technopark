from datetime import date as Date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from config import HOLIDAY_CALENDARS
from database import get_db
from models import Room, TimeSlot, Holiday, Booking
from schemas import RoomOut, SlotOut, HolidayOut, AvailabilityOut, AvailabilitySlot
from booking_rules import WIB, calendar_reason, now_wib

router = APIRouter(prefix='/api', tags=['Katalog'])

def get_room(db, room_id):
    room = db.get(Room, room_id)
    if not room or not room.is_active:
        raise HTTPException(404, 'Ruangan tidak ditemukan.')
    return room

@router.get('/rooms', response_model=list[RoomOut], summary='Jelajahi ruangan aktif')
def rooms(q: str = Query('', max_length=100), capacity: int | None = Query(None, ge=1, le=100), db: Session = Depends(get_db)):
    stmt = select(Room).where(Room.is_active.is_(True)).order_by(Room.id)
    if q.strip():
        stmt = stmt.where(Room.name.contains(q.strip(), autoescape=True))
    if capacity is not None:
        stmt = stmt.where(Room.capacity == capacity)
    return db.scalars(stmt).all()

@router.get('/rooms/{room_id}', response_model=RoomOut, summary='Lihat detail ruangan')
def room_detail(room_id: int, db: Session = Depends(get_db)):
    return get_room(db, room_id)

@router.get('/rooms/{room_id}/availability', response_model=AvailabilityOut, summary='Periksa lima slot pada tanggal penggunaan')
def availability(room_id: int, date: Date, db: Session = Depends(get_db)):
    get_room(db, room_id)
    reason = calendar_reason(db, date)
    occupied = set(db.scalars(select(Booking.time_slot_id).where(Booking.room_id == room_id, Booking.usage_date == date, Booking.status != 'cancelled')))
    slots = []
    for slot in db.scalars(select(TimeSlot).order_by(TimeSlot.id)):
        blocked = reason
        if not blocked and datetime.combine(date, slot.start_time, WIB) <= now_wib():
            blocked = 'Slot sudah dimulai.'
        if not blocked and slot.id in occupied:
            blocked = 'Sudah dipesan.'
        slots.append(AvailabilitySlot.model_validate({**SlotOut.model_validate(slot).model_dump(), 'available': not blocked, 'reason': blocked}))
    return AvailabilityOut(date=date, calendar_verified=str(date.year) in HOLIDAY_CALENDARS, slots=slots)

@router.get('/time-slots', response_model=list[SlotOut], summary='Lihat slot tetap WIB')
def time_slots(db: Session = Depends(get_db)):
    return db.scalars(select(TimeSlot).order_by(TimeSlot.id)).all()

@router.get('/holidays', response_model=list[HolidayOut], summary='Lihat hari libur terkonfigurasi')
def holidays(db: Session = Depends(get_db)):
    return db.scalars(select(Holiday).order_by(Holiday.holiday_date)).all()

@router.get('/calendar', summary='Lihat cakupan verifikasi kalender')
def calendar():
    return {'verified_years': sorted(int(y) for y in HOLIDAY_CALENDARS), 'sources': HOLIDAY_CALENDARS}
