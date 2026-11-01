"""Buat konfigurasi development dengan rahasia acak, tanpa menimpa file yang ada."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
targets = [root / '.env', root / 'backend/.env', root / 'backend/.env.test', root / 'frontend/.env']
if any(p.exists() for p in targets):
    raise SystemExit('Ada file .env lokal. Konfigurasi dipertahankan; sesuaikan manual menggunakan .env.example.')
password, root_password, test_password, test_root = [secrets.token_hex(24) for _ in range(4)]
targets[0].write_text(f'MYSQL_DATABASE=technopark_db\nMYSQL_USER=technopark\nMYSQL_PASSWORD={password}\nMYSQL_ROOT_PASSWORD={root_password}\nMYSQL_PORT=3307\nMYSQL_TEST_PASSWORD={test_password}\nMYSQL_TEST_ROOT_PASSWORD={test_root}\n')
targets[1].write_text(f'APP_ENV=development\nMYSQLHOST=127.0.0.1\nMYSQLPORT=3307\nMYSQLUSER=technopark\nMYSQLPASSWORD={password}\nMYSQLDATABASE=technopark_db\nJWT_SECRET_KEY={secrets.token_hex(32)}\nTOKEN_MINUTES=30\nCORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173\nHOLIDAY_CALENDARS={{}}\n')
targets[2].write_text(f'TEST_DATABASE_URL=mysql+pymysql://technopark_test:{test_password}@127.0.0.1:3308/technopark_test?charset=utf8mb4\n')
targets[3].write_text('VITE_API_BASE_URL=http://127.0.0.1:8000/api\n')
print('Empat file environment lokal dibuat. Rahasia tidak ditampilkan. Lanjutkan migrasi, seed, dan konfigurasi kalender.')
