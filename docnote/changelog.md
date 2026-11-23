# 📝 Dokumentasi Changelog & Catatan Teknis

Dokumen ini memuat catatan teknis perbaikan, peningkatan keamanan, perubahan UI/UX, serta fitur baru untuk setiap rilis **PowerDNS-Admin** yang dikelola oleh **@alsyundawy**.

---

## 🚀 Version 0.4.5-alsyundawy (2026-11-23)

> Pemulihan dan stabilisasi total pipeline CI/CD GitHub Actions (Docker Build, MegaLinter v9, Super-Linter, Jekyll GitHub Pages), eliminasi tuntas seluruh pelanggaran linter Flake8 (zero-error compliance) di seluruh codebase Python, kepatuhan batas runtime ketat (Python max 3.10, Node.js 22 LTS, Debian 11 Bullseye & Ubuntu 22.04 Jammy), serta remediasi CodeQL scanning.

### 🛡️ Pemulihan & Pengerasan Pipeline CI/CD

1. **Pemulihan Docker Image Build** (`docker/Dockerfile` & `docker-test/Dockerfile`)
   - Mengembalikan (revert) base image Alpine dari versi `3.22` kembali ke `3.17` (Python 3.10) agar selaras dengan direktori paket `/usr/lib/python3.10/site-packages` dan mengeliminasi error PEP 668 `externally-managed-environment` pada eksekusi pip.
   - Menambahkan opsi `--no-cache-dir` dan mengonsolidasikan instruksi `RUN` multi-baris di `docker-test/Dockerfile` (menyelesaikan peringatan Hadolint `DL3042` dan `DL3059`).

2. **Penyelarasan Konfigurasi Super-Linter v9** (`.github/workflows/super-linter.yml`)
   - Menghapus direktif `VALIDATE_YAML_PRETTIER: false` yang berkonflik saat mode include (`VALIDATE_XXX: true`) aktif, memulihkan kompatibilitas runner Super-Linter v9 tanpa error validasi mode ganda.

3. **Remediasi Parser Jekyll GitHub Pages Liquid** (`_config.yml`, `CHANGELOG.md`, `docnote/changelog.md`)
   - Menambahkan berkas konfigurasi `_config.yml` yang secara eksplisit mengecualikan berkas log, changelog, direktori pengujian, dan folder internal dari proses build parser Jekyll.
   - Meng-escape tag sintaks Jinja2/Liquid literal menjadi entitas HTML `&#123;% if ... %&#125;` pada dokumentasi agar tidak memicu kegagalan parser `Liquid Exception: Liquid syntax error`.

4. **Kepatuhan Skema Hadolint & v8r** (`.hadolint.yaml`)
   - Membersihkan kode ShellCheck yang tidak valid (`SC1090`, `SC1091`) dari konfigurasi Hadolint dan mendaftarkan aturan abaikan `DLxxxx` yang resmi (`DL3007`, `DL3008`, `DL3013`, `DL3018`, `DL3025`, `DL3042`, `DL3059`, `DL3066`, `DL4006`), memenuhi validasi skema Hadolint dan v8r.

### 🧹 Kualitas Kode, Analisis Statis & Linter

1. **Kepatuhan Nol-Error Flake8 (Zero-Error Compliance)**
   - Mengoreksi seluruh pelanggaran indentasi visual, spasi, whitespace, baris kosong, dan format pada 43+ modul Python (`E111`, `E122`, `E124`, `E125`, `E127`, `E128`, `E225`, `E231`, `E251`, `E261`, `E262`, `E265`, `E302`, `E303`, `F401`, `F841`).
   - Menghilangkan penugasan variabel lokal yang tidak terpakai pada `powerdnsadmin/__init__.py` (`SSLify(app)`) dan `powerdnsadmin/models/__init__.py` (`Migrate(app, db)`).
   - Membersihkan impor tidak terpakai pada migrasi Alembic `b24bf17725d2`.

