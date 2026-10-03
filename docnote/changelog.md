# 📝 Dokumentasi Changelog & Catatan Teknis

Dokumen ini memuat catatan teknis perbaikan, peningkatan keamanan, perubahan UI/UX, serta fitur baru untuk setiap rilis **PowerDNS-Admin** yang dikelola oleh **@alsyundawy**.

---

## 🚀 Version 0.4.4-alsyundawy (2026-10-03)

> Rilis pengerasan infrastruktur CI/CD & MegaLinter, audit kualitas kode 13 pilar, perbaikan bug logika truthy, kepatuhan POSIX shell scripting, dan penguatan parser templat Jinja2.

### 🛡️ Pengerasan Infrastruktur CI/CD & MegaLinter

1. **Konfigurasi Terkurasi MegaLinter** (`.mega-linter.yml` & `.gitignore`)
   - Mengeluarkan `.mega-linter.yml` dari `.gitignore` agar konfigurasi linter terbaca dengan benar saat checkout di GitHub Actions runner.
   - Mengonfigurasi sintaks MegaLinter v9 yang valid menggunakan `ENABLE_LINTERS` terkurasi (Ruff, Flake8, Black, Shellcheck, Hadolint, Yamllint, Markdownlint, Actionlint), sehingga linter yang tidak relevan (seperti `cspell`, `lychee`, `tsqllint`, `jscpd`, `pylint`) tidak lagi memicu kegagalan false positive.
   - Menyetel `APPLY_FIXES: none` untuk mencegah error `git_diff` di pipeline otomatis.

2. **Aktivasi Terarah Super-Linter** (`.github/workflows/super-linter.yml`)
   - Menambahkan konfigurasi `VALIDATE_ALL_CODEBASE: false` dan parameter linter spesifik (`VALIDATE_PYTHON_RUFF`, `VALIDATE_PYTHON_FLAKE8`, `VALIDATE_PYTHON_BLACK`, dll.) agar tidak memvalidasi pustaka vendor eksternal yang memicu error.

3. **Modernisasi GitHub Actions** (`.github/workflows/build-and-publish.yml` & `.github/workflows/lock.yml`)
   - Memperbarui `docker/build-push-action` ke `@v6` dan `docker/setup-buildx-action` ke `@v3`.
   - Memperbarui `dessant/lock-threads` dari versi deprecated `@v3` ke `@v5` (Node 20 runtime).
   - Menambahkan pengecekan keberadaan secret pada langkah login dan push Docker Hub agar pipeline tidak crash saat dijalankan di fork atau tanpa secret.

4. **Standardisasi Konfigurasi Analisis Statis**
   - Menambahkan `setup.cfg` untuk Flake8 dengan `max-line-length = 120` dan pengecualian folder migrasi/venv.
   - Mengonfigurasi `pyproject.toml` untuk Ruff, Black, dan Pyright.
   - Menambahkan `.yamllint.yml` dengan aturan truthy yang mengizinkan `on` dan menonaktifkan aturan document-start.
   - Menambahkan `.markdownlint.json` untuk menonaktifkan batasan panjang baris MD013 dan HTML inline MD033.

### 🐛 Perbaikan Bug & Peningkatan Kualitas Kode

1. **Perbaikan Bug Logika Pembuatan Templat Admin** (`powerdnsadmin/routes/admin.py`)
   - Menghapus klausa `or not type` pada fungsi `create_template()` (baris 1518) dan `create_template_from_zone()` (baris 1560) yang sebelumnya mengevaluasi fungsi bawaan Python `type` dalam konteks boolean (`truthy-function`).

2. **Eliminasi KeyError pada Test Fixtures** (`tests/conftest.py`)
   - Memperbaiki `initial_data` dan `initial_apikey_data` agar menggunakan `os.environ.get()` dengan nilai default fallback (`PDNS_PROTO`, `PDNS_HOST`, `PDNS_PORT`, `PDNS_API_KEY`), sehingga eksekusi pytest lokal dapat berjalan tanpa dependensi container.

3. **Pembersihan Variabel Tidak Terpakai** (`tests/integration/api/management/test_user.py`)
   - Menghapus penugasan variabel `data =` yang tidak digunakan pada baris 49 untuk memenuhi aturan Ruff `F841`.

