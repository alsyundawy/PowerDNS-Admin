# 📝 Dokumentasi Changelog & Catatan Perubahan

Dokumen ini memuat catatan teknis perbaikan, peningkatan keamanan, serta fitur baru untuk rilis **PowerDNS-Admin** oleh **@alsyundawy**.

---

## 🚀 Version 0.4.3-alsyundawy (2026-08-11)

Rilis pemeliharaan utama, perbaikan bug, peningkatan keamanan, serta idempotensi migrasi database berbasis `0.4.2-alsyundawy-fix`.

### 🛡️ Perbaikan Keamanan (Security Fixes)

1. **Verifikasi SSL API PowerDNS (`lib/helper.py`)**
   - Menghapus nilai konstan `verify = False` dan menggantinya dengan nilai dinamis dari database `Setting().get('verify_ssl_connections')`.
2. **Proteksi Serangan Replay TOTP (`models/user.py` & Migrasi `d2e3f4a5b6c7`)**
   - Menambahkan pelacakan kolom `otp_last_used` agar token TOTP yang sama tidak dapat digunakan kembali dalam window waktu yang sama.
3. **Isolasi Identitas Autentikasi API (`decorators.py` / `routes/api.py`)**
   - Mengenalkan `api_current_user` (`LocalProxy`) yang menjamin kredensial Cookie Session tidak menimpa autentikasi HTTP Basic Auth pada endpoint API.
4. **Penanganan Sesi CSRF Kadaluarsa (`routes/index.py` & `base.py`)**
   - Menghapus sesi dan melakukan logout otomatis saat CSRF token kadaluarsa, menyajikan pemberitahuan ramah pengguna tanpa error HTTP 403 raw.
5. **Otorisasi Templat Zone (`routes/admin.py`)**
   - Menambahkan decorator `@operator_role_required` pada rute `/template/<template>/apply` untuk mencegah modifikasi templat tanpa hak akses.

### ⚡ Idempotensi Database & Migrasi (Database & Migrations)

1. **Alokasi Role Defensif (`models/role.py` & `models/user.py`)**
   - Menambahkan class method `Role.get_id_by_name(name)` yang otomatis mendaftarkan role default (`User`, `Administrator`, `Operator`) jika tabel `role` masih kosong. Mencegah error `AttributeError: 'NoneType' object has no attribute 'id'`.
2. **Migrasi Database Idempoten & Auto-Stamp (`migrations/env.py` & `versions/787bdba9e147_init_db.py`)**
   - Migrasi `787bdba9e147_init_db.py` memeriksa keberadaan tabel sebelum mengeksekusi `CREATE TABLE account`.
   - `migrations/env.py` secara otomatis men-stamp `alembic_version` ke revisi `head` (`d2e3f4a5b6c7`) jika tabel skema sudah terbuat pada database eksisting, mengeliminasi error `table ... already exists`.
3. **Kompatibilitas Flask-Session 0.6+ (`powerdnsadmin/__init__.py` & `models/sessions.py`)**
   - Menambahkan `__table_args__ = {'extend_existing': True}` pada model `Sessions` dan mengikat `SESSION_SQLALCHEMY = models.db` sebelum inisialisasi `Session(app)`.

### 🐛 Perbaikan Bug & Stabilitas UI (Bug Fixes & UI)

1. **Perbaikan Redirect Autentikasi (`routes/index.py`)**
   - Memperbaiki `authenticate_user()` agar mengarahkan pengguna ke `dashboard.dashboard` setelah login berhasil.
2. **Validasi Registrasi CAPTCHA (`routes/index.py`)**
   - Mengubah kondisi menjadi `if CAPTCHA_ENABLE and not captcha.validate():` agar pendaftaran berhasil saat fitur CAPTCHA dinonaktifkan.
3. **Context Processor Tampilan Versi (`powerdnsadmin/__init__.py` & `base.html`)**
   - Mendaftarkan `@app.context_processor` `inject_pdns_version` untuk mencegah `TypeError: Object of type Undefined is not JSON serializable` pada seluruh sub-menu dashboard.
4. **Identitas Footer Rilis (`base.html` & `1base.html`)**
   - Mengubah footer tampilan menjadi **Version 0.4.3 Modified By Alsyundawy**.

---

## 🎨 Version 0.4.2-alsyundawy-fix (2026-08-09)

Rilis perbaikan keamanan antarmuka (frontend) oleh **@alsyundawy**.

- **Commit:** `bcbb766`
- **Compare URL:** `0.4.2-alsyundawy...0.4.2-alsyundawy-fix`

### 🔒 Perbaikan Keamanan Antarmuka

1. **Templat Login (`6login.html`, `7login.html`, `8login.html`)**
   - Peningkatan fungsi `safeSrc` untuk pengolahan logo, pencegahan URL sumber yang tidak valid, dan validasi URL pada tema terang.
2. **Templat Registrasi (`register.html`)**
   - Penambahan atribut `nonce="{{ CSP_NONCE|default('') }}"` pada tag script dan validasi skema URL redirect untuk mencegah injeksi `javascript:` / `data:`.

---

## 🔒 Version 0.4.2-alsyundawy (2026-08-09)

Rilis perbaikan keamanan komprehensif, remediasi peringatan CodeQL, dan kompatibilitas RFC2317 oleh **@alsyundawy**.

- **Commit:** `789c185`
- **Compare URL:** `0.4.2...0.4.2-alsyundawy`

### 🛡️ Remediasi Keamanan & CodeQL

1. **Kepatuhan RFC2317**: Escaping nama zone pada URL API zones (#1).
2. **Endpoint OIDC Userinfo**: Perbaikan bug pada endpoint OIDC userinfo (#2).
3. **Injeksi Query LDAP**: Sanitasi query LDAP dari masukan pengguna (CodeQL Alert #17 / PR #9).
4. **Proteksi Full SSRF**: Hardening pencegahan Server-Side Request Forgery (CodeQL Alert #13 / PR #8).
5. **Hardening Reflected XSS & DOM**: Pencegahan Reflected XSS dan re-interpretasi elemen DOM sebagai HTML (CodeQL Alerts #1, #15, #18, #19, #20, #27, #29 / PRs #10, #11, #13, #14, #15, #16, #18).
6. **Mode Debug Flask**: Menonaktifkan mode debug Flask pada lingkungan produksi (CodeQL Alert #16 / PR #12).

### 📦 Pembaruan Dependensi

- `cryptography`: `45.0.5` → `46.0.5` → `48.0.1` → `50.0.0` (#19, #25, #28)
- `pyasn1`: `0.6.2` → `0.6.4` (#26)
- `setuptools`: `80.9.0` → `83.0.0` (#27)

---

## 📦 Version 0.4.2 (Upstream Official)

Rilis resmi dari **PowerDNS-Admin** (31 Januari 2022).

- Upgrade ke SQLAlchemy 1.4.x (format URL database `postgresql://`).
