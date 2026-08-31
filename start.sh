#!/bin/sh
# Railway start command (railway.toml -> startCommand = "sh start.sh").
#
# All gunicorn tuning lives in ONE place: gunicorn_conf.py (every knob is
# env-overridable, e.g. GUNICORN_WORKERS / GUNICORN_THREADS / GUNICORN_TIMEOUT).
# This script only guarantees PORT is exported for that config to bind, then
# hands off. To change concurrency on a memory-constrained plan, set the env
# vars in Railway — do not add flags here.
export PORT="${PORT:-8080}"

exec /opt/venv/bin/gunicorn -c gunicorn_conf.py wsgi:app
