"""Seluruh tes wajib menggunakan MySQL lokal khusus technopark_test."""
import os
import secrets
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import pytest
from dotenv import dotenv_values
from sqlalchemy.engine import make_url

test_url = os.getenv('TEST_DATABASE_URL') or dotenv_values(Path(__file__).parents[1] / '.env.test').get('TEST_DATABASE_URL')
if not test_url:
    raise RuntimeError('Siapkan backend/.env.test dan MySQL technopark_test sebelum menjalankan pytest.')
parsed = make_url(test_url)
if parsed.drivername != 'mysql+pymysql' or parsed.database != 'technopark_test' or parsed.host not in {'127.0.0.1', 'localhost'} or parsed.port != 3308:
    raise RuntimeError('ABORT: tes hanya boleh memakai MySQL localhost:3308/technopark_test.')
os.environ['DATABASE_URL'] = test_url
os.environ['APP_ENV'] = 'test'
os.environ['JWT_SECRET_KEY'] = secrets.token_hex(32)
os.environ['HOLIDAY_CALENDARS'] = '{}'

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import delete
from database import SessionLocal, engine
from main import app
from models import Booking, Facility, Holiday, Room, TimeSlot, User, room_facilities
from seed import seed
from security import hash_password, create_token, limiter
import booking_rules

@pytest.fixture(scope='session', autouse=True)
def migrated_database():
    # Vérifikasi koneksi nyata SEBELUM migrasi; tidak ada fallback SQLite.
    with engine.connect() as conn:
        assert conn.exec_driver_sql('SELECT DATABASE()').scalar() == 'technopark_test'
    command.upgrade(Config(str(Path(__file__).parents[1] / 'alembic.ini')), 'head')

@pytest.fixture(autouse=True)
def fresh_database(migrated_database, monkeypatch):
    with SessionLocal() as db:
        for table in [Booking, room_facilities, Holiday, Room, Facility, TimeSlot, User]:
            db.execute(delete(table))
        db.commit()
        seed(db)
    limiter.hits.clear()
    monkeypatch.setattr(booking_rules, 'HOLIDAY_CALENDARS', {'2030': 'test-fixture-only'})
    monkeypatch.setattr(booking_rules, 'now_wib', lambda: datetime(2030, 1, 7, 8, 0, tzinfo=ZoneInfo('Asia/Jakarta')))
    yield

@pytest.fixture
def client():
    with TestClient(app) as instance:
        yield instance

@pytest.fixture
def accounts():
    with SessionLocal() as db:
        users = [User(name=n, email=f'{n.lower()}@example.com', role=r, password_hash=hash_password('Valid#Pass123'))
                 for n, r in [('Budi', 'user'), ('Siti', 'user'), ('Pengelola', 'admin')]]
        db.add_all(users)
        db.commit()
        return [{'id': u.id, 'headers': {'Authorization': f'Bearer {create_token(u.id)}'}} for u in users]

@pytest.fixture
def room_ids():
    from sqlalchemy import select
    with SessionLocal() as db:
        return list(db.scalars(select(Room.id).order_by(Room.id)))
