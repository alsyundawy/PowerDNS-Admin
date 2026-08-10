# ⚡ PowerDNS-Admin — Modified by Alsyundawy

[![Version](https://img.shields.io/badge/version-0.4.3--alsyundawy-brightgreen?style=for-the-badge)](https://github.com/alsyundawy/PowerDNS-Admin/releases)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Latest Release](https://img.shields.io/github/v/release/alsyundawy/PowerDNS-Admin?style=for-the-badge&logo=github)](https://github.com/alsyundawy/PowerDNS-Admin/releases)
[![License](https://img.shields.io/github/license/alsyundawy/PowerDNS-Admin?style=for-the-badge)](LICENSE)
[![Maintenance](https://img.shields.io/maintenance/yes/9999?style=for-the-badge)](https://github.com/alsyundawy/PowerDNS-Admin/)

[![GitHub Issues](https://img.shields.io/github/issues/alsyundawy/PowerDNS-Admin?style=flat-square&logo=github)](https://github.com/alsyundawy/PowerDNS-Admin/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/alsyundawy/PowerDNS-Admin?style=flat-square&logo=github)](https://github.com/alsyundawy/PowerDNS-Admin/pulls)
[![GitHub Stars](https://img.shields.io/github/stars/alsyundawy/PowerDNS-Admin?style=flat-square&logo=github)](https://github.com/alsyundawy/PowerDNS-Admin/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/alsyundawy/PowerDNS-Admin?style=flat-square&logo=github)](https://github.com/alsyundawy/PowerDNS-Admin/network/members)
[![Contributors](https://img.shields.io/github/contributors/alsyundawy/PowerDNS-Admin?style=flat-square&logo=github)](https://github.com/alsyundawy/PowerDNS-Admin/graphs/contributors)

[![Donate PayPal](https://img.shields.io/badge/Donate-PayPal-003087?style=flat-square&logo=paypal&logoColor=white)](https://www.paypal.me/alsyundawy)
[![Donate Ko-fi](https://img.shields.io/badge/Donate-Ko--fi-ff5e5b?style=flat-square&logo=ko-fi&logoColor=white)](https://ko-fi.com/alsyundawy)
[![GitHub Sponsor](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa?style=flat-square&logo=github-sponsors&logoColor=white)](https://github.com/sponsors/alsyundawy)

---

A **modern, secure, and feature-rich** Web Management Interface for [PowerDNS](https://www.powerdns.com/), enhanced with advanced security hardening, Role-Based Access Control (RBAC), multi-backend authentication, dynamic zone templating, Python 3.12+/3.13 compatibility, and automated database migration idempotency — maintained by **[@alsyundawy](https://github.com/alsyundawy)**.

---

## 🌟 Key Features

| Category | Features |
| :--- | :--- |
| 🌐 **Zone Management** | Forward & Reverse DNS (IPv4/IPv6 PTR), Zone Templating, IDN/Punycode, DNSSEC Management |
| 🔐 **Authentication** | Local, SAML 2.0, LDAP (OpenLDAP/Active Directory), OAuth2 (Google, GitHub, Azure, OpenID) |
| 🛡️ **Security** | TOTP 2FA with Replay Protection, RBAC, API Key Isolation, CSRF Protection, SSRF Prevention |
| 📊 **Monitoring** | Real-time PowerDNS Stats, Activity Logging, Audit Trail, Zone Change History |
| ⚡ **Automation** | RESTful API for Zone/Record Automation, DynDNS2 Protocol, Docker & Compose Ready |
| 🐍 **Compatibility** | Python 3.10–3.13, Flask 3.x, SQLAlchemy 1.4+, PostgreSQL / MySQL / SQLite |

---

## 🚀 Quick Start

### Option 1 — Docker *(Recommended)*

```bash
docker run -d \
  --name powerdns-admin \
  -e SECRET_KEY='replace-with-a-long-secure-random-key' \
  -v pda-data:/data \
  -p 9191:80 \
  alsyundawy/powerdns-admin:latest
```

Access the interface at `http://localhost:9191`.

### Option 2 — Docker Compose

```bash
git clone https://github.com/alsyundawy/PowerDNS-Admin.git
cd PowerDNS-Admin
docker-compose up -d
```

---

## ⚙️ Configuration & Environment Variables

PowerDNS-Admin supports configuration via environment variables or custom config files (`docker_config.py` / `config.py`):

| Variable | Description | Default |
| :--- | :--- | :--- |
| `SECRET_KEY` | Secret key for session encryption | *(Required)* |
| `SQLALCHEMY_DATABASE_URI` | Database connection URI | `sqlite:////data/pdns.db` |
| `PDNS_STATS_URL` | PowerDNS API endpoint URL | `http://127.0.0.1:8081` |
| `PDNS_API_KEY` | PowerDNS API Key | `""` |
| `CAPTCHA_ENABLE` | Enable CAPTCHA on registration page | `True` |

---

## 📸 Interface Preview

![Dashboard Preview](docs/screenshots/dashboard.png)

---

## 📋 Changelog Summary

### 🚀 [0.4.3-alsyundawy] — 2026-08-11

> Comprehensive maintenance, security hardening, database migration idempotency, UI/UX redesign, and Python 3.12+/3.13 compatibility — built on top of `0.4.2-alsyundawy-fix`.

#### 🛡️ Security Enhancements

- **Dynamic SSL Verification** — Replaced hardcoded `verify = False` with `Setting().get('verify_ssl_connections')` in `lib/helper.py`.
- **TOTP Replay Protection** — Atomic token consumption via `otp_last_used`; prevents replay attacks.
- **API Identity Isolation** — `api_current_user` (`LocalProxy`) ensures session cookies cannot override API Basic Auth.
- **Stale CSRF Handling** — Graceful session invalidation on CSRF failures with user-friendly notices (no raw `403`).
- **DNSSEC State Hardening** — DNSSEC flags only mutate after confirmed API success (`HTTP 502` surfaced).
- **Zone Template Authorization** — `@operator_role_required` guard on `/template/<template>/apply`.

#### ⚡ Database & Migration Idempotency

- **Defensive Role Seeding** — `Role.get_id_by_name(name)` auto-seeds default roles on empty databases.
- **Idempotent Migrations** — `787bdba9e147_init_db.py` checks table existence before `CREATE TABLE`; `env.py` auto-stamps `alembic_version` to `head`.
- **Flask-Session 0.6+ Compatibility** — `SESSION_SQLALCHEMY = models.db` bound before `Session(app)`; `Sessions` uses `extend_existing = True`.

#### 🐛 Bug Fixes & UI Stability

- **Login Redirect** — Fixed `authenticate_user()` to redirect to `dashboard.dashboard` on success.
- **CAPTCHA Toggle** — Registration skips CAPTCHA validation when `CAPTCHA_ENABLE = False`.
- **Context Processor** — `inject_pdns_version` registered globally; prevents `TypeError` on dashboard sub-menus.
- **Footer Version String** — Updated to `Version 0.4.3 Modified By Alsyundawy`.
- **Custom Headers** — `fetch_remote` no longer drops caller-supplied headers (e.g., `X-API-Key`).
- **DNSSEC Key Deletion** — `isinstance(jdata, dict)` guard added in `models/domain.py`.
- **Password Policy** — Fixed character class checks to use `ascii_lowercase`, `ascii_uppercase`, and `punctuation`.

#### 🎨 UI/UX Redesign (login.html & register.html)

- **Registration Page** — Fully redesigned with modern glassmorphism card, animated gradient background, real-time password strength meter, and dark/light theme toggle.
- **Duplicate Form Control** — Single `<input type="hidden" id="auth_method_hidden">` replaces duplicate controls; JS syncs the dropdown.
- **WCAG 2.1 AA Alert Contrast** — Alert text `#ffffff` with `rgba(239,68,68,0.20)` background (contrast ≥ 4.5:1).
- **`safeSrc()` Linter Compliance** — `void urlErr;` added in `catch` block; screen-reader labels and honeypot field included.

#### 🔧 Code Quality & CI/CD

- **Python 3.12+/3.13** — Replaced `distutils` and deprecated `imghdr` with modern alternatives.
- **Jekyll CI/CD** — Added `.github/workflows/jekyll-gh-pages.yml` for automated GitHub Pages deployment.
- **Linter Cleanup** — Resolved dead code, unhandled exception bindings, and raw escape sequences.

---

### 🛠️ [0.4.2-alsyundawy-fix] — 2026-08-09

Frontend security and template hardening. Commit: `bcbb766`.

- `safeSrc` logo URL validation improvements; CSP nonce on `register.html`; redirect URL scheme validation.

---

### 🔒 [0.4.2-alsyundawy] — 2026-08-09

Comprehensive security & CodeQL remediation release. Commit: `789c185`.

- RFC2317, OIDC, LDAP injection, SSRF, XSS/DOM hardening, production debug mode disabled.
- Dependencies: `cryptography` → `50.0.0`, `pyasn1` → `0.6.4`, `setuptools` → `83.0.0`.

---

### 📦 [0.4.2] — 2022-01-31 *(Upstream)*

SQLAlchemy 1.4 upgrade (`postgresql://` URI required), OAuth auto-config, case-insensitive user lookup.

---

## 📖 Documentation & Resources

| Resource | Link |
| :--- | :--- |
| 📄 API Reference | [docs/API.md](docs/API.md) |
| 🔑 OAuth Setup Guide | [docs/oauth.md](docs/oauth.md) |
| 📋 Full Changelog | [CHANGELOG.md](CHANGELOG.md) |
| 📝 Technical Notes | [docnote/changelog.md](docnote/changelog.md) |
| 🤝 Contribution Guide | [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) |

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
Maintained with ❤️ by **[@alsyundawy](https://github.com/alsyundawy)**.
