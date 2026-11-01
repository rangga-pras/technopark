import json
import os
import ssl
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL, make_url

load_dotenv(Path(__file__).with_name('.env'))

APP_ENV = os.getenv('APP_ENV', 'development')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')
if len(JWT_SECRET_KEY) < 32 or JWT_SECRET_KEY.startswith('replace-'):
    raise RuntimeError('Isi JWT_SECRET_KEY acak minimal 32 karakter di backend/.env.')
TOKEN_MINUTES = int(os.getenv('TOKEN_MINUTES', '30'))
CORS_ORIGINS = [x.strip().rstrip('/') for x in os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',') if x.strip()]
if not CORS_ORIGINS or any(x == '*' for x in CORS_ORIGINS):
    raise RuntimeError('CORS_ORIGINS harus berisi origin frontend yang tepat.')
if APP_ENV == 'production' and any(not x.startswith('https://') for x in CORS_ORIGINS):
    raise RuntimeError('Origin produksi wajib HTTPS.')

def database_url():
    raw = os.getenv('DATABASE_URL')
    if raw:
        url = make_url(raw)
        url = url.set(drivername='mysql+pymysql') if url.drivername == 'mysql' else url
    else:
        required = ['MYSQLHOST', 'MYSQLUSER', 'MYSQLPASSWORD', 'MYSQLDATABASE']
        if not all(os.getenv(k) for k in required):
            raise RuntimeError('Konfigurasi DATABASE_URL atau seluruh field MYSQL belum lengkap.')
        url = URL.create('mysql+pymysql', username=os.environ['MYSQLUSER'], password=os.environ['MYSQLPASSWORD'],
                         host=os.environ['MYSQLHOST'], port=int(os.getenv('MYSQLPORT', '3306')),
                         database=os.environ['MYSQLDATABASE'], query={'charset': 'utf8mb4'})
    if url.drivername != 'mysql+pymysql':
        raise RuntimeError('TechnoPark membutuhkan MySQL melalui PyMySQL.')
    return url

def database_connect_args():
    args = {'connect_timeout': 5}
    ssl_required = os.getenv('MYSQL_SSL_REQUIRED', '').strip().lower() in {'1', 'true', 'yes', 'on'}
    ssl_ca = os.getenv('MYSQL_SSL_CA', '').strip()
    ssl_ca_pem = os.getenv('MYSQL_SSL_CA_PEM', '').strip()
    if ssl_ca and ssl_ca_pem:
        raise RuntimeError('Pilih MYSQL_SSL_CA atau MYSQL_SSL_CA_PEM, jangan keduanya.')
    if ssl_required and not (ssl_ca or ssl_ca_pem):
        raise RuntimeError('CA database wajib diisi ketika MYSQL_SSL_REQUIRED aktif.')
    if ssl_ca:
        ca_path = Path(ssl_ca)
        if not ca_path.is_file():
            raise RuntimeError(f'CA database tidak ditemukan: {ca_path}')
        args.update(ssl_ca=str(ca_path), ssl_verify_cert=True, ssl_verify_identity=True)
    elif ssl_ca_pem:
        ssl_context = ssl.create_default_context()
        try:
            ssl_context.load_verify_locations(cadata=ssl_ca_pem)
        except ssl.SSLError as exc:
            raise RuntimeError('MYSQL_SSL_CA_PEM bukan certificate PEM yang valid.') from exc
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        args['ssl'] = ssl_context
    return args

# Isi sesudah operator mengaudit SELURUH hari libur nasional tahun tersebut.
# Format {"2026":"https://sumber-resmi..."}; tidak ada tahun yang diasumsikan valid.
HOLIDAY_CALENDARS = json.loads(os.getenv('HOLIDAY_CALENDARS', '{}'))
if not isinstance(HOLIDAY_CALENDARS, dict):
    raise RuntimeError('HOLIDAY_CALENDARS harus berupa object JSON tahun:URL sumber.')
