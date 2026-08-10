# Changelog

All notable changes to this project will be documented in this file.

## [0.4.3-alsyundawy] - 2026-08-09

Maintenance, bug-fix and optimization release on top of `0.4.2-alsyundawy-fix`.
The goal of this release is to remove regressions and latent bugs introduced by the
uncommitted `0.4.3-alsyundawy` working-tree changes (vs `bcbb766`) without
restructuring or removing any working functionality.

### Security Fixes

- **lib/helper.py:21** - PowerDNS API SSL verification was hardcoded off
  - `verify = False` → `verify = Setting().get('verify_ssl_connections')`
  - Fixes a critical issue where the PowerDNS API connection never verified TLS.

- **models/user.py (`verify_totp`)** - TOTP replay protection
  - A token observed by an attacker (shoulder-surfing, proxy logs) could be replayed
    while still inside the validity window. Tokens are now consumed per time-step:
    only the current/previous/next step is accepted and a step is atomically marked
    used via a conditional `UPDATE`, so the same token cannot be replayed.
  - Adds `otp_last_used` column (migration `d2e3f4a5b6c7_add_otp_replay_protection.py`)
    and clears it whenever the OTP secret is rotated/reset.

- **decorators.py / routes/api.py** - API authorization used the wrong identity
  - API views guard with `flask_login.current_user`, but Flask-Login gives the
    session cookie precedence over its request loader, so a request authenticated
    with HTTP Basic auth could be authorized as a different (session) user.
  - Added `api_current_user` (a `LocalProxy` resolving to the `api_basic_auth`
    verified user, falling back to the session user) and switched `api_can_remove_domain`,
    `api_can_create_domain` and `api_role_can` to use it; `routes/api.py` reuses the
    same proxy as `current_user`. Guard and view now always act on one identity.

- **routes/index.py / base.py** - Stale CSRF form submissions
  - After a CSRF rejection on `index.login`/`index.register` the previous code could
    leave an existing session "logged in" on the next request. `handle_access_forbidden`
    now logs the user out, clears the session, and re-renders the form with a
    friendly "form expired" message instead of a raw `403`.

- **routes/domain.py (`dnssec_enable`/`dnssec_disable`)** - DNSSEC state hardening
  - Previously returned success even when the PowerDNS call failed, and updated the
    zone's `dnssec` flag unconditionally. Now errors are surfaced (`502`) and the
    `dnssec` flag is only flipped after a successful PowerDNS operation (within a
    guarded transaction).

- **routes/admin.py (`apply_records`)** - Zone-template mutation lacked operator authorization
  - `/template/<template>/apply` only required `@login_required`, while its sibling
    template routes (`edit_template`, `delete_template`) require `@operator_role_required`.
    Any authenticated user could therefore replace a zone template's records. Added
    `@operator_role_required` to match the sibling routes.

### Bug Fixes

- **routes/index.py (`authenticate_user`)** - Login redirected back to `/login`
  - After a successful authentication the function returned
    `redirect(url_for('index.login'))` instead of the dashboard, so no user could
    actually reach the application. Fixed to redirect to `dashboard.dashboard`.

- **lib/utils.py (`fetch_remote`)** - Custom headers (e.g. `X-API-Key`) were dropped
  - The request passed `headers=headers` (the function argument) instead of
    `our_headers` (the merged headers actually built). Fixed so caller-supplied
    headers are used.

- **powerdnsadmin/models/domain.py (`delete_dnssec_key`)** - `TypeError` on DELETE
  - `fetch_json` returns `True` (no body) on a successful DELETE; the code then did
    `'error' in jdata`. Guarded with `isinstance(jdata, dict)`.

- **routes/index.py (`password_policy_check`)** - Wrong character classes enforced
  - The lowercase/uppercase/special checks used `string.digits` (copied from the
    digits branch). Corrected to `string.ascii_lowercase`, `string.ascii_uppercase`
    and `string.punctuation`. Added a `contains_attribute()` guard so empty
    `firstname`/`lastname`/`email` no longer force a never-satisfiable policy.
  - Renamed the loop variable from the builtin `input` to `user_input`.

