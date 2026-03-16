#!/bin/sh
# Railway: PORT may not expand in startCommand; use script to ensure it's set
PORT="${PORT:-8080}"
exec /opt/venv/bin/gunicorn wsgi:app --bind "0.0.0.0:${PORT}" --workers 1 --timeout 180 --preload
