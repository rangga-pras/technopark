from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from threading import Barrier
from zoneinfo import ZoneInfo
import pytest
from pydantic import ValidationError
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from fastapi.testclient import TestClient
from database import SessionLocal
from main import app
from models import Booking, Holiday, User
from schemas import BookingIn, RegisterIn
from security import hash_password, verify_password

def payload(room_ids, day='2030-01-08', slot=1, room=0):
    return {'room_id': room_ids[room], 'usage_date': day, 'time_slot_id': slot}

def test_schema_requires_fields_and_rejects_extra():
    with pytest.raises(ValidationError):
        BookingIn(room_id=1)
    with pytest.raises(ValidationError):
        BookingIn(room_id=1, usage_date='2030-01-08', time_slot_id=6)
    with pytest.raises(ValidationError):
        BookingIn(room_id=1, usage_date='2030-01-08', time_slot_id=1, user_id=42)

def test_bcrypt_and_multibyte_limit():
    hashed = hash_password('Sandi#123')
    assert hashed != 'Sandi#123' and verify_password('Sandi#123', hashed)
    assert not verify_password('Salah#123', hashed)
    with pytest.raises(ValidationError):
        RegisterIn(name='Budi', email='budi@example.com', password='😊' * 20, confirm_password='😊' * 20)

def test_seed_catalog_filters_and_no_sql_injection(client):
    rooms = client.get('/api/rooms').json()
    assert len(rooms) == 9
    assert len(client.get('/api/rooms?capacity=4').json()) == 3
    assert client.get('/api/rooms', params={'q': "' OR '1'='1"}).json() == []
    assert len(client.get('/api/time-slots').json()) == 5

def test_register_login_private_output(client):
    data = {'name': 'Ayu', 'email': 'AYU@example.com', 'password': 'Sandi#123', 'confirm_password': 'Sandi#123'}
    response = client.post('/api/auth/register', json=data)
    assert response.status_code == 201
    assert response.json()['email'] == 'ayu@example.com'
    assert 'password' not in response.text
    assert client.post('/api/auth/register', json=data).status_code == 409
    login = client.post('/api/auth/login', json={'email': 'ayu@example.com', 'password': 'Sandi#123'})
    assert login.status_code == 200
    headers = {'Authorization': f'Bearer {login.json()["access_token"]}'}
    assert client.get('/api/auth/me', headers=headers).status_code == 200
    assert client.get('/api/bookings/me', headers=headers).json() == []
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == 'ayu@example.com'))
        assert user.password_hash.startswith('$2b$')

def test_wrong_password_inactive_and_forged_token(client, accounts):
    assert client.post('/api/auth/login', json={'email': 'budi@example.com', 'password': 'wrong'}).status_code == 401
    with SessionLocal() as db:
        db.get(User, accounts[0]['id']).is_active = False
        db.commit()
    assert client.get('/api/auth/me', headers=accounts[0]['headers']).status_code == 401
    assert client.post('/api/auth/login', json={'email': 'budi@example.com', 'password': 'Valid#Pass123'}).status_code == 401
    assert client.get('/api/auth/me', headers={'Authorization': 'Bearer forged'}).status_code == 401

def test_login_rate_limit(client):
    responses = [client.post('/api/auth/login', json={'email': 'unknown@example.com', 'password': 'wrong'}) for _ in range(11)]
    assert responses[-1].status_code == 429

def test_one_user_same_date_and_different_dates(client, accounts, room_ids):
    h = accounts[0]['headers']
    assert client.post('/api/bookings', json=payload(room_ids), headers=h).status_code == 201
    assert client.post('/api/bookings', json=payload(room_ids, slot=2, room=1), headers=h).status_code == 409
    assert client.post('/api/bookings', json=payload(room_ids, day='2030-01-09'), headers=h).status_code == 201

def test_cross_user_collision_and_cancel_frees_constraints(client, accounts, room_ids):
    first = client.post('/api/bookings', json=payload(room_ids), headers=accounts[0]['headers']).json()
    assert client.post('/api/bookings', json=payload(room_ids), headers=accounts[1]['headers']).status_code == 409
    cancelled = client.delete(f'/api/bookings/{first["id"]}', headers=accounts[0]['headers'])
    assert cancelled.status_code == 200 and cancelled.json()['status'] == 'cancelled'
    assert client.post('/api/bookings', json=payload(room_ids), headers=accounts[1]['headers']).status_code == 201
    assert client.post('/api/bookings', json=payload(room_ids, slot=2), headers=accounts[0]['headers']).status_code == 201
    assert len(client.get('/api/bookings/me', headers=accounts[0]['headers']).json()) == 2

@pytest.mark.parametrize('day', ['2030-01-06', '2030-01-13', '2031-01-08'])
def test_past_sunday_and_unverified_year(client, accounts, room_ids, day):
    assert client.post('/api/bookings', json=payload(room_ids, day=day), headers=accounts[0]['headers']).status_code == 422

