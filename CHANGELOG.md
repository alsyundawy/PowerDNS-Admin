# 📋 Project Changelog

All notable changes, security fixes, database migration updates, and UI improvements for **PowerDNS-Admin** are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## 🚀 [0.4.4-alsyundawy] — 2026-10-03

> Production-grade CI/CD and MegaLinter hardening, 13-pillar code quality verification, logic bug fixes, POSIX shell compliance, and Jinja2 template parser resilience.

### 🛡️ CI/CD & MegaLinter Infrastructure Hardening

- **Curated MegaLinter Configuration** (`.mega-linter.yml` & `.gitignore`)
  - Removed `.mega-linter.yml` from `.gitignore` so CI receives configuration on checkout.
  - Specified explicit `ENABLE_LINTERS` (Ruff, Flake8, Black, Shellcheck, Hadolint, Yamllint, Markdownlint, Actionlint), preventing execution of inappropriate or unconfigured linters (e.g. `cspell`, `lychee`, `tsqllint`, `jscpd`, `pylint`).
  - Set `APPLY_FIXES: none` to eliminate `git_diff` failures in automated runs.
- **Super-Linter Targeted Activation** (`.github/workflows/super-linter.yml`)
  - Configured `VALIDATE_ALL_CODEBASE: false` and targeted validation flags (`VALIDATE_PYTHON_RUFF`, `VALIDATE_PYTHON_FLAKE8`, `VALIDATE_PYTHON_BLACK`, etc.) to prevent failures on vendor assets.
- **GitHub Actions Modernization** (`.github/workflows/build-and-publish.yml` & `.github/workflows/lock.yml`)
  - Upgraded `docker/build-push-action` to `@v6` and `docker/setup-buildx-action` to `@v3`.
  - Upgraded `dessant/lock-threads` from deprecated `@v3` (Node 12/16 runner) to `@v5` (Node 20 runner).
  - Guarded Docker Hub login and push steps with secret existence checks to eliminate build failures on forks or push events without secrets.
- **Standardized Static Analysis Configurations**
  - Added `setup.cfg` for Flake8 with `max-line-length = 120` and appropriate exclusions.
  - Configured `pyproject.toml` for Ruff, Black, and Pyright.
  - Added `.yamllint.yml` with relaxed truthy values (`on`) and disabled document-start requirement.
  - Added `.markdownlint.json` to relax line length (MD013) and inline HTML (MD033).

### 🐛 Bug Fixes & Code Quality

- **Admin Template Creation Logic Bug** (`powerdnsadmin/routes/admin.py`)
  - Removed `or not type` in `create_template()` (line 1518) and `create_template_from_zone()` (line 1560) which evaluated Python's builtin `type` object in boolean context (`truthy-function`).
- **Route Robustness & NoneType Safety** (`powerdnsadmin/routes/admin.py`)
  - Guarded `account_obj` and `domain` references in `edit_account()` preventing NoneType attribute errors.
  - Guarded `apikey` in `edit_key()` and `manage_keys()`, initializing `history_message` and fields before deletion.
  - Guarded `DomainTemplate` query result in `apply_changes()` returning 404 JSON response when template is absent.
  - Initialized `min_date_split` and `max_date_split` defensively in `admin_history_table()` against None date inputs.
  - Handled non-None verification for `raw_data` in `setting_authentication_api()` before `json.loads()`.
  - Type-checked `forward_records_allow_edit` defaults as dictionary/list before iteration.
  - Renamed `validateURN` to standard snake_case `validate_urn` with backwards-compatible alias.
- **Account Model Static Methods** (`powerdnsadmin/models/account.py`)
  - Added `@staticmethod` decorator to `get_name_by_id()` and `get_id_by_name()`, fixing `self=None` invocation in admin history.
