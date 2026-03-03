# Hours Tracking App — Flask (Python)

A port of the ColdBox/CFML hours tracking app, built with Flask. Intended as a training/learning tool — same features, same database, same MVCS architecture as the original.

## Tech Stack
- Flask 3.1.3, Python 3.14+, MySQL 8 (via PyMySQL), Bootstrap 5 + Alpine.js
- Server: `/usr/local/bin/uv run python run.py` at http://127.0.0.1:8001
- DB: `hours_tracking`, user `cfuser`, password `cfpassword`
- Package manager: `uv` (at `/usr/local/bin/uv`)

## Commands
```bash
/usr/local/bin/uv run python run.py    # start dev server (auto-installs deps)
```

## Default Login
- Email: `rob.barthle@cf-expert.com`
- Password: `admin123`

## Architecture
- **Blueprints** — one per resource in `app/blueprints/`; equivalent to ColdBox handlers or Laravel controllers
- **Services** — all business logic and SQL in `app/services/`; instantiated at module level in each blueprint
- **DB layer** — raw PyMySQL in `app/db.py`; helpers: `query()`, `query_one()`, `execute()`, `execute_in_transaction()`
- **Auth** — decorators `@login_required`, `@admin_required` in `app/auth.py`; session-based via `session['user']`
- **Helpers** — template filters/globals in `app/helpers.py`; registered via `register_helpers(app)` in app factory
- **Templates** — Jinja2 in `templates/`, organized by feature; `base.html` is the layout

## Code Style
- snake_case modules and methods; PascalCase classes
- Blueprint naming: `<resource>_bp` (e.g., `invoices_bp`)
- Service methods: `list()`, `get()`, `create()`, `update()`, `delete()`
- Raw SQL with `%s` placeholders — no ORM
- Session auth: `session['user']` contains `id`, `email`, `first_name`, `last_name`, `role`

## Key Gotchas
- **No BCrypt** — uses SHA-512 with per-user salt to match the original ColdBox app: `hashlib.sha512((salt + password).encode()).hexdigest().upper()` — note: **salt first**, then password
- **HTTP method spoofing** — forms use `<input type="hidden" name="_method" value="PUT">` and blueprints check `request.form.get('_method', '').upper()`
- **Transaction pattern** — `execute_in_transaction(ops)` takes a callback `ops(conn, cur)` and handles commit/rollback
- **Jinja2 loop mutation** — use `{% set ns = namespace(val='') %}` with `{% set ns.val = x %}` to mutate variables inside loops
- **`timedelta` in templates** — injected via context processor in `app/__init__.py`; use `now + timedelta(days=30)` in templates
- **No migrations needed** — shares the `hours_tracking` database with the ColdBox and Laravel apps; data already exists
- **Trailing slash routes** — Flask registers routes as `/clients/`; requests to `/clients` get a 308 redirect automatically

## Testing
- No test suite yet.