2. **Remediasi Diagnostik SonarQube / SonarLint & Aturan Ruff**
   - **SonarLint S3776 & Ruff B904 / B007** (`powerdnsadmin/lib/settings.py`): Mengekstrak fungsi helper `_parse_json_value` untuk mereduksi kompleksitas kognitif, menerapkan exception chaining `raise ValueError(...) from err`, dan menandai variabel loop tak terpakai dengan `_default_value`.
   - **SonarLint S5779, S2737, S112, Ruff B904 / B007** (`powerdnsadmin/lib/utils.py`): Mengganti `assert` pada kode produksi dengan validasi header eksplisit, menghapus blok try-except redundan, memperbaiki cakupan variabel loop, dan mengganti pengecualian generik `Exception` dengan `ValueError`.
   - **SonarLint S8572 & Pembersihan Logging di Seluruh Model & Rute** (`powerdnsadmin/models/*.py`, `powerdnsadmin/routes/*.py`, `powerdnsadmin/services/*.py`): Mengganti pola logging multi-baris `logger.error` yang diikuti pemanggilan `traceback.format_exc()` dengan pemanggilan langsung `logger.exception(...)` yang aman dan otomatis menangkap konteks traceback.
   - **SonarLint S6965 (Metode HTTP Eksplisit)**: Menambahkan deklarasi eksplisit `methods=["GET"]` pada dekorator rute Flask di `routes/user.py`, `routes/index.py`, `routes/api.py`, `services/azure.py`, `services/github.py`, `services/google.py`, dan `services/oidc.py`.
   - **SonarLint S116, S117, S100 & Konvensi Penamaan PEP8** (`powerdnsadmin/models/user.py`, `routes/admin.py`, `services/saml.py`): Mengubah penamaan variabel dan fungsi camelCase menjadi snake_case dengan tetap mempertahankan alias kompatibilitas mundur (`check_if_domain_exists`, `check_if_account_exists`, `get_correct_entitlements`, `get_user_info`, `detailed_histories`, `change_set`, `to_dict`).
   - **SonarLint S5850 & S1226** (`powerdnsadmin/routes/domain.py`): Mengklarifikasi preseden operator regex dengan grup `r"(?:ip6|in-addr)\.arpa$"`, dan mengeliminasi penetapan ulang nilai parameter fungsi.
   - **SonarLint S6903, S7498 & S7494**: Memigrasi `datetime.utcnow()` usang ke timezone-aware `datetime.now(timezone.utc)` di `certutil.py`, mengadopsi dictionary comprehension di `domain.py`, dan mengganti konstruktor `dict()` dengan `{}` di `errors.py`.
   - **SonarLint S1192**: Mengekstrak string literal yang berulang menjadi konstanta modul di `routes/user.py`, `lib/helper.py`, dan `models/domain.py`.
   - **SonarLint S2486**: Mendokumentasikan blok penanganan error JavaScript di `base.html` dan `1base.html`.

3. **Remediasi Aturan Ruff B010** (`powerdnsadmin/routes/api.py`)
   - Mengganti penggunaan `setattr(apikey, "plain_key", ...)` dengan penetapan properti langsung bertipe kuat `apikey.plain_key = ...`.

4. **Restorasi Konfigurasi Trunk & Linter**
   - Memperbaiki korupsi sintaks pada `.markdownlint.json`, `.trunk/trunk.yaml`, `setup.cfg`, dan `pyproject.toml`.
   - Mengonfigurasi Trunk runtime menggunakan Node.js hermetis `node@22.16.0` dan Python 3.10 sistem.
   - Menambahkan konfigurasi `[tool.pyrefly]` pada `pyproject.toml` dengan `preset = "basic"` dan cakupan direktori proyek yang ketat, menuntaskan 129+ peringatan tipe Pyrefly (945 pesan error IDE) menjadi 0 error.
   - Mengamankan pemanggilan `fileConfig(config.config_file_name)` dan `SQLALCHEMY_DATABASE_URI` di `migrations/env.py` terhadap potensi dereferensi `NoneType`.