- **powerdnsadmin/models/setting.py (`get`)** - Crash on blank/malformed JSON
  - `forward/reverse_records_allow_edit` were merged with `dict(**jdata)`, which
    raised when the stored value was empty or malformed. Added a `dict` type-check
    that falls back to the defaults.

- **powerdnsadmin/lib/settings.py (`pwd_min_special`)** - Wrong type
  - Was `bool`; reverted to `int` (default `0`) so the registration template can bind
    it as a number and the policy check treats it as a character-class minimum.
    `0` preserves the historical "no special characters required" behaviour.

- **powerdnsadmin/models/role.py (`__init__`)** - Duplicate `__init__` definitions
  - Two `__init__` methods were defined; the second (`id=None`) shadowed the first,
    dropping `name`/`description` parameters. Collapsed into a single
    `__init__(self, id=None, name=None, description=None)`.

- **routes/domain.py** - Operand order and bare excepts
  - `filter(domain_name == Domain.name)` → `filter(Domain.name == domain_name)`.
  - Bare `except:` in `add()` → `except Exception:`.

- **routes/api.py** - Uninitialized queries / missing validation
  - Replaced non-existent `current_user.get_domain().all()` with `get_user_domains()`.
  - Fixed `api_update_apikey` using an unbound `domain_obj_list`/`None` target list by
    using `target_domains`.
  - Fixed duplicate-zone validation: `len(...) == 0` (always false) →
    `len(...) != len(set(...))` for create and update (accounts too).

- **models/user.py** - `verify_totp` / `create_local_user` hardening
  - `verify_totp` early-returns when there is no secret and wraps the conditional
    UPDATE in try/except rollback.
  - `create_local_user` uses `func.lower(...)` for case-insensitive username/email
    lookups, skips the email-uniqueness check when no email is provided, and wraps
    the commit in `try/except` (handling `IntegrityError`) to avoid swallowed
    duplicates.

- **models/sessions.py** - `datetime.utcnow()` deprecation
  - Replaced with a naive-UTC helper so Flask-Session datetime comparisons keep
    working on Python 3.12+; added throttled expired-session cleanup
    (`clean_up_expired_sessions_if_due`, run from each blueprint `before_request`).

- **models/domain_setting.py (`__repr__`)** - `NameError` when representing a setting
  - The method formatted an undefined local `setting` instead of `self.setting`; now uses
    `self.setting`.

- **routes/index.py (`dyndns_update`)** - Format string with an unused argument
  - The DynDNS success history message passed an extra `str(ip)` argument to `.format()`
    although the template only defines `{0}` and `{1}`. Removed the unused argument
    (resolves F523 / mypy `str-format`).

- **models/role.py & models/user.py (`Role.get_id_by_name`)** - Safe role ID allocation
  - Direct `.id` calls on `Role.query.filter_by(...).first()` raised `AttributeError: 'NoneType' object has no attribute 'id'` if the `role` table had no seeded rows. Added `Role.get_id_by_name(name)` class method to auto-seed default roles (`User`, `Administrator`, `Operator`) if missing, guaranteeing a valid integer ID.

- **routes/index.py (`register`)** - Conditional CAPTCHA check
  - `captcha.validate()` was called unconditionally even when `CAPTCHA_ENABLE` was disabled, causing registration to fail with `Invalid CAPTCHA answer`. Updated guard to `if CAPTCHA_ENABLE and not captcha.validate():`.

- **migrations/env.py & versions/787bdba9e147_init_db.py** - Idempotent DB migrations & Auto-stamping
  - Initial migration `787bdba9e147_init_db.py` checks table existence via SQLAlchemy inspector before creating `account` table.
  - `migrations/env.py` automatically detects pre-created databases without revision metadata and stamps `alembic_version` to head (`d2e3f4a5b6c7`), preventing `table ... already exists` errors during deployment.

