"""Import opt-in daftar libur nasional terverifikasi; tidak mengimpor cuti bersama."""
import argparse
import json
from datetime import date
from pathlib import Path
from database import SessionLocal
from models import Holiday
from config import APP_ENV
from dotenv import dotenv_values, set_key

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--year', required=True, choices=['2026', '2027'])
    parser.add_argument('--activate-local', action='store_true', help='Audit tanggal lalu aktifkan tahun di backend/.env development')
    args = parser.parse_args()
    item = json.loads(Path(__file__).with_name('data').joinpath('holidays.json').read_text(encoding='utf-8'))['years'][args.year]
    with SessionLocal() as db:
        for raw, name in item['holidays'].items():
            day = date.fromisoformat(raw)
            existing = db.get(Holiday, day)
            if not existing:
                db.add(Holiday(holiday_date=day, name=name))
        db.commit()
        for raw in item['holidays']:
            assert db.get(Holiday, date.fromisoformat(raw)) is not None
    if args.activate_local:
        if APP_ENV != 'development':
            raise SystemExit('Aktivasi file .env hanya untuk development. Tetapkan env deployment melalui dashboard.')
        env = Path(__file__).with_name('.env')
        calendars = json.loads(dotenv_values(env).get('HOLIDAY_CALENDARS') or '{}')
        calendars[args.year] = item['source']
        set_key(env, 'HOLIDAY_CALENDARS', json.dumps(calendars))
    print(f'Import {args.year} selesai; {len(item["holidays"])} tanggal nasional. Data yang sudah ada dipertahankan.')
    print('Tahun diaktifkan di .env lokal; restart API.' if args.activate_local else 'Audit daftar di halaman admin; kemudian tambahkan tahun dan URL sumber berikut ke HOLIDAY_CALENDARS:')
    print(item['source'])

if __name__ == '__main__':
    main()