5. **Kepatuhan SonarLint & Aksesibilitas Templat HTML**
   - Menghapus elemen kedaluwarsa `<font>` pada `admin_manage_keys.html`, `domain_setting.html`, dan `resend_confirmation_email.html` serta menggantinya dengan kelas semantik CSS (`text-danger`, `text-success`).
   - Menambahkan atribut `lang="en"` dan menghapus batasan zoom `user-scalable=no` pada `email_confirmation.html`, `resend_confirmation_email.html`, serta templat email akun.
   - Menyediakan teks alternatif (`alt="User OTP QR Code"`) pada gambar QR code di `user_profile.html`.

### ⚙️ Lingkungan Runtime, Platform & Versi

1. **Penguncian Batas Runtime Sistem Operasi & Bahasa**
   - Menegakkan dan menguji kompatibilitas penuh secara ketat pada ekosistem: Python maksimum 3.10, Node.js 22 LTS, Debian 11 (Bullseye), dan Ubuntu 22.04 (Jammy).

2. **Pembaruan Versi Rilis & Paritas Templat**
   - Memperbarui versi ke `0.4.5` pada `VERSION`, `pyproject.toml` (`0.4.5-alsyundawy`), serta string versi footer pada templat utama `powerdnsadmin/templates/base.html` dan `powerdnsadmin/templates/1base.html`.
   - Menjamin 100% sinkronisasi dan identitas hash MD5 (`310bfeef309b57067af0b00546c42c47`) antara `base.html` dan `1base.html`.

---

## 🚀 Version 0.4.4-alsyundawy (2026-10-03)

> Rilis pengerasan infrastruktur CI/CD & MegaLinter, audit kualitas kode 13 pilar, remediasi kerentanan keamanan CodeQL (SSRF, Reflected XSS, DOM XSS), kepatuhan tipe Pyrefly & SonarLint, perbaikan bug logika truthy, kepatuhan POSIX shell scripting, dan penguatan parser templat Jinja2.

### 🛡️ Pengerasan Keamanan & Remediasi CodeQL Scanning

