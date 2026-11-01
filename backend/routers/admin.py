from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Booking, Facility, Holiday, Room, User, room_facilities
from schemas import (AdminBookingIn, AdminBookingOut, BookingIn, FacilityIn, FacilityOut,
                     HolidayIn, HolidayOut, Message, RoomIn, RoomOut, SummaryOut, UserCreate, UserOut, UserPatch)
from security import hash_password, require_admin
from booking_rules import (cancel_booking, complete_due, ensure_editable, operational_conflicts,
                           output_booking, save_booking)
from seed import CANONICAL_ROOMS

router = APIRouter(prefix='/api/admin', tags=['Admin'], dependencies=[Depends(require_admin)])

def record(db, model, key, lock=False):
    stmt = select(model).where(list(model.__table__.primary_key)[0] == key)
    item = db.scalar(stmt.with_for_update() if lock else stmt)
    if item is None:
        raise HTTPException(404, 'Data tidak ditemukan.')
    return item

def commit(db):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Data duplikat atau masih digunakan. Periksa kembali input Anda.')

@router.get('/summary', response_model=SummaryOut, summary='Ringkasan operasional')
def summary(db: Session = Depends(get_db)):
    complete_due(db)
    upcoming = db.scalars(select(Booking).where(Booking.status == 'upcoming')).unique().all()
    return SummaryOut(active_rooms=db.scalar(select(func.count()).select_from(Room).where(Room.is_active.is_(True))),
        active_users=db.scalar(select(func.count()).select_from(User).where(User.is_active.is_(True))),
        upcoming=len(upcoming), cancelled=db.scalar(select(func.count()).select_from(Booking).where(Booking.status == 'cancelled')),
        operational_conflicts=sum(bool(operational_conflicts(db, b)) for b in upcoming))

@router.get('/rooms', response_model=list[RoomOut], summary='Daftar semua ruangan dan arsip')
def rooms(db: Session = Depends(get_db)):
    return db.scalars(select(Room).order_by(Room.id)).all()

def room_values(db, data, room=None):
    values = data.model_dump(exclude={'facility_ids'})
    if room and room.name in dict(CANONICAL_ROOMS) and (data.name != room.name or data.capacity != room.capacity):
        raise HTTPException(422, 'Nama dan kapasitas sembilan ruangan bawaan harus dipertahankan.')
    facilities = db.scalars(select(Facility).where(Facility.id.in_(data.facility_ids))).all()
    if len(facilities) != len(set(data.facility_ids)):
        raise HTTPException(422, 'Salah satu fasilitas tidak ditemukan.')
    room = room or Room()
    for k, v in values.items():
        setattr(room, k, v)
    room.facilities = list(facilities)
    db.add(room)
    commit(db)
    db.refresh(room)
    return room

@router.post('/rooms', response_model=RoomOut, status_code=201, summary='Tambah ruangan')
def add_room(data: RoomIn, db: Session = Depends(get_db)):
    return room_values(db, data)

@router.get('/rooms/{key}', response_model=RoomOut, summary='Lihat ruangan termasuk arsip')
def get_room(key: int, db: Session = Depends(get_db)):
    return record(db, Room, key)

@router.patch('/rooms/{key}', response_model=RoomOut, summary='Edit informasi dan fasilitas ruangan')
def edit_room(key: int, data: RoomIn, db: Session = Depends(get_db)):
    return room_values(db, data, record(db, Room, key, True))

@router.delete('/rooms/{key}', response_model=Message, summary='Arsipkan ruangan')
def archive_room(key: int, db: Session = Depends(get_db)):
    room = record(db, Room, key, True)
    room.is_active = False
    commit(db)
    return Message(message='Ruangan diarsipkan. Riwayat booking tetap disimpan.')

@router.get('/facilities', response_model=list[FacilityOut], summary='Daftar fasilitas')
def facilities(db: Session = Depends(get_db)):
    return db.scalars(select(Facility).order_by(Facility.id)).all()

@router.post('/facilities', response_model=FacilityOut, status_code=201, summary='Tambah fasilitas')
def add_facility(data: FacilityIn, db: Session = Depends(get_db)):
    item = Facility(**data.model_dump())
    db.add(item)
    commit(db)
    return item

@router.get('/facilities/{key}', response_model=FacilityOut, summary='Lihat fasilitas')
def get_facility(key: int, db: Session = Depends(get_db)):
    return record(db, Facility, key)

@router.patch('/facilities/{key}', response_model=FacilityOut, summary='Edit fasilitas')
def edit_facility(key: int, data: FacilityIn, db: Session = Depends(get_db)):
    item = record(db, Facility, key)
    item.name = data.name
    commit(db)
    return item

@router.delete('/facilities/{key}', response_model=Message, summary='Hapus fasilitas yang tidak terpakai')
def delete_facility(key: int, db: Session = Depends(get_db)):
    item = record(db, Facility, key, True)
    if db.scalar(select(func.count()).select_from(room_facilities).where(room_facilities.c.facility_id == key)):
        raise HTTPException(409, 'Lepaskan fasilitas dari ruangan terlebih dahulu.')
    db.delete(item)
    commit(db)
    return Message(message='Fasilitas dihapus.')