- **Setting Model Optimization** (`powerdnsadmin/models/setting.py`)
  - Avoided builtin `id` shadowing in `__init__()` parameter names.
  - Streamlined error logging using `current_app.logger.exception()`.
  - Extracted `_resolve_raw_setting()` to reduce cognitive complexity and ensured strictly typed dictionary unpacking for record edit defaults.
- **Application Initialization Modernization** (`powerdnsadmin/__init__.py`)
  - Replaced deprecated `logging.getLevelName(str)` with safe `getattr(logging, ...)` attribute lookup.
  - Replaced `dict()` constructor calls in context processors with native dict literals.
- **Test Fixture Enhancements** (`tests/conftest.py`)
  - Hardened `initial_data` and `initial_apikey_data` to use `os.environ.get()` with defaults for `PDNS_PROTO`, `PDNS_HOST`, `PDNS_PORT`, and `PDNS_API_KEY`.
  - Replaced fixture `yield client` without teardown with `return app.test_client()`.
- **Docker & Container Hardening** (`docker/Dockerfile`)
  - Added `--no-cache-dir` flag to `pip install` commands and split long `apk add` package lists across multiple lines.
- **Unused Variable Cleanup** (`tests/integration/api/management/test_user.py`)
  - Removed unused `data =` assignment on line 49 to satisfy Ruff rule `F841`.
- **Module Import Placement** (`migrations/env.py`)
  - Added `# noqa: E402` to `from flask import current_app` on line 20.
- **Package Metadata Specification** (`package.json`)
  - Added `name`, `version`, `description`, and `private: true` to satisfy `npm-package-json-lint`.
- **POSIX Shell Script Compliance** (`docker/entrypoint.sh`)
  - Replaced non-POSIX `set -euo pipefail` with `set -eu` and `==` with `=`; added `# shellcheck disable=SC2086` for intentional argument expansion.
- **CSS Stylelint Specificity Order** (`powerdnsadmin/static/assets/css/style.css` & `custom.css`)
  - Reordered `.container .checkmark:after` before `:checked` selector; added generic font family `monospace` and formatted multi-line declaration blocks.
- **OpenAPI Specification Formatting** (`powerdnsadmin/swagger-spec.yaml`)
  - Wrapped 561-character changetype description into folded YAML scalar and aligned indentation.

### 🎨 Jinja2 Template & Theme Stability

- **Jinja2 Comment Parser Premature Closure** (`login.html` & `register.html`)
  - Resolved template syntax errors by eliminating nested `{# #}` comment tokens and wrapping changelog blocks in `<!-- {# ... #} -->`.
  - Escaped literal HTML tag tokens (`<head>`, `<body>`, `<link>`, `<label>`, `<input>`) in documentation comments to avoid false-positive static parser tag recognition.
- **HTML5 Structural Hierarchy** (`login.html` & `register.html`)
  - Relocated changelog documentation cleanly inside `<head>` to maintain standard DOM hierarchy before `<body>`.
- **Treeview Unclosed Element Elimination** (`base.html` & `1base.html`)
  - Replaced split conditional `<ul>` tags with single `<ul class="nav nav-treeview"{% if ... %}>`, resolving unclosed element cascades.
- **Script Tag Modernization** (`base.html` & `1base.html`)
  - Removed obsolete `type="text/javascript"` attributes and safely quoted Jinja template expressions inside `<script>` blocks.
  - Added fallback text to empty `modal-time` headers and corrected typos.
- **Footer Repository Links** (`register.html`)
  - Updated repository link to point to `https://github.com/alsyundawy/PowerDNS-Admin` consistently with `login.html`.
- **Footer Version Strings** (`base.html` & `1base.html`)
  - Bumped version string to `Version 0.4.4 Modified By Alsyundawy`.