- **powerdnsadmin/__init__.py & models/sessions.py** - Flask-Session 0.6+ & Context Processor
  - Bound `SESSION_SQLALCHEMY = models.db` before `Session(app)` and added `__table_args__ = {'extend_existing': True}` to `Sessions` model.
  - Added `@app.context_processor` `inject_pdns_version` so `{{ (pdns_version or '')|tojson }}` in `base.html` never throws `TypeError` / HTTP 500 across all dashboard pages.

- **models/user.py (LDAP group membership)** - Incorrect membership test
  - `not ldap_group in ldap_user_groups` rewritten as `ldap_group not in ldap_user_groups`.

- **models/domain_setting.py (`__eq__`)** - Type comparison style
  - `type(self) == type(other)` rewritten as `type(self) is type(other)`.

### Code Quality / Maintainability

- **Python < 3.12 `distutils` removal**
  - `StrictVersion` (used by `domain.py`/`record.py`/`index.py`/`domain.py`) is
    replaced by a tolerant `version_tuple()` helper (handles `4.9.0-alpha1`,
    `4.7.3-1ubuntu2`, `4.8.0~rc1`). `distutils.util.strtobool` is replaced by a
    local `strtobool()`. No new runtime dependency introduced.
- **Invalid escape sequences** in `models/domain.py` (`get_reverse_domain_name`)
  fixed by using raw strings (tree is clean of `SyntaxWarning` on 3.13).
- **lib/utils.py:30** `type(data) != str` → `isinstance(data, str)`.
- **lib/utils.py:232** removed a stray debug `print`.
- **models/account.py:63** fixed `__repr__` typo `'<Account {0}r>'` → `'<Account {0}>'`.
- **lib/schema.py** removed the unused `key` field from `ApiKeySchema`.
- **default_config.py** `SQLALCHEMY_TRACK_MODIFICATIONS = False`; added
  `SESSION_CLEANUP_N_REQUESTS = 100`.
- **requirements.txt** invalid `name=value` pins (`idna=...`, `pillow=...`,
  `pygments=...`) changed to `==`; pinned `werkzeug==3.0.6` (Flask 2.2.5 still reads
  `werkzeug.__version__`, which 3.1 removed, breaking `flask --version` and the test
  client).
- **docs/oauth.md** Azure scope corrected to `User.Read openid email profile`.
- **Lint (ruff/pyflakes) cleanup** - Removed dead code and silenced false positives
  without changing behaviour:
  - `lib/settings.py` - type comparisons `==` → `is` (`convert_type`); dropped two unused
    `except JSONDecodeError as e` bindings (F841).
  - `lib/utils.py` - renamed ambiguous `ensure_list(l)` parameter to `value` (E741);
    dropped an unused `except Exception as e` binding (F841).
  - `models/domain.py` - dropped an unused `except Exception as e` binding (F841) and four
    redundant local `import urllib.parse` (the module-level import already provides
    `urljoin`/`quote_plus`).
  - `routes/admin.py` - removed unused `from ast import literal_eval` (F401).
  - `routes/api.py` - removed an unused `resp` assignment (F841) and an unused
    `except Exception as e` binding (F841).
  - `routes/base.py` - dropped an unused `except (...) as e` binding (F841).
  - `routes/dashboard.py` - removed unused imports `User`, `History`, `Server` (F401).
  - `routes/index.py` - removed a redundant `OneLogin_Saml2_Utils` import (F401).
  - `models/__init__.py` imports are intentionally kept (they register SQLAlchemy models)
    and are excluded from this cleanup.

### Frontend / Templates

- Unique dropdown `id`/`aria-labelledby` in `admin_manage_user.html`,
  `admin_manage_account.html`, `admin_manage_keys.html`, `dashboard_domain.html` and
  `template.html` (`dropdownMenu-{{ id }}`).
