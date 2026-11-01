# TechnoPark

TechnoPark adalah aplikasi web full-stack untuk melihat ketersediaan dan memesan ruang belajar, diskusi, atau rapat. Aplikasi menyediakan sembilan ruang, lima slot berdurasi dua jam, autentikasi berbasis role, riwayat booking, dan halaman administrasi.

> **Catatan deployment:** aplikasi belum di-deploy karena proses deployment mengalami kendala konfigurasi pada layanan hosting. Tidak ada URL live yang diklaim; aplikasi disiapkan dan diuji melalui lingkungan lokal.

## Fitur Utama

- Katalog sembilan ruang beserta kapasitas, fasilitas, pencarian, dan filter.
- Pemeriksaan ketersediaan berdasarkan tanggal dan slot waktu.
- Registrasi, login, logout, profil, dan role `user`/`admin`.
- Pembuatan, perubahan, pembatalan, dan riwayat booking.
- Validasi satu booking aktif per pengguna per tanggal penggunaan.
- Pencegahan bentrok ruang, tanggal, dan slot pada tingkat API dan database.
- CRUD admin untuk ruang, fasilitas, hari libur, pengguna, dan booking.
- Antarmuka responsif untuk desktop, tablet, dan mobile.

## Teknologi

| Bagian | Teknologi |
| --- | --- |
| Frontend | Vue 3, Vite, JavaScript, Vue Router, Pinia, CSS native, Fetch API |
| Backend | FastAPI, Pydantic, SQLAlchemy ORM, Alembic, PyMySQL |
| Database | MySQL 8.4 melalui Docker Compose |
| Keamanan | JWT bearer, bcrypt, role guard, validasi server, CORS origin spesifik |
| Pengujian | pytest + HTTPX dan Playwright |

## Pemetaan MVC

TechnoPark memakai pola MVC yang disesuaikan untuk arsitektur SPA dan REST API.

| MVC | Lokasi | Tanggung jawab |
| --- | --- | --- |
| Model | `backend/models/`, `backend/database.py`, `backend/alembic/` | Entitas, relasi, transaksi, constraint, dan migrasi MySQL |
| View | `frontend/src/pages/`, `frontend/src/components/`, `frontend/src/assets/` | Halaman Vue, komponen UI, dan tampilan responsif |
| Controller | `backend/routers/`, `backend/booking_rules.py`, `backend/security.py` | Endpoint API, aturan bisnis, autentikasi, dan otorisasi |

Alur request: **Vue View -> Fetch API -> FastAPI Controller -> SQLAlchemy Model -> MySQL -> JSON response**.

## Akun Demo

Gunakan **email sebagai username**. Akun berikut khusus untuk evaluasi lokal dan dibuat melalui `backend/seed_demo.py`.

| Role | Email / Username | Kata sandi |
| --- | --- | --- |
| Admin | `admin@technopark.id` | `AdminTechno#2026` |
| User | `user@technopark.id` | `UserTechno#2026` |

Jangan gunakan kredensial demo ini pada production. Script akan menolak dijalankan ketika `APP_ENV=production`.

## Menjalankan di Lokal

### Prasyarat

- Windows 10/11
- Python 3.12
- Node.js 24 dan npm
- Docker Desktop dengan Docker Compose

### 1. Siapkan environment dan database

Buka Command Prompt atau PowerShell pada folder project:

```powershell
cd C:\Semester4\WAD05\UAS\TechnoPark
python scripts\setup_local.py
docker compose up -d --wait db
docker compose ps
```

Jalankan `setup_local.py` satu kali pada fresh clone. Script membuat empat file environment dengan secret acak; jika file `.env` sudah ada, lewati perintah tersebut. Jika perintah `python` tidak tersedia, gunakan `py -3.12`.

### 2. Siapkan dan jalankan backend

```powershell
cd C:\Semester4\WAD05\UAS\TechnoPark
python -m venv backend\.venv
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe seed.py
.\.venv\Scripts\python.exe seed_demo.py
.\.venv\Scripts\python.exe manage_calendar.py --year 2026 --activate-local
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Jika folder `backend\.venv` sudah tersedia, lewati perintah pembuatan virtual environment. Tidak perlu mengaktifkannya dengan `Activate.ps1` atau `activate.bat`; seluruh perintah memakai interpreter `.venv` secara langsung.

Backend tersedia di:

- API: `http://127.0.0.1:8000/api`
- Swagger: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/health`

### 3. Jalankan frontend

Buka terminal baru:

```powershell
cd C:\Semester4\WAD05\UAS\TechnoPark\frontend
npm ci
npm run dev
```

Buka `http://127.0.0.1:5173`, lalu login menggunakan salah satu akun demo.

### Menjalankan kembali di lain waktu

Gunakan tiga terminal:

```powershell
# Terminal 1 - dari root project
docker compose up -d --wait db

# Terminal 2 - dari folder backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Terminal 3 - dari folder frontend
npm run dev
```

Untuk menghentikan server, tekan `Ctrl+C` pada terminal backend dan frontend, lalu jalankan `docker compose down` dari root project. Jangan menambahkan opsi `-v` jika data MySQL ingin dipertahankan.

## Database

Database terdiri dari tujuh tabel utama: `users`, `rooms`, `facilities`, `room_facilities`, `time_slots`, `holidays`, dan `bookings`. Dua generated unique constraints mencegah booking ganda meskipun request datang bersamaan.

- Migrasi: `backend/alembic/`
- Schema SQL: `database/technopark_schema.sql`
- ERD: [`docs/erd.md`](docs/erd.md)

## Pengujian

Jalankan database test terpisah agar data development tidak tersentuh:

```powershell
cd C:\Semester4\WAD05\UAS\TechnoPark
docker compose --profile test up -d --wait db-test

cd backend
.\.venv\Scripts\python.exe -m pytest -q

cd ..\frontend
npm run test:e2e
npm run build
```

Verifikasi terakhir yang tercatat: **18 backend tests passed**, **6 end-to-end tests passed**, dan production build Vite berhasil. Detail tersedia di [`docs/verification.md`](docs/verification.md).

## Struktur Project

```text
TechnoPark/
|-- backend/              # FastAPI, model, controller, migration, dan tests
|-- frontend/             # Vue SPA, halaman, komponen, aset, dan E2E tests
|-- database/             # Export schema MySQL tanpa data privat
|-- docs/                 # ERD, arsitektur, dan catatan verifikasi
|-- scripts/              # Setup environment lokal
|-- compose.yaml          # MySQL development dan test
`-- README.md
```

Dokumentasi arsitektur lengkap dapat dilihat di [`docs/architecture.md`](docs/architecture.md).

## Catatan Keamanan

- Password disimpan sebagai hash bcrypt, bukan plaintext.
- JWT dikirim melalui header `Authorization` dan disimpan hanya di memori frontend; refresh halaman meminta login ulang.
- Backend memeriksa role admin, status akun, dan kepemilikan booking.
- SQLAlchemy memakai parameterized query; Vue tidak memakai `v-html` untuk input pengguna.
- API tidak memakai cookie autentikasi otomatis, sehingga risiko CSRF berbasis cookie tidak terpicu. Jika autentikasi diubah ke cookie, proteksi CSRF harus ditambahkan.
