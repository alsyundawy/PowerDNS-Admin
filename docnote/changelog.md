# 📝 Dokumentasi Changelog & Catatan Teknis

Dokumen ini memuat catatan teknis perbaikan, peningkatan keamanan, perubahan UI/UX, serta fitur baru untuk setiap rilis **PowerDNS-Admin** yang dikelola oleh **@alsyundawy**.

---

## 🚀 Version 0.4.3-alsyundawy (2026-08-11)

> Rilis pemeliharaan utama mencakup perbaikan bug, peningkatan keamanan, idempotensi migrasi database, desain ulang UI/UX halaman login & registrasi, serta kompatibilitas Python 3.12+/3.13 — berbasis `0.4.2-alsyundawy-fix`.

### 🛡️ Perbaikan Keamanan (Security Fixes)

1. **Verifikasi SSL API PowerDNS** (`lib/helper.py`)
   - Menghapus nilai konstan `verify = False` dan menggantinya dengan nilai dinamis dari database `Setting().get('verify_ssl_connections')`.

2. **Proteksi Serangan Replay TOTP** (`models/user.py` & Migrasi `d2e3f4a5b6c7`)
   - Menambahkan pelacakan kolom `otp_last_used` agar token TOTP yang sama tidak dapat digunakan kembali dalam window validitas yang sama.

3. **Isolasi Identitas Autentikasi API** (`decorators.py` / `routes/api.py`)
   - `api_current_user` (`LocalProxy`) menjamin kredensial Cookie Session tidak menimpa autentikasi HTTP Basic Auth pada endpoint API.

4. **Penanganan Sesi CSRF Kadaluarsa** (`routes/index.py` & `routes/base.py`)
   - Menghapus sesi dan logout otomatis saat CSRF token kadaluarsa; menyajikan pemberitahuan ramah pengguna tanpa error HTTP 403 mentah.

5. **Otorisasi Templat Zone** (`routes/admin.py`)
   - Decorator `@operator_role_required` ditambahkan pada rute `/template/<template>/apply` untuk mencegah modifikasi templat tanpa hak akses.

6. **Pengerasan Status DNSSEC** (`routes/domain.py`)
   - Menampilkan error API PowerDNS (`HTTP 502`); flag status DNSSEC hanya berubah setelah operasi API dikonfirmasi berhasil.

### ⚡ Idempotensi Database & Migrasi

1. **Alokasi Role Defensif** (`models/role.py` & `models/user.py`)
   - `Role.get_id_by_name(name)` secara otomatis mendaftarkan role default (`User`, `Administrator`, `Operator`) jika tabel `role` masih kosong. Mencegah `AttributeError: 'NoneType' object has no attribute 'id'`.

2. **Migrasi Database Idempoten & Auto-Stamp** (`migrations/env.py` & `versions/787bdba9e147_init_db.py`)
   - `787bdba9e147_init_db.py` memeriksa keberadaan tabel sebelum mengeksekusi `CREATE TABLE account`.
   - `migrations/env.py` men-stamp `alembic_version` ke revisi `head` (`d2e3f4a5b6c7`) secara otomatis jika skema database sudah ada, mengeliminasi error `table ... already exists`.

3. **Kompatibilitas Flask-Session 0.6+** (`powerdnsadmin/__init__.py` & `models/sessions.py`)
   - `SESSION_SQLALCHEMY = models.db` diikat sebelum `Session(app)` diinisialisasi; model `Sessions` menggunakan `extend_existing = True`.

### 🐛 Perbaikan Bug & Stabilitas UI

1. **Perbaikan Redirect Autentikasi** (`routes/index.py`)
   - `authenticate_user()` kini mengarahkan pengguna ke `dashboard.dashboard` setelah login berhasil.

2. **Validasi CAPTCHA Kondisional** (`routes/index.py`)
   - Kondisi diubah menjadi `if CAPTCHA_ENABLE and not captcha.validate():` agar pendaftaran berhasil saat fitur CAPTCHA dinonaktifkan.

3. **Context Processor Versi** (`powerdnsadmin/__init__.py` & `base.html`)
   - `@app.context_processor` `inject_pdns_version` didaftarkan secara global untuk mencegah `TypeError: Object of type Undefined is not JSON serializable` pada seluruh sub-menu dashboard.

4. **Identitas Footer Rilis** (`base.html` & `1base.html`)
   - Footer diubah menjadi **Version 0.4.3 Modified By Alsyundawy**.

5. **Preservasi Custom Headers** (`lib/utils.py`)
   - `fetch_remote` tidak lagi membuang header kustom dari pemanggil (contoh: `X-API-Key`).

6. **Pemeriksaan Tipe Response Hapus DNSSEC** (`models/domain.py`)
   - Guard `isinstance(jdata, dict)` ditambahkan pada respons `delete_dnssec_key`.

7. **Kelas Karakter Kebijakan Password** (`routes/index.py`)
   - Pemeriksaan kelas karakter diperbaiki menggunakan `ascii_lowercase`, `ascii_uppercase`, dan `punctuation`.

### 🎨 Desain Ulang UI/UX (login.html & register.html)

