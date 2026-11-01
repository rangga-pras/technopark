from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from config import HOLIDAY_CALENDARS
from models import Booking, Holiday, Room, TimeSlot, User, utcnow
from schemas import BookingOut, AdminBookingOut

WIB = ZoneInfo('Asia/Jakarta')

def now_wib():
    return datetime.now(WIB)

def calendar_reason(db, day):
    now = now_wib()
    if day < now.date():
        return 'Tanggal penggunaan sudah lewat.'
    if day.weekday() == 6:
        return 'TechnoPark tutup pada hari Minggu.'
    if str(day.year) not in HOLIDAY_CALENDARS:
        return f'Kalender libur {day.year} belum diverifikasi. Hubungi pengelola.'
    holiday = db.get(Holiday, day)
    if holiday:
        return f'Tutup pada hari libur: {holiday.name}.'
    return None

def operational_conflicts(db, booking):
    reasons = []
    if not booking.room.is_active:
        reasons.append('Ruangan dinonaktifkan. Hubungi pengelola.')
    if not booking.user.is_active:
        reasons.append('Akun pemesan dinonaktifkan.')
    holiday = db.get(Holiday, booking.usage_date)
    if holiday:
        reasons.append(f'Hari libur: {holiday.name}. Hubungi pengelola.')
    if str(booking.usage_date.year) not in HOLIDAY_CALENDARS:
        reasons.append('Kalender tahun penggunaan belum diverifikasi.')
    return reasons

def output_booking(db, booking, admin=False):
    schema = AdminBookingOut if admin else BookingOut
    result = schema.model_validate(booking)
    if result.status == 'upcoming' and datetime.combine(booking.usage_date, booking.time_slot.end_time, WIB) <= now_wib():
        result.status = 'completed'
    if result.status == 'upcoming':
        result.operational_conflicts = operational_conflicts(db, booking)
    return result

def complete_due(db):
    now = now_wib()
    ended = list(db.scalars(select(TimeSlot.id).where(TimeSlot.end_time <= now.time().replace(tzinfo=None))))
    condition = (Booking.usage_date < now.date()) | ((Booking.usage_date == now.date()) & Booking.time_slot_id.in_(ended))
    db.execute(update(Booking).where(Booking.status == 'upcoming', condition).values(status='completed'))
    db.commit()

def ensure_editable(booking):
    if booking.status != 'upcoming' or datetime.combine(booking.usage_date, booking.time_slot.start_time, WIB) <= now_wib():
        raise HTTPException(409, 'Hanya booking mendatang yang belum dimulai dapat diubah atau dibatalkan.')

def save_booking(db, data, user_id, booking=None):
    # Kunci master selama transaksi. Unique indexes tetap penjaga terakhir
    # untuk semua penulis DB, termasuk request yang masuk bersamaan.
    user = db.scalar(select(User).where(User.id == user_id).with_for_update())
    room = db.scalar(select(Room).where(Room.id == data.room_id).with_for_update())
    slot = db.get(TimeSlot, data.time_slot_id)
    if not user or not user.is_active:
        raise HTTPException(422, 'Akun pemesan tidak aktif atau tidak ditemukan.')
    if not room or not room.is_active:
        raise HTTPException(422, 'Ruangan tidak tersedia untuk dipesan.')
    if not slot:
        raise HTTPException(422, 'Pilih salah satu dari lima slot yang tersedia.')
    reason = calendar_reason(db, data.usage_date)
    if reason:
        raise HTTPException(422, reason)
    if datetime.combine(data.usage_date, slot.start_time, WIB) <= now_wib():
        raise HTTPException(422, 'Slot ini sudah dimulai. Pilih waktu berikutnya.')
    if booking is None:
        booking = Booking(user_id=user_id, status='upcoming')
        db.add(booking)
    booking.room_id = data.room_id
    booking.usage_date = data.usage_date
    booking.time_slot_id = data.time_slot_id
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Slot baru saja dipesan atau akun sudah memiliki booking pada tanggal penggunaan ini. Pilih jadwal lain.')
    db.refresh(booking)
    return booking

def cancel_booking(db, booking):
    ensure_editable(booking)
    booking.status = 'cancelled'
    booking.cancelled_at = utcnow()
    db.commit()
    db.refresh(booking)
    return booking
