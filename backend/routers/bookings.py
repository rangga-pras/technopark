from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_db
from models import Booking, User
from schemas import BookingIn, BookingOut
from security import current_user
from booking_rules import cancel_booking, complete_due, ensure_editable, output_booking, save_booking

router = APIRouter(prefix='/api/bookings', tags=['Booking'])

def own_booking(db, booking_id, user):
    booking = db.scalar(select(Booking).where(Booking.id == booking_id).with_for_update())
    if not booking or booking.user_id != user.id:
        raise HTTPException(404, 'Booking tidak ditemukan.')
    return booking

@router.get('/me', response_model=list[BookingOut], summary='Lihat riwayat booking sendiri')
def my_bookings(user: User = Depends(current_user), db: Session = Depends(get_db)):
    complete_due(db)
    return [output_booking(db, b) for b in db.scalars(select(Booking).where(Booking.user_id == user.id).order_by(Booking.usage_date.desc(), Booking.id.desc())).unique()]

@router.get('/{booking_id}', response_model=BookingOut, summary='Lihat satu booking sendiri')
def detail(booking_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return output_booking(db, own_booking(db, booking_id, user))

@router.post('', response_model=BookingOut, status_code=201, summary='Konfirmasi booking gratis')
def create(data: BookingIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return output_booking(db, save_booking(db, data, user.id))

@router.patch('/{booking_id}', response_model=BookingOut, summary='Ubah jadwal booking mendatang')
def edit(booking_id: int, data: BookingIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    booking = own_booking(db, booking_id, user)
    ensure_editable(booking)
    return output_booking(db, save_booking(db, data, user.id, booking))

@router.delete('/{booking_id}', response_model=BookingOut, summary='Batalkan booking tanpa menghapus riwayat')
def cancel(booking_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return output_booking(db, cancel_booking(db, own_booking(db, booking_id, user)))