def test_holiday_and_started_slot(client, accounts, room_ids, monkeypatch):
    with SessionLocal() as db:
        db.add(Holiday(holiday_date=date(2030, 1, 8), name='Libur khusus fixture'))
        db.commit()
    assert client.post('/api/bookings', json=payload(room_ids), headers=accounts[0]['headers']).status_code == 422
    import booking_rules
    monkeypatch.setattr(booking_rules, 'now_wib', lambda: datetime(2030, 1, 7, 11, 0, tzinfo=ZoneInfo('Asia/Jakarta')))
    assert client.post('/api/bookings', json=payload(room_ids, day='2030-01-07', slot=2), headers=accounts[0]['headers']).status_code == 422

def test_idor_wrong_role_guest_and_cookie_not_auth(client, accounts, room_ids):
    b = client.post('/api/bookings', json=payload(room_ids), headers=accounts[0]['headers']).json()
    for method in ['get', 'delete']:
        assert getattr(client, method)(f'/api/bookings/{b["id"]}', headers=accounts[1]['headers']).status_code == 404
    assert client.patch(f'/api/bookings/{b["id"]}', json=payload(room_ids, slot=2), headers=accounts[1]['headers']).status_code == 404
    assert client.get('/api/admin/users', headers=accounts[0]['headers']).status_code == 403
    assert client.post('/api/bookings', json=payload(room_ids)).status_code == 401
    assert client.get('/api/auth/me', cookies={'access_token': 'test'}).status_code == 401

def test_conflicting_edit_rolls_back(client, accounts, room_ids):
    h = accounts[0]['headers']
    first = client.post('/api/bookings', json=payload(room_ids), headers=h).json()
    client.post('/api/bookings', json=payload(room_ids, day='2030-01-09'), headers=h)
    response = client.patch(f'/api/bookings/{first["id"]}', json=payload(room_ids, day='2030-01-09', room=1), headers=h)
    assert response.status_code == 409
    assert client.get(f'/api/bookings/{first["id"]}', headers=h).json()['usage_date'] == '2030-01-08'

def test_admin_crud_and_canonical_protection(client, accounts, room_ids):
    h = accounts[2]['headers']
    r = client.get(f'/api/admin/rooms/{room_ids[0]}', headers=h).json()
    edit = {k: r[k] for k in ['name', 'capacity', 'description', 'thumbnail', 'is_active']}
    edit['facility_ids'] = [f['id'] for f in r['facilities']]
    edit['name'] = 'Nama pengganti'
    assert client.patch(f'/api/admin/rooms/{r["id"]}', json=edit, headers=h).status_code == 422
    f = client.post('/api/admin/facilities', json={'name': 'Papan tulis tambahan'}, headers=h).json()
    assert client.patch(f'/api/admin/facilities/{f["id"]}', json={'name': 'Papan portable'}, headers=h).status_code == 200
    assert client.delete(f'/api/admin/facilities/{f["id"]}', headers=h).status_code == 200
    holiday = {'holiday_date': '2030-01-10', 'name': 'Hari libur fixture'}
    assert client.post('/api/admin/holidays', json=holiday, headers=h).status_code == 201
    holiday['name'] = 'Hari libur fixture diubah'
    assert client.patch('/api/admin/holidays/2030-01-10', json=holiday, headers=h).status_code == 200
    assert client.delete('/api/admin/holidays/2030-01-10', headers=h).status_code == 200
    assert client.delete(f'/api/admin/users/{accounts[2]["id"]}', headers=h).status_code == 409
    assert client.get('/api/admin/summary', headers=h).json()['active_rooms'] == 9

def test_operational_conflict_preserves_history(client, accounts, room_ids):
    h = accounts[2]['headers']
    booking = client.post('/api/admin/bookings', json={**payload(room_ids), 'user_id': accounts[0]['id']}, headers=h).json()
    assert client.delete(f'/api/admin/rooms/{room_ids[0]}', headers=h).status_code == 200
    result = client.get(f'/api/admin/bookings/{booking["id"]}', headers=h).json()
    assert result['status'] == 'upcoming' and result['operational_conflicts']

def test_simultaneous_api_requests_exactly_one_wins(accounts, room_ids):
    barrier = Barrier(2)
    def reserve(account):
        with TestClient(app) as client:
            barrier.wait(timeout=10)
            return client.post('/api/bookings', json=payload(room_ids), headers=account['headers']).status_code
    with ThreadPoolExecutor(2) as executor:
        results = list(executor.map(reserve, accounts[:2]))
    assert sorted(results) == [201, 409]

def test_mysql_generated_indexes_even_without_api(accounts, room_ids):
    with SessionLocal() as db:
        ddl = db.execute(text('SHOW CREATE TABLE bookings')).first()[1]
        generated = db.execute(text("SELECT COLUMN_NAME, EXTRA FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'bookings' AND COLUMN_NAME IN ('active_date_key', 'active_slot_key')")).all()
        assert len(generated) == 2 and all('STORED GENERATED' in extra for _, extra in generated)
        assert 'uq_booking_user_active_date' in ddl and 'uq_booking_room_date_slot' in ddl
        db.add(Booking(user_id=accounts[0]['id'], room_id=room_ids[0], usage_date=date(2030, 1, 8), time_slot_id=1, status='completed'))
        db.commit()
        db.add(Booking(user_id=accounts[0]['id'], room_id=room_ids[1], usage_date=date(2030, 1, 8), time_slot_id=2))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
        db.add(Booking(user_id=accounts[1]['id'], room_id=room_ids[0], usage_date=date(2030, 1, 8), time_slot_id=1))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
