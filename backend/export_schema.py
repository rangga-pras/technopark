"""Ekspor DDL nyata dan data master publik; tidak pernah mengekspor akun/booking."""
import re
from pathlib import Path
from sqlalchemy import text, select
from database import engine, SessionLocal
from models import Room, Facility, TimeSlot, Holiday, room_facilities

def quote(value):
    return "'" + str(value).replace('\\', '\\\\').replace("'", "''") + "'"

def export():
    lines = ['-- TechnoPark / MySQL 8.4. Schema dan data master publik, tanpa akun atau booking.',
             '-- Untuk instalasi aplikasi gunakan Alembic + seed; jangan impor file ini lalu menjalankan migrasi awal.',
             'SET NAMES utf8mb4;']
    tables = ['users', 'rooms', 'time_slots', 'facilities', 'holidays', 'room_facilities', 'bookings']
    with engine.connect() as connection:
        for table in tables:
            ddl = connection.exec_driver_sql(f'SHOW CREATE TABLE `{table}`').first()[1]
            ddl = re.sub(r' AUTO_INCREMENT=\d+', '', ddl)
            lines.append(ddl + ';')
    with SessionLocal() as db:
        for model, columns in [(Room, ['id','name','capacity','description','thumbnail','visual_variant','is_active']),
                               (Facility, ['id','name']), (TimeSlot, ['id','start_time','end_time']),
                               (Holiday, ['holiday_date','name'])]:
            for item in db.scalars(select(model)):
                values = [str(int(getattr(item,c))) if isinstance(getattr(item,c),(int,bool)) else quote(getattr(item,c)) for c in columns]
                lines.append(f'INSERT INTO `{model.__tablename__}` ({", ".join(columns)}) VALUES ({", ".join(values)});')
        for room_id, facility_id in db.execute(select(room_facilities)):
            lines.append(f'INSERT INTO room_facilities (room_id, facility_id) VALUES ({room_id}, {facility_id});')
    destination = Path(__file__).resolve().parents[1] / 'database/technopark_schema.sql'
    destination.parent.mkdir(exist_ok=True)
    destination.write_text('\n\n'.join(lines) + '\n', encoding='utf-8')
    print('DDL dan data master publik diekspor. Tabel akun dan booking kosong.')

if __name__ == '__main__':
    export()
