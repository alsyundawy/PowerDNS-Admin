# 📋 Project Changelog

All notable changes, security fixes, database migration updates, and UI improvements for **PowerDNS-Admin** are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## 🚀 [0.4.3-alsyundawy] — 2026-08-11

> Comprehensive maintenance, security hardening, database migration idempotency, UI/UX redesign, and Python 3.12+/3.13 compatibility release — built on top of `0.4.2-alsyundawy-fix`.

### 🛡️ Security Enhancements

- **Dynamic PowerDNS API SSL Verification** (`lib/helper.py`)
  - Replaced hardcoded `verify = False` with dynamic setting `Setting().get('verify_ssl_connections')`.
- **TOTP Replay Protection** (`models/user.py` & Migration `d2e3f4a5b6c7`)
  - Atomic single-step token consumption with `otp_last_used` tracking; prevents replay attacks within validity windows.
- **API Identity & Basic Auth Isolation** (`decorators.py` / `routes/api.py`)
  - `api_current_user` (`LocalProxy`) resolves strictly to request-scoped credentials; session cookies cannot override API Basic Auth identity.
- **Stale CSRF Session Protection** (`routes/index.py` & `routes/base.py`)
  - Graceful session invalidation on CSRF failures with user-friendly expiration notices instead of raw `403` errors.
- **DNSSEC State Hardening** (`routes/domain.py`)
  - Surfaced PowerDNS API errors (`HTTP 502`); DNSSEC flags only mutate after successful API operations.
- **Zone Template Mutation Protection** (`routes/admin.py`)
  - `@operator_role_required` guard added to `/template/<template>/apply`.

### ⚡ Database & Migration Idempotency

- **Defensive Role Seeding** (`models/role.py` & `models/user.py`)
  - `Role.get_id_by_name(name)` auto-seeds default roles (`User`, `Administrator`, `Operator`) if missing; eliminates `AttributeError` on fresh deployments.
- **Idempotent DB Migrations & Auto-Stamping** (`migrations/env.py` & `versions/787bdba9e147_init_db.py`)
  - Migration `787bdba9e147_init_db.py` checks table existence before `CREATE TABLE account`.
  - `env.py` auto-stamps `alembic_version` to `head` (`d2e3f4a5b6c7`) on pre-created schemas, eliminating `table ... already exists` deployment errors.
- **Flask-Session 0.6+ Compatibility** (`powerdnsadmin/__init__.py` & `models/sessions.py`)
  - `SESSION_SQLALCHEMY = models.db` bound before `Session(app)`; `Sessions` model uses `extend_existing = True`.

### 🐛 Bug Fixes & UI Stability

- **Login Redirect Correction** (`routes/index.py`) — `authenticate_user()` now correctly redirects to `dashboard.dashboard` on success.
- **Conditional CAPTCHA Validation** (`routes/index.py`) — Registration skips CAPTCHA when `CAPTCHA_ENABLE = False`.
- **Global Context Processor** (`powerdnsadmin/__init__.py` & `base.html`) — `inject_pdns_version` registered globally; prevents `TypeError` across all dashboard sub-menus.
- **Footer Version String** (`base.html` & `1base.html`) — Updated to `Version 0.4.3 Modified By Alsyundawy`.
- **Custom Headers Preservation** (`lib/utils.py`) — `fetch_remote` no longer drops caller-supplied headers (e.g., `X-API-Key`).
- **DNSSEC Key Deletion** (`models/domain.py`) — `isinstance(jdata, dict)` guard added on `delete_dnssec_key` responses.
- **Password Policy Character Classes** (`routes/index.py`) — Fixed checks to use `ascii_lowercase`, `ascii_uppercase`, and `punctuation`.

### 🎨 UI/UX Redesign (login.html & register.html)

- **Registration Page Full Redesign** (`register.html`)
  - Modern glassmorphism card with animated gradient background, real-time password strength meter, dark/light theme toggle, and responsive layout.
  - Added `sr-only` screen-reader labels for all form controls and a honeypot anti-bot field for improved accessibility and security.
