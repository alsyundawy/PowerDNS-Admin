# Changelog Documentation

## Change Tracking

### Version 0.4.3-alsyundawy (2026-08-09)

Perubahan signifikan dari versi 0.4.2-alsyundawy-fix meliputi:

#### Kategori Perbaikan

##### Security Fixes (Perbaikan Keamanan)
1. **lib/helper.py:21** - Hardcoded SSL verification
   - Masalah: `verify = False` untuk semua komunikasi API PowerDNS
   - Solusi: Menggunakan setting `verify_ssl_connections` dari database
   - Dampak: Menghentikan keamanan SSL yang sempurna

2. **models/setting.py:48,70,93** - Traceback method tidak valid
   - Masalah: `traceback.format_exec()` tidak ada di modul traceback
   - Solusi: Menggunakan `traceback.format_exc()` yang benar
   - Dampak: Mengizinkan penulisan log exception yang benar

##### Bug Fixes (Perbaikan Bug)
1. **routes/domain.py:767,813** - SQL query filter operand salah
   - Masalah: `domain_name == Domain.name` (urutan tidak tepat)
   - Solusi: `Domain.name == domain_name`
   - Platform: Mendukung SQLite, PostgreSQL, MySQL

2. **routes/api.py:289** - Query tidak dijalankan
   - Masalah: `.filter()` tanpa `.first()` atau `.all()`
   - Solusi: Menambahkan `.first()` untuk mengeksekusi query
   - Dampak: Endpoint API delete zone tidak bekerja

3. **models/domain.py:601,613** - Logging tidak efektif
   - Masalah: `logger.debug(print(...))` karena print() mengembalikan None
   - Solusi: `logger.debug(traceback.format_exc())`
   - Dampak: Debugging menjadi tidak berguna

4. **routes/api.py:678,907** - Bug logika
   - Masalah: `[] or User.query.all()` selalu mengembalikan hasil query
   - Solusi: `User.query.all()` langsung
   - Dampak: Perilaku tidak terduga pada daftar pengguna/akun

5. **routes/index.py (`authenticate_user`)** - Login kembali ke halaman `/login`
   - Masalah: setelah autentikasi berhasil, fungsi mengembalikan redirect ke
     `index.login` sehingga pengguna tidak dapat masuk ke aplikasi
   - Solusi: redirect ke `dashboard.dashboard`

6. **models/role.py & models/user.py (`Role.get_id_by_name`)** - Error `NoneType` ID
   - Masalah: `Role.query.filter_by(...).first().id` melempar `AttributeError: 'NoneType' object has no attribute 'id'` saat tabel `role` kosong
   - Solusi: Menambahkan class method `Role.get_id_by_name(name)` yang otomatis membuat role (`User`, `Administrator`, `Operator`) jika belum ada di database

7. **routes/index.py (`register`)** - Validasi CAPTCHA gagal saat CAPTCHA dinonaktifkan
   - Masalah: `captcha.validate()` dipanggil langsung walau `CAPTCHA_ENABLE` dinonaktifkan
   - Solusi: `if CAPTCHA_ENABLE and not captcha.validate():`

8. **migrations/env.py & versions/787bdba9e147_init_db.py** - Idempotensi Migrasi & Auto-stamp
   - Masalah: `flask db upgrade` gagal dengan `table account already exists` pada database eksisting
   - Solusi: Pengecekan tabel pada `787bdba9e147_init_db.py` dan auto-stamping berbasis SQL di `migrations/env.py`

9. **powerdnsadmin/__init__.py & base.html** - Context Processor `pdns_version` & Sub-menu Error 500
   - Masalah: `{{ (pdns_version or '')|tojson }}` melempar `TypeError` pada sub-menu dashboard
   - Solusi: Mendaftarkan `@app.context_processor` `inject_pdns_version` di `__init__.py` dan mengikat versi footer ke `Version 0.4.3 Modified By Alsyundawy`

##### Code Quality Improvements (Perbaikan Kualitas Kode)
- Menghapus debug print statement dari kode produksi
- Memperbaiki typo di method `__repr__` Account model
- Menghapus duplikat method `__init__` di Setting model
- Mengkoreksi tipe data `pwd_min_special` dari `bool` kembali ke `int` (default `0`) agar template registrasi dapat mengikatnya sebagai angka (policy karakter khusus)
- Memperbaiki setting deprecated `SQLALCHEMY_TRACK_MODIFICATIONS`
- Mengganti bare `except:` dengan exception type spesifik
- Memperbaiki escape sequence untuk kompatibilitas Python 3.12+

### Version 0.4.2-alsyundawy-fix (2026-08-09)

**Release Author:** @alsyundawy

#### Security Fixes
1. Escaping zone name in zones API URL to fully support RFC2317
2. Potential fix for code scanning alert: LDAP query built from user-controlled sources
3. Potential fix for code scanning alert: Full server-side request forgery
4. Potential fix for code scanning alert: Flask app is run in debug mode
5. Potential fix for code scanning alert: Reflected server-side cross-site scripting

#### Bug Fixes
1. Fix: oidc userinfo endpoint

#### Dependency Updates
- cryptography: 45.0.5 → 46.0.5 → 48.0.1 → 50.0.0
- pyasn1: 0.6.2 → 0.6.4
- setuptools: 80.9.0 → 83.0.0

### Version 0.4.2-alsyundawy

Release by @alsyundawy with comprehensive security and functionality fixes.

**GitHub Release:** https://github.com/alsyundawy/PowerDNS-Admin/releases/tag/0.4.2-alsyundawy

### Version 0.4.2 (Inisial dari Upstream)

Rilis resmi PowerDNS-Admin versi 0.4.2 (31 Januari 2022)

**Pengumumen Penting:**
- **PERUBATAN BREAKING**: Upgrade ke SQLAlchemy 1.4.x
- Format koneksi database ubah dari `postgres://` ke `postgresql://`

**Fitur dan Perbaikan Utama:**
- OAuth auto-configuration yang lebih baik
- Konfigurasi environment variable untuk semua setting
- Perbaikan case-insensitive untuk username/email
- Dukungan untuk sub-path deployment
- LDAP search filter cleansing
- Numerous bug fixes dan cleanup

### Version 0.4.1 dan lebih lanjut

Lihat GitHub releases untuk riwayat lengkapnya.

---

**Author:** alsyundawy
**Date:** 2026-08-09
**Repository:** https://github.com/alsyundawy/PowerDNS-Admin