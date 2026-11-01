"""API browser-test terisolasi. Hanya localhost:3308/technopark_test."""
import json
import os
import secrets
import sys
from pathlib import Path
from datetime import datetime
from dotenv import dotenv_values
from sqlalchemy.engine import make_url

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
raw = os.getenv('TEST_DATABASE_URL') or dotenv_values(root / '.env.test').get('TEST_DATABASE_URL')
url = make_url(raw or '')
if url.host not in {'127.0.0.1', 'localhost'} or url.port != 3308 or url.database != 'technopark_test' or url.drivername != 'mysql+pymysql':
    raise SystemExit('ABORT: hanya DB test lokal port 3308 yang diizinkan.')
os.environ.update(DATABASE_URL=raw, APP_ENV='test', JWT_SECRET_KEY=secrets.token_hex(32),
    CORS_ORIGINS='http://127.0.0.1:5174', HOLIDAY_CALENDARS=json.dumps({str(y): 'browser-test-fixture' for y in range(datetime.now().year, datetime.now().year + 3)}))
from alembic import command
from alembic.config import Config
from sqlalchemy import delete
from database import SessionLocal
from models import Booking, Facility, Holiday, Room, TimeSlot, User, room_facilities
from seed import seed
from security import hash_password

command.upgrade(Config(str(root / 'alembic.ini')), 'head')
credentials = {'email': 'pengelola-e2e@example.com', 'password': secrets.token_urlsafe(18)}
with SessionLocal() as db:
    for table in [Booking, room_facilities, Holiday, Room, Facility, TimeSlot, User]:
        db.execute(delete(table))
    db.commit()
    seed(db)
    db.add(User(name='Pengelola QA', email=credentials['email'], role='admin', password_hash=hash_password(credentials['password'])))
    db.commit()
(root / '.env.e2e.json').write_text(json.dumps(credentials))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='127.0.0.1', port=8001, proxy_headers=False)