- **Duplicate `auth_method` Form Control** (`login.html`)
  - Removed `name="auth_method"` from `<select>` and all Jinja2 conditional hidden inputs. Replaced with a single `<input type="hidden" id="auth_method_hidden" name="auth_method">` synced via JS on page-load and `change` events.
- **WCAG 2.1 AA Alert Contrast** (`login.html` & `register.html`)
  - Alert text changed to `#ffffff` with `rgba(239,68,68,0.20)` background, meeting contrast ratio ≥ 4.5:1.
- **`safeSrc()` Exception Handling** (`login.html` & `register.html`)
  - `void urlErr;` added inside `catch (urlErr)` to satisfy linter rule *"Handle this exception or don't catch it at all"*.

### 🔧 Code Quality & CI/CD

- **Python 3.12+/3.13 Compatibility** — Replaced removed `distutils` with `version_tuple`/`strtobool` helpers; deprecated `imghdr` replaced with magic-byte image type signatures.
- **Jekyll GitHub Pages CI/CD** — Added `.github/workflows/jekyll-gh-pages.yml` for automated documentation site deployment.
- **Linter Cleanup** — Resolved dead code, unhandled exception bindings, and raw escape sequences.
- **README & Badge Overhaul** — Redesigned README with centered badge block (`for-the-badge` primary, `flat-square` secondary), documentation resource table, and full changelog summary.

---

## 🛠️ [0.4.2-alsyundawy-fix] — 2026-08-09

Frontend security and template hardening release by **@alsyundawy**.

- **Commit:** `bcbb766`
- **Full Changelog:** `0.4.2-alsyundawy...0.4.2-alsyundawy-fix`

### 🎨 Frontend & Template Security

- **Login Templates** (`6login.html`, `7login.html`, `8login.html`)
  - Improved `safeSrc` logo handling to validate light-theme logo URLs and prevent invalid source attributes.
- **register.html**
  - Added `nonce="{{ CSP_NONCE|default('') }}"` to script tags.
  - URL scheme validation on redirect parameters blocks `javascript:` / `data:` URI injection.

---

## 🔒 [0.4.2-alsyundawy] — 2026-08-09

Comprehensive security release, CodeQL scanning alert remediations, and RFC2317 compliance by **@alsyundawy**.

- **Commit:** `789c185`
- **Full Changelog:** `0.4.2...0.4.2-alsyundawy`

### 🛡️ Security Fixes & CodeQL Remediations

- **RFC2317 Zone Name Escaping** — Zone names fully escaped in API URLs (#1).
- **OIDC Endpoint Fix** — Resolved OIDC userinfo endpoint issue (#2).
- **LDAP Query Injection** — LDAP queries sanitized from user-controlled input (CodeQL Alert #17 / PR #9).
- **Full SSRF Prevention** — Server-Side Request Forgery protections hardened (CodeQL Alert #13 / PR #8).
- **XSS & DOM Hardening** — Prevented reflected XSS and DOM HTML re-interpretation (CodeQL Alerts #1, #15, #18, #19, #20, #27, #29 / PRs #10, #11, #13–#16, #18).
- **Production Debug Mode** — Flask debug mode disabled in production defaults (CodeQL Alert #16 / PR #12).

### 📦 Dependency Updates

- `cryptography`: `45.0.5` → `46.0.5` → `48.0.1` → `50.0.0` (#19, #25, #28)
- `pyasn1`: `0.6.2` → `0.6.4` (#26)
- `setuptools`: `80.9.0` → `83.0.0` (#27)

---

## 📦 [0.4.2] — 2022-01-31 *(Upstream)*

Official upstream release from **PowerDNS-Admin**.

### 📌 Upstream Highlights

- **SQLAlchemy 1.4 Upgrade** — Database connection strings must use `postgresql://` (not `postgres://`).
- OAuth provider auto-configuration enhancements.
- Case-insensitive local user lookup fixes.