1. **Desain Ulang Halaman Registrasi** (`register.html`)
   - Tampilan modern dengan kartu glassmorphism, latar animasi gradien, indikator kekuatan password real-time, dan toggle tema gelap/terang.
   - Penambahan label `sr-only` untuk semua kontrol form (aksesibilitas screen-reader) dan field honeypot anti-bot.

2. **Duplikat Kontrol Form `auth_method`** (`login.html`)
   - Menghapus `name="auth_method"` dari `<select>` dan semua hidden input Jinja2 kondisional. Diganti dengan satu `<input type="hidden" id="auth_method_hidden" name="auth_method">` yang disinkronkan via JS saat halaman dimuat dan pada event `change`.

3. **Kontras Teks Alert WCAG 2.1 AA** (`login.html` & `register.html`)
   - Warna teks `.alert` diubah dari `#ff9999` / `#fca5a5` menjadi `#ffffff` dengan background `rgba(239,68,68,0.20)` untuk memenuhi rasio kontras ≥ 4.5:1.

4. **Penanganan Exception `safeSrc()`** (`login.html` & `register.html`)
   - `void urlErr;` ditambahkan di dalam blok `catch (urlErr)` pada fungsi `safeSrc()` agar exception yang ditangkap diakui secara eksplisit, memenuhi aturan linter *"Handle this exception or don't catch it at all"*.

### 🔧 Kualitas Kode, CI/CD & Pembaruan

1. **Kompatibilitas Python 3.12+/3.13**
   - Mengganti `distutils` yang sudah dihapus dengan helper lokal `version_tuple` dan `strtobool`.
   - Mengganti `imghdr` yang sudah deprecated dengan deteksi berbasis magic-byte signature.

2. **Jekyll GitHub Pages CI/CD**
   - Menambahkan workflow `.github/workflows/jekyll-gh-pages.yml` untuk deployment otomatis situs dokumentasi ke GitHub Pages.

3. **Pembenahan Linter**
   - Menghapus kode mati, binding exception yang tidak ditangani, dan raw escape sequence.

4. **Desain Ulang README & Badge**
   - Header README dirancang ulang dengan badge blok terpusat: `for-the-badge` untuk badge primer, `flat-square` untuk badge sekunder.
   - Ditambahkan tabel sumber daya dokumentasi dan ringkasan changelog lengkap.

---

## 🎨 Version 0.4.2-alsyundawy-fix (2026-08-09)

Rilis perbaikan keamanan antarmuka (frontend) oleh **@alsyundawy**.

- **Commit:** `bcbb766`
- **Compare URL:** `0.4.2-alsyundawy...0.4.2-alsyundawy-fix`

### 🔒 Perbaikan Keamanan Antarmuka

1. **Templat Login** (`6login.html`, `7login.html`, `8login.html`)
   - Peningkatan fungsi `safeSrc` untuk pengolahan logo, pencegahan URL sumber yang tidak valid, dan validasi URL pada tema terang.

2. **Templat Registrasi** (`register.html`)
   - Penambahan atribut `nonce="{{ CSP_NONCE|default('') }}"` pada tag script.
   - Validasi skema URL pada parameter redirect untuk mencegah injeksi `javascript:` / `data:`.

---

## 🔒 Version 0.4.2-alsyundawy (2026-08-09)

Rilis perbaikan keamanan komprehensif, remediasi peringatan CodeQL, dan kompatibilitas RFC2317 oleh **@alsyundawy**.

- **Commit:** `789c185`
- **Compare URL:** `0.4.2...0.4.2-alsyundawy`

### 🛡️ Remediasi Keamanan & CodeQL

1. **Kepatuhan RFC2317** — Escaping nama zone pada URL API zones (#1).
2. **Endpoint OIDC Userinfo** — Perbaikan bug pada endpoint OIDC userinfo (#2).
3. **Injeksi Query LDAP** — Sanitasi query LDAP dari masukan pengguna (CodeQL Alert #17 / PR #9).
4. **Proteksi Full SSRF** — Hardening pencegahan Server-Side Request Forgery (CodeQL Alert #13 / PR #8).
5. **Hardening XSS & DOM** — Pencegahan Reflected XSS dan re-interpretasi elemen DOM sebagai HTML (CodeQL Alerts #1, #15, #18, #19, #20, #27, #29 / PRs #10, #11, #13–#16, #18).
6. **Mode Debug Flask** — Menonaktifkan mode debug Flask pada lingkungan produksi (CodeQL Alert #16 / PR #12).

### 📦 Pembaruan Dependensi

- `cryptography`: `45.0.5` → `46.0.5` → `48.0.1` → `50.0.0` (#19, #25, #28)
- `pyasn1`: `0.6.2` → `0.6.4` (#26)
- `setuptools`: `80.9.0` → `83.0.0` (#27)

---

## 📦 Version 0.4.2 (Upstream Official — 2022-01-31)

Rilis resmi dari **PowerDNS-Admin**.

- Upgrade ke SQLAlchemy 1.4.x — format URL database harus menggunakan `postgresql://`.
- Peningkatan konfigurasi otomatis provider OAuth.
- Perbaikan pencarian pengguna lokal yang case-insensitive.
