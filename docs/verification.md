# Verifikasi lokal

Pengujian dilaksanakan pada 1–2 November 2026 di Windows, Node 24, Python 3.12, Microsoft Edge, dan MySQL 8.4.13 melalui Docker Desktop. Hasil berikut berasal dari perintah yang benar-benar dijalankan.

| Pemeriksaan | Hasil |
| --- | --- |
| `python -m alembic upgrade head` | Berhasil pada MySQL development dan test |
| `python seed.py`, diulang dua kali | Berhasil; sembilan ruang dan lima slot tetap |
| `python -m alembic check` | Tidak ada operasi upgrade baru |
| `python -m pytest -q` | 18 passed pada MySQL test; ada peringatan deprecation dependency, tanpa tes gagal |
| `npm run test:e2e` | 6 passed, browser Edge dan API test terisolasi |
| `npm run build` | Berhasil menghasilkan build produksi Vite |
| `python -m pip check` | Tidak ada dependency rusak |
| `pip-audit` | Tidak ada kerentanan yang dikenal pada paket terpasang setelah pembaruan |
| Audit npm saat instalasi | 0 vulnerabilities |
| Build Docker backend Linux | Berhasil; health HTTP 200 dan katalog sembilan ruangan |
| Restart MySQL development | Tetap sembilan ruangan dan 35 tanggal libur |
| CORS | Origin frontend tepat diterima; origin lain ditolak pada preflight |
| SPA deep link lokal | HTTP 200 dan refresh detail ruangan berhasil |
| Audit visual 375/390/768/1280/1440 px | 0 temuan gagal; 4 peringatan tentang variasi tipografi, inset kartu, footage, dan jumlah animasi |
| Pemeriksaan file kandidat repository | Tidak ada nilai secret lokal atau materi konteks privat |

Tes backend mencakup validasi Pydantic, hash bcrypt, registrasi/login, keluaran tanpa hash, rate-limit, akun nonaktif, token palsu, role, IDOR, tanggal lampau/Minggu/tahun belum diverifikasi, hari libur, slot sudah dimulai, konflik lintas pengguna, batas per tanggal, tanggal berbeda, pembatalan yang membebaskan constraint, rollback edit, arsip, dan dua request booking bersamaan. Metadata MySQL memastikan kedua kolom bersifat `STORED GENERATED`; penulisan langsung ke DB juga menguji kedua unique indexes, termasuk status `completed`.

Tes browser menelusuri pencarian/filter/empty/error/retry, pilihan guest yang dipertahankan setelah daftar, konfirmasi, perubahan jadwal, pembatalan, profil/logout, CRUD admin, validasi perubahan ruang bawaan, refresh sesi, dan overflow di 375/768/1280 px. Foto mempunyai alt dan font disajikan lokal.

## Pengukuran performa

Dua pengukuran Lighthouse pada build produksi lokal dengan emulasi mobile, setelah perbaikan layout awal:

| Metrik | Run pertama | Run kedua |
| --- | ---: | ---: |
| Performance | 97 | 94 |
| Accessibility | 100 | 100 |
| Best practices | 100 | 100 |
| Largest Contentful Paint | 2,6 detik | 3,2 detik |
| Cumulative Layout Shift | 0 | 0 |
| Total Blocking Time | 50 ms | 50 ms |

Angka ini merupakan hasil lab lokal, bukan pengukuran trafik produksi. LCP belum konsisten di bawah sasaran 2,5 detik; optimasi lanjutan dapat memprioritaskan rendition foto hero untuk perangkat kecil dan pengukuran ulang pada hosting aktual. Skor aksesibilitas otomatis tidak menggantikan seluruh pengujian pembaca layar.

## Batas verifikasi deployment

Konfigurasi Cloudflare Pages dan Railway sudah disiapkan, tetapi belum ada URL publik yang diuji. Hubungkan repository, akun penyedia, dan domain; buat admin pertama secara interaktif; lalu ulangi pengujian CORS, HTTPS, SPA fallback, login, transaksi booking, dan admin melalui URL aktual. Fitur pemulihan email dan pencabutan JWT individual tidak tersedia; perilaku sesi dan penggantian kata sandi dijelaskan di README.
