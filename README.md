# Hours Tracking — Flask (Python)

A port of the ColdBox/CFML hours tracking app, built with Flask and Python.

**Database:** Uses the `hours_tracking` MySQL database.
**URL:** `http://127.0.0.1:8001`
**Login:** `rob.barthle@cf-expert.com` / `admin123`

---

## Prerequisites

- Python 3.12+ (installed via Homebrew)
- `uv` package manager (`/usr/local/bin/uv`)
- MySQL 8 running with the `hours_tracking` database already set up

## Start the Server

```bash
cd /Users/rob/Sites/contract-work/hours-tracking-python
/usr/local/bin/uv run python run.py
```

Then open `http://127.0.0.1:8001` and log in.

Press `Ctrl+C` to stop.

---

## Notes

- `.env` is already configured — no changes needed.
- Dependencies are managed by `uv` and defined in `pyproject.toml`. They are installed automatically on first run.