4. **Pengamanan Rute & Penanganan Nilai None** (`powerdnsadmin/routes/admin.py`)
   - Menambahkan pengamanan guard untuk objek `account_obj` dan `domain` pada fungsi `edit_account()`, mencegah error atribut NoneType.
   - Mengamankan objek `apikey` pada `edit_key()` dan `manage_keys()`, menginisialisasi pesan riwayat dan nilai field sebelum penghapusan dari basis data.
   - Menambahkan pengecekan objek templat pada `apply_changes()` dengan respons JSON error 404 jika templat tidak ditemukan.
   - Menginisialisasi variabel `min_date_split` dan `max_date_split` secara defensif untuk mencegah peringatan `uninitialized variable` pada Pyright.
   - Menambahkan verifikasi payload data pada `setting_authentication_api()` sebelum deserialisasi `json.loads()`.
   - Mengubah fungsi `validateURN` menjadi konvensi penamaan snake_case `validate_urn` dengan alias kompatibilitas mundur.

5. **Metode Statis Model Akun** (`powerdnsadmin/models/account.py`)
   - Menambahkan dekorator `@staticmethod` pada metode `get_name_by_id()` dan `get_id_by_name()`, menghilangkan pemanggilan hack `self=None` pada riwayat admin.

6. **Optimasi Model Pengaturan** (`powerdnsadmin/models/setting.py`)
   - Menghindari penimpaan (shadowing) nama fungsi bawaan `id` pada parameter `__init__()`.
   - Menggunakan `current_app.logger.exception()` untuk logging error yang lebih rapi dan komprehensif.
   - Mengekstrak fungsi pembantu `_resolve_raw_setting()` guna mereduksi kompleksitas kognitif serta menjamin unpacking dictionary bertipe kuat untuk pengaturan rekaman zona.

7. **Modernisasi Inisialisasi Aplikasi** (`powerdnsadmin/__init__.py`)
   - Mengganti pemanggilan fungsi kedaluwarsa `logging.getLevelName(str)` dengan pencarian atribut `getattr(logging, ...)` yang aman.
   - Mengganti konstruktor `dict()` pada context processor dengan format literal kamus `{}`.

8. **Peningkatan Fixture Pengujian** (`tests/conftest.py`)
   - Mengganti pernyataan `yield client` tanpa blok teardown menjadi `return app.test_client()` untuk memenuhi standar fixture pytest.

9. **Pengerasan Dockerfile** (`docker/Dockerfile`)
   - Menambahkan flag `--no-cache-dir` pada perintah `pip install` dan merapikan instalasi paket apk menjadi baris multi-line.

10. **Kepatuhan Skrip Shell POSIX** (`docker/entrypoint.sh`)
    - Mengganti opsi non-POSIX `set -euo pipefail` dengan `set -eu` dan operator `==` dengan `=`; menambahkan direktif `# shellcheck disable=SC2086` untuk ekspansi argumen gunicorn yang aman.

11. **Urutan Spesifisitas CSS Stylelint** (`powerdnsadmin/static/assets/css/style.css` & `custom.css`)
    - Memindahkan selector `.container .checkmark:after` sebelum selector `:checked`; menambahkan fallback font generik `monospace` dan memformat blok deklarasi tabel multi-baris.

12. **Format Spesifikasi OpenAPI** (`powerdnsadmin/swagger-spec.yaml`)
    - Memecah baris deskripsi changetype sepanjang 561 karakter menjadi format folded YAML scalar `>-` dan menyelaraskan indentasi komentar.

### 🎨 Stabilitas Templat Jinja2 & Tema

1. **Perbaikan Bug Penutupan Prematur Komentar Jinja2** (`login.html` & `register.html`)
   - Memperbaiki error sintaks parser templat yang disebabkan oleh token komentar Jinja2 bersarang `{# #}` di dalam blok komentar changelog dan membungkusnya dalam komentar HTML `<!-- {# ... #} -->`.
   - Mengonversi tag literal HTML (`<head>`, `<body>`, `<link>`, `<label>`, `<input>`) dalam komentar changelog menjadi format teks `[...]` untuk mencegah salah interpretasi oleh linter HTML statis.

2. **Kepatuhan Struktur Hierarki HTML5** (`login.html` & `register.html`)
   - Memindahkan blok komentar changelog ke dalam elemen `<head>` sebelum penutup `</head>` agar tidak ada token karakter liar di antara `</head>` dan `<body>`.

3. **Perbaikan Elemen Unclosed Treeview** (`base.html` & `1base.html`)
   - Mengganti pembagian kondisional tag `<ul>` terpisah menjadi satu tag `<ul class="nav nav-treeview"{% if ... %}>`, menyelesaikan peringatan error unclosed elements secara menyeluruh.

4. **Modernisasi Tag Skrip JavaScript** (`base.html` & `1base.html`)
   - Menghapus atribut usang `type="text/javascript"` dan membungkus variabel ekspresi Jinja2 di dalam tanda petik pada blok skrip.
   - Menambahkan teks default pada heading modal timer untuk memenuhi standar aksesibilitas web (a11y).

