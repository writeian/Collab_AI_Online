"""
Structured logs for AI streaming (Redis worker + in-request SSE).

Grep production logs for the prefix ``ai_stream`` then parse the JSON payload.
Tokens are never logged in full—only a short prefix and length.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

_MOD = logging.getLogger(__name__)
_PREFIX = "ai_stream"


def _safe_token_prefix(token: Optional[str], max_prefix: int = 10) -> Optional[str]:
    if not token or not isinstance(token, str):
        return None
    t = token.strip()
    if not t:
        return None
    if len(t) <= max_prefix:
        return t
    return t[:max_prefix] + "…"


def log_ai_stream_event(
    event: str,
    *,
    logger: Optional[logging.Logger] = None,
    token: Optional[str] = None,
    **fields: Any,
) -> None:
    """Emit one line: ``ai_stream {<json>}`` with sorted keys for stable greps."""
    log = logger if logger is not None else _MOD
    payload: dict[str, Any] = {"event": event}
    for key, val in fields.items():
        if val is not None:
            payload[key] = val
    if token is not None:
        payload["stream_token_prefix"] = _safe_token_prefix(token)
        if isinstance(token, str):
            payload["stream_token_len"] = len(token)
    try:
        line = json.dumps(payload, default=str, sort_keys=True)
    except (TypeError, ValueError):
        log.info("%s %s %s", _PREFIX, event, payload)
        return
    log.info("%s %s", _PREFIX, line)
