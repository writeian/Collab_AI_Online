"""Gunicorn runtime config with safe defaults for streaming-heavy chat workloads."""

from __future__ import annotations

import os


def _int_env(name: str, default: int, minimum: int = 1) -> int:
    raw = os.getenv(name)
    try:
        value = int(raw) if raw is not None else int(default)
    except (TypeError, ValueError):
        value = int(default)
    return max(minimum, value)


bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
worker_class = (os.getenv("GUNICORN_WORKER_CLASS", "gthread") or "gthread").strip()
workers = _int_env("GUNICORN_WORKERS", 3, minimum=1)
timeout = _int_env("GUNICORN_TIMEOUT", 300, minimum=30)
graceful_timeout = _int_env("GUNICORN_GRACEFUL_TIMEOUT", 30, minimum=10)
keepalive = _int_env("GUNICORN_KEEPALIVE", 5, minimum=1)

# Worker-type specific settings
if worker_class == "gthread":
    threads = _int_env("GUNICORN_THREADS", 12, minimum=1)
elif worker_class in {"gevent", "eventlet"}:
    worker_connections = _int_env("GUNICORN_WORKER_CONNECTIONS", 1000, minimum=100)