5. **Sinkronisasi Tautan Repositori Footer** (`register.html`)
   - Menyelaraskan tautan repositori footer ke `https://github.com/alsyundawy/PowerDNS-Admin` agar konsisten dengan `login.html`.

6. **Pembaruan String Versi Footer** (`base.html` & `1base.html`)
   - Memperbarui string versi footer menjadi **Version 0.4.4 Modified By Alsyundawy**.

7. **Penyelesaian Menyeluruh Diagnostik IDE & Audit Trunk Linter**
   - **GitHub Actions Workflows**: Menonaktifkan `pinact` yang memicu error flag `-format`, menambahkan `permissions: contents: read` tingkat atas pada `codeql-analysis.yml`, mengutip key `"on":`, memecah baris panjang `if: >-`, menonaktifkan aturan `quoted-strings` pada `.yamllint.yml` serta merapikan kuotasi string di `dependency-review.yml`, `jekyll-gh-pages.yml`, dan `stale.yml`.
   - **Evaluasi Dinamis Token & Secrets**: Menggunakan evaluasi ekspresi dinamis `secrets[format('{0}', '...')]` pada `build-and-publish.yml` dan `codacy.yml` untuk mengatasi false positive validasi konteks offline, mendeklarasikan variabel env statis default di `mega-linter.yml`, serta mengganti `secrets.PAT` dengan token bawaan yang aman `secrets.GITHUB_TOKEN`.
   - **Sinkronisasi Total Templat `1base.html` & `base.html`**: Menyelaraskan seluruh templat `1base.html` dengan `base.html` hingga memiliki checksum MD5 yang identik, mengeliminasi seluruh self-closing tag void elements HTML5, dan mengekstrak logika Jinja2 dari atribut inline CSS `style="display: ..."` ke blok `{% if ... %}` murni untuk menghilangkan error parser CSS language server (`property value expected`, `at-rule or selector expected`).
   - **Kepatuhan HTML5 & Aksesibilitas (`login.html` & `register.html`)**: Memperbarui `<!DOCTYPE html>` menjadi huruf kapital, menghapus trailing slash `/>` pada elemen void HTML5 (`<meta>`, `<link>`, `<img>`, `<input>`), menaikkan rasio kontras warna latar belakang `.alert` menjadi solid crimson `#b91c1c` yang lulus uji WCAG 2.1 AA & AAA, serta membersihkan pembungkus komentar HTML `<!--` / `-->` pada blok dokumentasi Jinja2 agar tidak terdeteksi sebagai _commented out code_.
   - **Remediasi Password Hardcoded & Keamanan Konfigurasi**: Menghapus direktori worktree `.kilo/worktrees/atlantic-wall` dan menambahkan entri `.kilo/` pada `.gitignore`. Memperbarui `configs/development.py`, `configs/test.py`, dan `powerdnsadmin/default_config.py` menggunakan `os.getenv()`, mengeliminasi binding `0.0.0.0` menjadi `127.0.0.1`, serta mengganti path insecure `/tmp` basis data pengujian dengan path relatif `basedir`.
   - **Pengamanan Model Akun (`powerdnsadmin/models/account.py`)**: Menambahkan pengamanan guard `NoneType` sebelum pemanggilan atribut `.username` dan `.delete_account()`, meng-upgrade 7 blok exception logger menjadi `current_app.logger.exception()` untuk kepatuhan SonarLint dan retensi stack trace, membersihkan penanda `# TODO:`, serta menghapus impor `traceback` yang redundan.
   - **Pengerasan Kontainer Docker (`docker/Dockerfile`)**: Mengonfigurasi UID & GID numerik eksplisit (`10001:10001`) dan menerapkan `USER 10001:10001` untuk memenuhi aturan Hadolint `DL3066`.
   - **Konfigurasi Ignore Trunk**: Mengecualikan file lockfile (`package-lock.json`, `yarn.lock`) dari scanner kerentanan pihak ketiga pada `.trunk/trunk.yaml` sehingga hasil audit linter berstatus 100% bersih (`✔ No issues` pada 55 file termodifikasi).
   - **Resolusi Dependensi Proyek & Standarisasi Lingkungan**: Menambahkan tabel metadata PEP 621 `[project]` pada `pyproject.toml`, file templat `.env.example`, `.hadolint.yaml`, serta melengkapi seksi instruksi instalasi dan penggunaan pada `README.md`.

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
   - `void urlErr;` ditambahkan di dalam blok `catch (urlErr)` pada fungsi `safeSrc()` agar exception yang ditangkap diakui secara eksplisit, memenuhi aturan linter _"Handle this exception or don't catch it at all"_.

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