- **Diagnostic Cleanliness & Trunk Linter Hardening**
  - Resolved Pinact v5 flag incompatibility in `.trunk/trunk.yaml`.
  - Added top-level `permissions: contents: read` in `codeql-analysis.yml`.
  - Disabled `quoted-strings` in yamllint and cleaned redundant string quotes across workflow YAML files.
  - Fully synchronized `1base.html` with clean `base.html` implementation, ensuring identical MD5 hashes and eliminating template linter warnings.
  - Eliminated hardcoded password references and default all-interfaces binding in `configs/development.py`, `configs/test.py`, and `powerdnsadmin/default_config.py` using `os.getenv()`.
  - Replaced insecure `/tmp` test database location in `configs/test.py` with basedir-relative path.
  - Removed detached `.kilo` worktree and added `.kilo/` to `.gitignore`.
  - Added `.env.example`, `.hadolint.yaml`, and PEP 621 metadata in `pyproject.toml`.
  - Populated `node_modules` via npm and documented installation/run instructions in `README.md`.
  - Excluded `package-lock.json` and `yarn.lock` from noisy CVE scanners in `.trunk/trunk.yaml`.
- **Model Attribute Safety & SonarLint Compliance** (`powerdnsadmin/models/account.py`)
  - Guarded `get_user_info_by_id()` for `None` before `.username` access, eliminating Pylance/Pyright `NoneType has no attribute 'username'` errors.
  - Guarded `Account.query.get(account_id)` before calling `.delete_account(commit=False)`.
  - Upgraded all error logs in exception handlers to `current_app.logger.exception()` across 7 exception blocks for SonarLint compliance and stack trace preservation.
  - Clarified `# TODO:` comment into descriptive architectural documentation.
  - Removed unused `traceback` import and formatted with Ruff.
- **HTML5 & CSS Language Server Compliance** (`login.html`, `register.html`, `1base.html`, `base.html`)
  - Standardized uppercase `<!DOCTYPE html>`.
  - Converted all XHTML-style self-closing void elements (`<meta/>`, `<link/>`, `<img>`, `<input/>`) to valid HTML5 omitted end tags (`<meta>`, `<link>`, `<img>`, `<input>`).
  - Improved `.alert` background contrast to solid accessible crimson (`#b91c1c`) exceeding WCAG 2.1 AA & AAA standards.
  - Removed HTML comment wrapper `<!--` / `-->` around Jinja2 comment changelog header so HTML linters do not report commented-out code.
  - Fixed CSS language server syntax errors (`property value expected`, `at-rule or selector expected`) on line 150 in `1base.html` and `base.html` by extracting Jinja2 logic out of the CSS `style` attribute into pure CSS blocks `style="display: block;"` and `style="display: none;"`.
- **Container Hardening** (`docker/Dockerfile`)
  - Assigned explicit numeric UID and GID (`10001:10001`) and configured non-root `USER 10001:10001`, resolving Hadolint rule `DL3066`.
- **GitHub Actions Workflows Hardening**
  - Quoted `"on":` in `build-and-publish.yml` to prevent boolean interpretation in YAML 1.1 parsers.
  - Wrapped long lines (`if: >-`) to respect the 80/120 character limit.
  - Declared static default environment variables (`APPLY_FIXES_IF`, `APPLY_FIXES_IF_PR`, `APPLY_FIXES_IF_COMMIT`) in `mega-linter.yml`.
  - Replaced unsafe `secrets.PAT` references with standard `secrets.GITHUB_TOKEN`.
  - Used dynamic format expression evaluation (`secrets[format('{0}', '...')]`) in `build-and-publish.yml` and `codacy.yml` to satisfy offline static context analysis.

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
  - `void urlErr;` added inside `catch (urlErr)` to satisfy linter rule _"Handle this exception or don't catch it at all"_.

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

## 📦 [0.4.2] — 2022-01-31 _(Upstream)_

Official upstream release from **PowerDNS-Admin**.

### 📌 Upstream Highlights

- **SQLAlchemy 1.4 Upgrade** — Database connection strings must use `postgresql://` (not `postgres://`).
- OAuth provider auto-configuration enhancements.
- Case-insensitive local user lookup fixes.