@router.get('/holidays', response_model=list[HolidayOut], summary='Daftar hari libur')
def holidays(db: Session = Depends(get_db)):
    return db.scalars(select(Holiday).order_by(Holiday.holiday_date)).all()

@router.post('/holidays', response_model=HolidayOut, status_code=201, summary='Tambah hari libur dari sumber resmi')
def add_holiday(data: HolidayIn, db: Session = Depends(get_db)):
    item = Holiday(**data.model_dump())
    db.add(item)
    commit(db)
    return item

@router.get('/holidays/{key}', response_model=HolidayOut, summary='Lihat hari libur')
def get_holiday(key: date, db: Session = Depends(get_db)):
    return record(db, Holiday, key)

@router.patch('/holidays/{key}', response_model=HolidayOut, summary='Edit hari libur')
def edit_holiday(key: date, data: HolidayIn, db: Session = Depends(get_db)):
    item = record(db, Holiday, key, True)
    item.holiday_date, item.name = data.holiday_date, data.name
    commit(db)
    return item

@router.delete('/holidays/{key}', response_model=Message, summary='Hapus hari libur')
def delete_holiday(key: date, db: Session = Depends(get_db)):
    db.delete(record(db, Holiday, key, True))
    commit(db)
    return Message(message='Hari libur dihapus. Audit ulang cakupan kalender tahun terkait.')

@router.get('/users', response_model=list[UserOut], summary='Daftar akun')
def users(db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.id)).all()

@router.post('/users', response_model=UserOut, status_code=201, summary='Buat akun pengguna atau admin')
def add_user(data: UserCreate, db: Session = Depends(get_db)):
    item = User(**data.model_dump(exclude={'password', 'confirm_password'}), password_hash=hash_password(data.password))
    db.add(item)
    commit(db)
    return item

@router.get('/users/{key}', response_model=UserOut, summary='Lihat akun tanpa hash')
def get_user(key: int, db: Session = Depends(get_db)):
    return record(db, User, key)

def update_user(db, key, values):
    # Semua perubahan admin mengambil kunci dengan urutan yang sama.
    admins = db.scalars(select(User).where(User.role == 'admin', User.is_active.is_(True)).order_by(User.id).with_for_update()).all()
    item = record(db, User, key, True)
    if item.role == 'admin' and item.is_active and (values.get('role', item.role) != 'admin' or not values.get('is_active', item.is_active)) and len(admins) <= 1:
        raise HTTPException(409, 'Admin aktif terakhir tidak dapat dinonaktifkan atau diturunkan rolenya.')
    for k, v in values.items():
        if k == 'password':
            item.password_hash = hash_password(v)
        else:
            setattr(item, k, str(v).lower() if k == 'email' else v)
    commit(db)
    return item

@router.patch('/users/{key}', response_model=UserOut, summary='Edit akun, role, status, atau kata sandi')
def edit_user(key: int, data: UserPatch, db: Session = Depends(get_db)):
    values = data.model_dump(exclude_unset=True)
    if any(v is None for v in values.values()):
        raise HTTPException(422, 'Kolom yang diubah tidak boleh kosong.')
    return update_user(db, key, values)

@router.delete('/users/{key}', response_model=Message, summary='Nonaktifkan akun dan pertahankan riwayat')
def disable_user(key: int, db: Session = Depends(get_db)):
    update_user(db, key, {'is_active': False})
    return Message(message='Akun dinonaktifkan. Riwayat tetap disimpan.')

@router.get('/bookings', response_model=list[AdminBookingOut], summary='Daftar booking semua pengguna')
def bookings(db: Session = Depends(get_db)):
    complete_due(db)
    return [output_booking(db, b, True) for b in db.scalars(select(Booking).order_by(Booking.usage_date.desc(), Booking.id.desc())).unique()]

@router.get('/bookings/{key}', response_model=AdminBookingOut, summary='Lihat satu booking')
def get_booking(key: int, db: Session = Depends(get_db)):
    return output_booking(db, record(db, Booking, key), True)

@router.post('/bookings', response_model=AdminBookingOut, status_code=201, summary='Booking atas nama pengguna dengan aturan yang sama')
def add_booking(data: AdminBookingIn, db: Session = Depends(get_db)):
    return output_booking(db, save_booking(db, data, data.user_id), True)

@router.patch('/bookings/{key}', response_model=AdminBookingOut, summary='Edit jadwal booking mendatang')
def edit_booking(key: int, data: BookingIn, db: Session = Depends(get_db)):
    item = record(db, Booking, key, True)
    ensure_editable(item)
    return output_booking(db, save_booking(db, data, item.user_id, item), True)

@router.delete('/bookings/{key}', response_model=AdminBookingOut, summary='Batalkan booking mendatang')
def cancel(key: int, db: Session = Depends(get_db)):
    return output_booking(db, cancel_booking(db, record(db, Booking, key, True)), True)