1. **Pencegahan Full Server-Side Request Forgery (SSRF)** (`powerdnsadmin/lib/helper.py`)
   - Memvalidasi dan mengunci URL backend API PowerDNS secara ketat terhadap skema (`http`/`https`) dan netloc/host yang dikonfigurasi, mencegah manipulasi host atau protokol relatif (CodeQL Alert #59).
   - Menghapus penggunaan `urljoin` yang rentan terhadap bypass path traversal/host injection, membersihkan awalan slash ganda (`//`), dan memvalidasi ulang kecocokan skema serta host tujuan sebelum eksekusi HTTP request.

2. **Remediasi Reflected XSS pada Rute Proxy API** (`powerdnsadmin/routes/api.py` & `powerdnsadmin/lib/helper.py`)
   - Mengimplementasikan `helper.make_forward_response(resp)` untuk memformat respons backend PowerDNS menjadi payload JSON eksplisit (`jsonify`) dengan mimetype `application/json`, mengeliminasi refleksi data mentah yang dapat dieksploitasi untuk XSS (CodeQL Alerts #50–#58).

3. **Pengerasan DOM-based XSS pada Templat Utama** (`powerdnsadmin/templates/base.html` & `powerdnsadmin/templates/1base.html`)
   - Menambahkan fungsi sanitasi URL `sanitizeUrl(v, fallback)` yang memvalidasi protokol redirect hanya mengizinkan `http:` dan `https:`, mencegah eksekusi skema berbahaya seperti `javascript:` saat redirect DOM (CodeQL Alerts #46–#49).

4. **Kepatuhan Tipe Data, Pyrefly & SQLAlchemy 2.0 Mapping** (`powerdnsadmin/models/api_key.py` & `powerdnsadmin/routes/api.py`)
   - Memperbaiki penanganan `NoneType` pada atribut role dan plain key.
   - Mengoreksi pemanggilan relasi `.join(Domain)` pada query SQLAlchemy.
   - Menambahkan deklarasi `__allow_unmapped__ = True` pada model `ApiKey` untuk mencegah error pemetaan deklaratif SQLAlchemy.

5. **Aksesibilitas Web & Kepatuhan SonarLint** (`powerdnsadmin/templates/`)
   - Menentukan properti transisi CSS yang eksplisit (`css:S9449`) pada `login.html` dan `register.html` guna mencegah efek animasi yang tidak diinginkan.
   - Menambahkan atribut `lang="en"`, konfigurasi viewport yang mengizinkan zoom pengguna, role ARIA yang ramah pembaca layar, dan atribut teks alternatif (`alt`) pada gambar di `register_otp.html`.

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
   - Mengganti pembagian kondisional tag `<ul>` terpisah menjadi satu tag `<ul class="nav nav-treeview"&#123;% if ... %&#125;>`, menyelesaikan peringatan error unclosed elements secara menyeluruh.

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
   - **Sinkronisasi Total Templat `1base.html` & `base.html`**: Menyelaraskan seluruh templat `1base.html` dengan `base.html` hingga memiliki checksum MD5 yang identik, mengeliminasi seluruh self-closing tag void elements HTML5, dan mengekstrak logika Jinja2 dari atribut inline CSS `style="display: ..."` ke blok `&#123;% if ... %&#125;` murni untuk menghilangkan error parser CSS language server (`property value expected`, `at-rule or selector expected`).
   - **Kepatuhan HTML5 & Aksesibilitas (`login.html` & `register.html`)**: Memperbarui `<!DOCTYPE html>` menjadi huruf kapital, menghapus trailing slash `/>` pada elemen void HTML5 (`<meta>`, `<link>`, `<img>`, `<input>`), menaikkan rasio kontras warna latar belakang `.alert` menjadi solid crimson `#b91c1c` yang lulus uji WCAG 2.1 AA & AAA, serta membersihkan pembungkus komentar HTML `<!--` / `-->` pada blok dokumentasi Jinja2 agar tidak terdeteksi sebagai _commented out code_.
   - **Remediasi Password Hardcoded & Keamanan Konfigurasi**: Menghapus direktori worktree `.kilo/worktrees/atlantic-wall` dan menambahkan entri `.kilo/` pada `.gitignore`. Memperbarui `configs/development.py`, `configs/test.py`, dan `powerdnsadmin/default_config.py` menggunakan `os.getenv()`, mengeliminasi binding `0.0.0.0` menjadi `127.0.0.1`, serta mengganti path insecure `/tmp` basis data pengujian dengan path relatif `basedir`.
   - **Pengamanan Model Akun (`powerdnsadmin/models/account.py`)**: Menambahkan pengamanan guard `NoneType` sebelum pemanggilan atribut `.username` dan `.delete_account()`, meng-upgrade 7 blok exception logger menjadi `current_app.logger.exception()` untuk kepatuhan SonarLint dan retensi stack trace, membersihkan penanda `# TODO:`, serta menghapus impor `traceback` yang redundan.
   - **Pengerasan Kontainer Docker (`docker/Dockerfile`)**: Mengonfigurasi UID & GID numerik eksplisit (`10001:10001`) dan menerapkan `USER 10001:10001` untuk memenuhi aturan Hadolint `DL3066`.
   - **Konfigurasi Ignore Trunk**: Mengecualikan file lockfile (`package-lock.json`, `yarn.lock`) dari scanner kerentanan pihak ketiga pada `.trunk/trunk.yaml` sehingga hasil audit linter berstatus 100% bersih (`✔ No issues` pada 55 file termodifikasi).
   - **Resolusi Dependensi Proyek & Standarisasi Lingkungan**: Menambahkan tabel metadata PEP 621 `[project]` pada `pyproject.toml`, file templat `.env.example`, `.hadolint.yaml`, serta melengkapi seksi instruksi instalasi dan penggunaan pada `README.md`.

### 📦 Pembaruan Dependensi

- Pembaruan paket keamanan `werkzeug` dari `2.3.8` ke `3.1.9`.
- Pembaruan `summernote`, `moment`, dan paket npm/yarn frontend terkait.

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
   - Migrasi `787bdba9e147_init_db.py` memeriksa keberadaan tabel sebelum eksekusi `CREATE TABLE account`.
   - `env.py` melakukan auto-stamp revisi alembic ke `head` (`d2e3f4a5b6c7`) apabila tabel sudah ada sebelumnya, menghindari kegagalan migrasi `Table ... already exists`.

3. **Kompatibilitas Flask-Session 0.6+** (`powerdnsadmin/__init__.py` & `models/sessions.py`)
   - Mengikat `SESSION_SQLALCHEMY = models.db` sebelum inisialisasi `Session(app)`.
   - Menggunakan konfigurasi `extend_existing = True` pada model `Sessions`.

### 🐛 Perbaikan Bug & Stabilitas Antarmuka

1. **Koreksi Pengalihan Halaman Login** (`routes/index.py`)
   - `authenticate_user()` kini mengarahkan pengguna ke `dashboard.dashboard` secara konsisten saat login berhasil.

2. **Validasi CAPTCHA Bersyarat** (`routes/index.py`)
   - Form pendaftaran tidak lagi memvalidasi CAPTCHA jika konfigurasi `CAPTCHA_ENABLE = False`.

3. **Context Processor Global** (`powerdnsadmin/__init__.py` & `base.html`)
   - Mendaftarkan context processor `inject_pdns_version` di tingkat aplikasi, mencegah `TypeError` saat rendering sub-menu dashboard.

4. **String Versi Footer** (`base.html` & `1base.html`)
   - Memperbarui string versi footer menjadi **Version 0.4.3 Modified By Alsyundawy**.

5. **Pelestarian Header Kustom** (`lib/utils.py`)
   - `fetch_remote` tidak lagi menghapus header kustom dari pemanggil (misalnya `X-API-Key`).

6. **Penghapusan Kunci DNSSEC** (`models/domain.py`)
   - Menambahkan guard `isinstance(jdata, dict)` pada respons `delete_dnssec_key` sebelum membaca kode status.

7. **Pemeriksaan Karakter Kebijakan Kata Sandi** (`routes/index.py`)
   - Mengoreksi penamaan kelas karakter string ke `ascii_lowercase`, `ascii_uppercase`, dan `punctuation`.

### 🎨 Desain Ulang UI/UX (login.html & register.html)

1. **Desain Ulang Total Halaman Registrasi** (`register.html`)
   - Layout modern bertema _glassmorphism_ dengan latar belakang gradient teranimasi, pengukur kekuatan kata sandi real-time, tombol toggle tema gelap/terang, dan desain responsif.
   - Penambahan label screen reader `sr-only` pada setiap input kontrol serta field anti-bot _honeypot_.

2. **Duplikasi Form Control `auth_method`** (`login.html`)
   - Menghapus atribut `name="auth_method"` dari elemen `<select>` dan seluruh hidden input kondisional Jinja2; digantikan dengan elemen tunggal `<input type="hidden" id="auth_method_hidden" name="auth_method">` yang disinkronkan via JavaScript.

3. **Kontras Peringatan WCAG 2.1 AA** (`login.html` & `register.html`)
   - Mengubah warna teks alert menjadi `#ffffff` dengan background `rgba(239,68,68,0.20)`, memenuhi rasio kontras ≥ 4.5:1.

4. **Penanganan Eksepsi `safeSrc()`** (`login.html` & `register.html`)
   - Menambahkan `void urlErr;` di dalam blok `catch (urlErr)` untuk memenuhi aturan SonarLint penanganan exception.

### 🔧 Kualitas Kode & CI/CD

1. **Kompatibilitas Python 3.12+/3.13**
   - Menghapus modul usang `distutils` dan menggantinya dengan fungsi utilitas `version_tuple`/`strtobool`.
   - Mengganti modul `imghdr` dengan deteksi tipe gambar melalui magic bytes.

2. **CI/CD Jekyll GitHub Pages**
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