- `user_profile.html` restores the active authentication tab after the OTP toggle
  reloads the page (via `localStorage`).
- `login.html` drops the automatic meta-refresh that discarded unsaved credentials
  and could resubmit a stale CSRF token; expiry is handled server-side.
- `domain.html` record-edit handlers now use `.off('click').on('click', ...)` and
  `link.onclick = ...` to avoid duplicate binding after re-renders.
- `routes/user.py` image-type detection no longer uses the removed `imghdr` module
  (manual magic-byte signatures incl. WebP).

## [0.4.2-alsyundawy-fix] - 2026-08-09

Release by @alsyundawy with frontend security improvements.

### Security Fixes

- **6login.html, 7login.html, 8login.html** - Improved safeSrc function for logo handling
  - Fixed handling of `logo.getAttribute('src')` to prevent potential source URL issues
  - Added URL validation for light theme logo loading

- **register.html** - Added CSP nonce and URL validation
  - Added `nonce="{{ CSP_NONCE|default('') }}"` attribute to script tag
  - Added validation for redirect URLs to prevent javascript:/data: scheme injection

### What's Changed

- Escaping zone name in zones API URL to fully support RFC2317
- Potential fix for code scanning alert: LDAP query built from user-controlled sources
- Potential fix for code scanning alert: Full server-side request forgery
- Potential fix for code scanning alert: Flask app is run in debug mode
- Potential fix for code scanning alert: Reflected server-side cross-site scripting
- Fix: oidc userinfo endpoint

### Dependency Updates

- Bump cryptography: 45.0.5 → 46.0.5 → 48.0.1 → 50.0.0
- Bump pyasn1: 0.6.2 → 0.6.4
- Bump setuptools: 80.9.0 → 83.0.0

## [0.4.2-alsyundawy] - 2026-08-09

This version represents intermediate code analysis and optimizations before comprehensive fixes in 0.4.3-alsyundawy-fix.

## [0.4.2] - 2022-01-31 - Official Release from upstream

### Release Notes from Upstream

This release focused on tying up what loose ends could be within reason in preparation for the freeze release. Following this release, only dependency updates within reason will be managed. There may be additional feature releases on this edition, but nothing is promised.

**POTENTIALLY BREAKING CHANGE** - This release upgrades to SQLAlchemy `1.4.x` which removes support for the use of `postgres://` on database connection URI strings. You must switch to the supported format of `postgresql://` to avoid a failure of the connection.

### Notable Changes from Upstream

- Updated OAuth service providers to properly respect new OAuth auto-configuration settings
- Corrected issue with `SERVER_EXTERNAL_SSL` setting extraction from environment
- Fixed issue with unassigned zones being selected after account name validation fails
- Allow all application settings to be configured by environment variables
- Fix record comment removal
- Automatically focus username field in login view
- Indicate unsaved changes in UI
- Remove miscellaneous code cleanup
- Fix non rr_set events in Zone Changelog display
- Update static fonts to use relative paths
- Fix local user setup for case-insensitive username/email verification
- Update index router to replace deprecated `before_app_first_request` event
- Update zone type comparison logic to be case-insensitive
- Fix zone name encoding for UI XHR requests and PDNS API
- Add LDAP search filter cleansing mechanism for special characters
- Add support for application to run in sub-paths

## [0.4.1] and earlier versions

Previous versions. See GitHub releases for history.

[0.4.2]: https://github.com/PowerDNS-Admin/PowerDNS-Admin/releases/tag/v0.4.2
[0.4.3-alsyundawy]: https://github.com/alsyundawy/PowerDNS-Admin/releases/tag/0.4.3-alsyundawy
[0.4.2-alsyundawy-fix]: https://github.com/alsyundawy/PowerDNS-Admin/compare/0.4.2-alsyundawy...0.4.2-alsyundawy-fix
[0.4.2-alsyundawy]: https://github.com/alsyundawy/PowerDNS-Admin/releases/tag/0.4.2-alsyundawy