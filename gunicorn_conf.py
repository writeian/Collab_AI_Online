"""Gunicorn runtime config — the single source of truth for server tuning.

Both entry points load this file:
  * Railway:  start.sh -> `gunicorn -c gunicorn_conf.py wsgi:app`
  * Procfile: `web: gunicorn -c gunicorn_conf.py wsgi:app`

Every value below is overridable via a Railway/environment variable, so there is
no second place to edit. Defaults target ~20 simultaneous users and match the
configuration that was previously hard-coded in start.sh.
"""

from __future__ import annotations

import os


def _int_env(name: str, default: int, minimum: int = 1) -> int:
    raw = os.getenv(name)
    try:
        value = int(raw) if raw is not None else int(default)
    except (TypeError, ValueError):
        value = int(default)
    return max(minimum, value)


bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
worker_class = (os.getenv("GUNICORN_WORKER_CLASS", "gthread") or "gthread").strip()
workers = _int_env("GUNICORN_WORKERS", 3, minimum=1)

# NOTE: with gthread workers this `timeout` is the worker *heartbeat* timeout, not a
# per-request kill — a long streaming AI reply keeps the worker heart-beating, so it is
# not cut off. It only reaps a worker whose process has genuinely stalled. Lowering it to
# bound a stuck request only makes sense once AI work moves off the request thread (R2);
# until then keep it generous so streaming completions are never truncated.
timeout = _int_env("GUNICORN_TIMEOUT", 300, minimum=30)
graceful_timeout = _int_env("GUNICORN_GRACEFUL_TIMEOUT", 60, minimum=10)
keepalive = _int_env("GUNICORN_KEEPALIVE", 2, minimum=1)

# Do not use --preload with forked workers + SQLAlchemy PostgreSQL
# (connections created pre-fork go stale in the children).
preload_app = False

# Worker-type specific settings
if worker_class == "gthread":
    threads = _int_env("GUNICORN_THREADS", 8, minimum=1)
elif worker_class in {"gevent", "eventlet"}:
    worker_connections = _int_env("GUNICORN_WORKER_CONNECTIONS", 1000, minimum=100)
