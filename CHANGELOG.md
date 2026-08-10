# 📋 Project Changelog

All notable changes, security fixes, database migration updates, and releases for **PowerDNS-Admin** are documented in this file.

---

## 🚀 [0.4.3-alsyundawy] - 2026-08-11

Comprehensive maintenance, security hardening, database migration idempotency, and UI stability release built on top of `0.4.2-alsyundawy-fix`.

### 🛡️ Security Enhancements

- **Dynamic PowerDNS API SSL Verification** (`lib/helper.py`)
  - Converted hardcoded `verify = False` to dynamic database setting `Setting().get('verify_ssl_connections')`.
- **TOTP Replay Protection** (`models/user.py` & Migration `d2e3f4a5b6c7`)
  - Added atomic single-step TOTP consumption with `otp_last_used` tracking to prevent token replay attacks within validity windows.
- **API Identity & Basic Auth Isolation** (`decorators.py` / `routes/api.py`)
  - Introduced `api_current_user` (`LocalProxy`) resolving strictly to request-scoped credentials, preventing session cookies from overriding API Basic Auth identity.
- **Stale CSRF Session Protection** (`routes/index.py` & `routes/base.py`)
  - Gracefully invalidates sessions and logs users out on CSRF failures, displaying friendly form expiration notices instead of raw `403` errors.
- **DNSSEC State Hardening** (`routes/domain.py`)
  - Surfaced PowerDNS API errors (`HTTP 502`) and ensured DNSSEC status flags only mutate after successful API operations.
- **Zone Template Mutation Protection** (`routes/admin.py`)
  - Added `@operator_role_required` guard to `/template/<template>/apply` to prevent unauthorized template record modifications.

### ⚡ Database & Migration Idempotency

- **Defensive Role Allocation** (`models/role.py` & `models/user.py`)
  - Added `Role.get_id_by_name(name)` class method to auto-seed default roles (`User`, `Administrator`, `Operator`) if missing, eliminating `AttributeError: 'NoneType' object has no attribute 'id'` on registration or external auth.
- **Idempotent DB Migrations & Auto-Stamping** (`migrations/env.py` & `versions/787bdba9e147_init_db.py`)
  - Initial migration `787bdba9e147_init_db.py` inspects table existence before attempting `CREATE TABLE account`.
  - `migrations/env.py` automatically detects pre-created database schemas and stamps `alembic_version` to head (`d2e3f4a5b6c7`), eliminating deployment `table ... already exists` errors.
- **Flask-Session 0.6+ & Sessions Model Compatibility** (`powerdnsadmin/__init__.py` & `models/sessions.py`)
  - Bound `SESSION_SQLALCHEMY = models.db` before `Session(app)` and added `__table_args__ = {'extend_existing': True}` to `Sessions` model.

### 🐛 Bug Fixes & UI Stability

- **Login Redirect Correction** (`routes/index.py`)
  - Fixed `authenticate_user()` redirecting back to `/login` instead of `dashboard.dashboard` upon successful authentication.
- **Conditional CAPTCHA Validation** (`routes/index.py`)
  - Updated `register()` route to evaluate `if CAPTCHA_ENABLE and not captcha.validate():`, allowing registration when CAPTCHA is disabled.
- **Global Context Processor `inject_pdns_version`** (`powerdnsadmin/__init__.py` & `base.html`)
  - Registered `inject_pdns_version` globally to prevent `TypeError: Object of type Undefined is not JSON serializable` across all dashboard sub-menus.
- **Footer Version String** (`base.html` & `1base.html`)
  - Updated footer display string to `Version 0.4.3 Modified By Alsyundawy`.
- **Custom Headers Preservation** (`lib/utils.py`)
  - Fixed `fetch_remote` dropping custom caller headers (`X-API-Key`).
- **DELETE Endpoint Type Check** (`models/domain.py`)
  - Added `isinstance(jdata, dict)` check on `delete_dnssec_key` responses.
- **Password Policy Character Classes** (`routes/index.py`)
  - Corrected policy checks to use `ascii_lowercase`, `ascii_uppercase`, and `punctuation` instead of digits.

### 🔧 Code Quality & Dependencies

- **Python 3.12+ / 3.13 Compatibility**: Replaced removed `distutils` with local helpers (`version_tuple`, `strtobool`) and replaced deprecated `imghdr` with magic-byte image type signatures.
- **Linter Cleanup**: Resolved dead code, unhandled exception bindings, and raw escape sequences.

---

## 🛠️ [0.4.2-alsyundawy-fix] - 2026-08-09

Frontend security and template hardening release by **@alsyundawy**.

- **Commit:** `bcbb766`
- **Full Changelog:** `0.4.2-alsyundawy...0.4.2-alsyundawy-fix`

### 🎨 Frontend & Template Security

- **6login.html, 7login.html, 8login.html**
  - Improved `safeSrc` logo handling function to validate light-theme logo URLs and prevent invalid source attributes.
- **register.html**
  - Added `nonce="{{ CSP_NONCE|default('') }}"` to script tags.
  - Added URL scheme validation for redirect parameters to block `javascript:` / `data:` URI injection.

---

## 🔒 [0.4.2-alsyundawy] - 2026-08-09

Comprehensive security release, CodeQL scanning alert remediations, and RFC2317 compliance by **@alsyundawy**.

- **Commit:** `789c185`
- **Full Changelog:** `0.4.2...0.4.2-alsyundawy`

### 🛡️ Security Fixes & CodeQL Remediations

- **RFC2317 Zone Name Escaping**: Fully escaped zone names in zones API URLs (#1).
- **OIDC Endpoint Fix**: Resolved issues with the OIDC userinfo endpoint (#2).
- **LDAP Query Injection**: Sanitized LDAP queries built from user-controlled sources (CodeQL Alert #17 / PR #9).
- **Full SSRF Prevention**: Hardened server-side request forgery protections (CodeQL Alert #13 / PR #8).
- **XSS & DOM Hardening**: Prevented reflected XSS and DOM text reinterpretation as HTML (CodeQL Alerts #1, #15, #18, #19, #20, #27, #29 / PRs #10, #11, #13, #14, #15, #16, #18).
- **Production Debug Mode**: Disabled Flask debug mode in production defaults (CodeQL Alert #16 / PR #12).

### 📦 Dependency Updates

- `cryptography`: `45.0.5` → `46.0.5` → `48.0.1` → `50.0.0` (#19, #25, #28)
- `pyasn1`: `0.6.2` → `0.6.4` (#26)
- `setuptools`: `80.9.0` → `83.0.0` (#27)

---

## 📦 [0.4.2] - 2022-01-31

Official upstream release from **PowerDNS-Admin**.

### 📌 Upstream Highlights

- **SQLAlchemy 1.4 Upgrade**: Requires database connection strings to use `postgresql://` instead of `postgres://`.
- OAuth provider auto-configuration enhancements.
- Case-insensitive local user lookup fixes.
