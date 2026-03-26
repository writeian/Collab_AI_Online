#!/bin/sh
# Railway: PORT may not expand in startCommand; use script to ensure it's set.
#
# Concurrency (tuned for ~20 simultaneous users):
# - gthread: multiple requests per worker process (polling + LLM without head-of-line blocking).
# - Override via env if Railway plan is memory-constrained: GUNICORN_WORKERS=2 GUNICORN_THREADS=6
#
# Do not use --preload with forked workers + SQLAlchemy PostgreSQL (stale connections post-fork).
PORT="${PORT:-8080}"
WORKERS="${GUNICORN_WORKERS:-3}"
THREADS="${GUNICORN_THREADS:-8}"

exec /opt/venv/bin/gunicorn wsgi:app \
  --bind "0.0.0.0:${PORT}" \
  -k gthread \
  --workers "${WORKERS}" \
  --threads "${THREADS}" \
  --timeout 300 \
  --graceful-timeout 60
