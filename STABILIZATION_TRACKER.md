# Stabilization Tracker

Tracking the "make the app better before adding features" work.

- **Branch:** `stabilization` (off `updated-edu-tools`, the deployed branch — do NOT commit to `updated-edu-tools` directly)
- **Base commit:** `aff4668`
- **Started:** 2026-08-07
- **Source:** security audit + reliability/performance pass of the deployed branch
- **Goal:** app is reliable + fast for a class of students before new features are added

## How to use this file

Each item has: **Issue** (what's wrong), **Fix** (the plan), **Implementation** (filled in when done — what was actually changed), and **Files** (where the change lives). Update the **Status** as you go.

**Status key:** ⬜ Not started · 🟡 In progress · ✅ Done · ⏸️ Blocked / needs you

---

## Summary

| ID | Priority | Area | Issue (short) | Week | Status |
|----|----------|------|---------------|------|--------|
| R1 | 🔴 Critical | Performance | Live AI call on every page render (modes) | 1 | ⬜ |
| S1 | 🔴 Critical | Security | Leaked DB password in git history + committed doc | 1 | ⏸️ |
| S2 | 🟠 High | Security | `SECRET_KEY` hardcoded fallback, not enforced | 1 | ⬜ |
| S3 | 🟠 High | Security | Stored XSS in admin password-reset page | 1 | ⬜ |
| R7 | 🟠 High | Reliability | Broken migrations; schema hand-patched every boot | 1 | ⬜ |
| R8 | 🟠 High | Observability | No error monitoring — failures are invisible | 1 | ⬜ |
| S4 | 🟡 Medium | Security | Unauthenticated diagnostic/info endpoints | 1 | ⬜ |
| R2 | 🟠 High | Performance | Synchronous AI calls block request threads | 2 | ⬜ |
| R3 | 🟠 High | Reliability | DB connection pool can exceed Railway's limit | 2 | ⬜ |
| R4 | 🟠 High | Reliability | Transaction poisoning → intermittent 500s | 2 | ⬜ |
| R5 | 🟡 Medium | Performance | N+1 queries on dashboard / member lists | 2 | ⬜ |
| R6 | 🟡 Medium | Config | Dead gunicorn config, 300s timeout, hot-path logging | 2 | ⬜ |
| S5 | 🟡 Medium | Security | Account enumeration (register + forgot-password) | 3 | ⬜ |
| S6 | 🟡 Medium | Security | Password-reset token logged to server output | 3 | ⬜ |
| S7 | 🟡 Medium | Security | Weak password policy (6 chars, no checks) | 3 | ⬜ |
| S8 | 🟢 Low | Security | Whole library blueprint is CSRF-exempt | 3 | ⬜ |
| S9 | 🟢 Low | Cleanup | Committed virtualenvs (`.venv/`, `.venv311/`) | 3 | ⬜ |
| S10 | 🟢 Low | Security | Upload decompression-bomb DoS; no body size cap | 3 | ⬜ |
| S11 | 🟢 Low | Security | CSP allows `unsafe-inline` / `unsafe-eval` | 3 | ⬜ |
| S12 | 🟢 Low | Security | Deactivated user keeps an active session | 3 | ⬜ |

---

## Week 1 — See it & stop the bleeding

### R1 — Live AI call on every page render (modes) 🔴 ⬜
- **Issue:** When a chat/room page renders, `get_modes_for_room()` runs, and for a room that has learning goals but no saved modes it calls the model synchronously (with provider failover) *during the page load*. Result: 5–30s page loads, and hangs/failures when the model is slow, rate-limited, or errors. This is the most visible "slow / breaks."
- **Fix:** Generate a room's modes once (at room creation / when goals change) and persist them (as `CustomPrompt` rows or a cached column). Make `get_modes_for_room()` a pure database read that returns instantly, with a template fallback if modes aren't generated yet. No model call on any GET render.
- **Implementation:** _pending_
- **Files:** `src/utils/openai_utils.py` (`get_modes_for_room` ~L406, `generate_room_modes` ~L238); call sites `src/app/chat.py:606,795`, `src/app/room/routes/crud.py:224,660`, `src/app/room/__init__.py:169`, `src/app/dashboard.py:131`, `src/app/achievements.py:114,235`; persistence via `src/models/custom_prompt.py`.

### S1 — Leaked DB password in git history + committed doc 🔴 ⏸️
- **Issue:** A real Railway Postgres password was committed in `a0ff8ca` and is still reachable in git history; it's also printed in plaintext inside `SECURITY_INCIDENT_2025-11-27.md`. A later commit says "password rotated."
- **Fix:** (1) Confirm in the Railway dashboard that the password was actually rotated — **needs you**. (2) Redact the plaintext from the incident doc. (3) Purge it from history with `git filter-repo` / BFG.
- **Implementation:** _pending_
- **Files:** `SECURITY_INCIDENT_2025-11-27.md`; full git history (rewrite); Railway dashboard (rotation).

### S2 — `SECRET_KEY` hardcoded fallback, not enforced 🟠 ⬜
- **Issue:** `SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"`. If the env var is ever missing in production, sessions are signed with a key that's public in the repo → forgeable sessions / auth bypass.
- **Fix:** In production, fail fast at startup if `SECRET_KEY` is unset instead of falling back to the hardcoded default.
- **Implementation:** _pending_
- **Files:** `src/config/settings.py:23` (and `ProductionConfig.init_app`).

### S3 — Stored XSS in admin password-reset page 🟠 ⬜
- **Issue:** The reset page builds an HTML message via f-string containing user-controlled `display_name` / `username` / `email`, then renders it with `{{ message|safe }}`. A user who registers with a `<script>` display name executes JS in the admin's browser when that user's password is reset.
- **Fix:** Escape the values (drop `|safe`, or build the message with escaping). Do not render user-controlled strings as raw HTML.
- **Implementation:** _pending_
- **Files:** `src/app/admin_password_reset.py` (template `~L38`, message build `~L110–136`).

### R7 — Broken migrations; schema hand-patched every boot 🟠 ⬜
- **Issue:** Alembic migrations aren't clean, so on every startup the app runs a large block of manual `CREATE TABLE` / `ALTER TABLE` statements to patch the schema. Fragile; a bad deploy can leave a half-built table.
- **Fix:** Get Alembic to `head` reliably, make migrations idempotent, and remove the manual DDL from startup once migrations own the schema.
- **Implementation:** _pending_
- **Files:** `src/main.py:33–531` (`run_production_migrations` + manual DDL), `src/app/__init__.py:162–253` (document-table DDL), `migrations/`, `alembic.ini`.

### R8 — No error monitoring (failures are invisible) 🟠 ⬜
- **Issue:** The app swallows many errors (`try/except → print → continue`), so crashes students hit are never seen. You can't fix "it breaks" without watching it break.
- **Fix:** Add error monitoring (e.g., Sentry free tier) so every unhandled error is captured with a stack trace and request context.
- **Implementation:** _pending_
- **Files:** `src/app/__init__.py` (init in the factory), `requirements.txt`, env var for the DSN.

### S4 — Unauthenticated diagnostic/info endpoints 🟡 ⬜
- **Issue:** `/routes` (full URL map), `/metrics` (live user/room/message counts), `/version`, `/__tpl`, `/__tpl_base`, `/__static_check`, `/__landing_assets_check` are all public.
- **Fix:** Gate behind `@require_admin` or remove them in production.
- **Implementation:** _pending_
- **Files:** `src/main.py` (`/routes` ~L669, `/version` ~L686); `src/app/__init__.py` (`/metrics` ~L491, `/__tpl` ~L428, `/__tpl_base` ~L440, `/__static_check` ~L536, `/__landing_assets_check` ~L648).

---

## Week 2 — Make the core loop survive the class

### R2 — Synchronous AI calls block request threads 🟠 ⬜
- **Issue:** Some actions call the model in-request, holding one of ~24 server threads (3 workers × 8) for the whole call: message-send fallback (`sync_blocking`), "continue generating", and Google-Doc import on chat creation. Under a class this starves the thread pool → slow, then 5-minute timeouts → 500s.
- **Fix:** Route all model calls through the existing Redis + rq worker; make any in-request AI optional and time-boxed. Keep graceful fallback but stop masking errors with a canned greeting.
- **Implementation:** _pending_
- **Files:** `src/app/chat.py:434,440` (sync fallback), `:1291` (continue), `src/app/room/routes/crud.py:639` (doc import), `src/app/api/card_comments.py:331`; worker `src/workers/ai_reply_job.py`.

### R3 — DB connection pool can exceed Railway's limit 🟠 ⬜
- **Issue:** Each worker holds up to 22 connections (pool 10 + overflow 12); ×3 workers + the background worker ≈ 70+, likely above the Postgres plan's `max_connections` → "too many connections" under load.
- **Fix:** Check the Postgres plan's `max_connections` and set `DB_POOL_SIZE` / `DB_POOL_MAX_OVERFLOW` so `workers × (pool + overflow)` stays comfortably under it.
- **Implementation:** _pending_
- **Files:** `src/config/settings.py:40–46`; env vars on Railway; `start.sh` (worker count).

### R4 — Transaction poisoning → intermittent 500s 🟠 ⬜
- **Issue:** Swallowed exceptions after a DB write without a rollback leave the pooled connection in a failed state; the next request to reuse it errors ("current transaction is aborted") — intermittent, hard to reproduce, clears on restart. (Evidence: reactive rollback patches across many files; the `InFailedSqlTransaction` fix in `library/upload.py`.)
- **Fix:** Roll back in every `except` around a DB write; add a `teardown_request`/`teardown_appcontext` that rolls back a dirty session so no bad connection is returned to the pool.
- **Implementation:** _pending_
- **Files:** `src/app/__init__.py` (add teardown; 500 handler rollback exists ~L714); swallow-and-continue sites in `src/app/chat.py`, `src/app/dashboard.py`, `src/app/room/**`, others.

### R5 — N+1 queries on dashboard / member lists 🟡 ⬜
- **Issue:** Member rendering runs one query per member (`[User.query.get(m.user_id) for m in members]`); the dashboard runs several count queries per room in a loop. Sluggish at class scale.
- **Fix:** Batch with `User.query.filter(User.id.in_(ids))` and grouped aggregate counts.
- **Implementation:** _pending_
- **Files:** `src/app/dashboard.py:294` (and per-room count loop ~L?), `src/app/room/services/room_service.py:360`.

### R6 — Config footguns: dead gunicorn config, timeout, hot-path logging 🟡 ⬜
- **Issue:** Railway starts via `start.sh`, which ignores `gunicorn_conf.py` (two disagreeing config sources). The 300s timeout lets a hung call tie up a thread for 5 minutes. `require_room_access` logs several ERROR lines on every room visit.
- **Fix:** Consolidate to one gunicorn config; lower the request timeout (with AI work moved off-request per R2); drop the per-request ERROR logs to debug.
- **Implementation:** _pending_
- **Files:** `start.sh`, `gunicorn_conf.py`, `railway.toml`, `Procfile`; `src/app/access_control.py:262–292` (logging).

---

## Week 3 — Smooth it & harden

### S5 — Account enumeration 🟡 ⬜
- **Issue:** Registration ("Username already exists" / "Email already registered") and forgot-password (different message when the email exists vs. not) let an attacker enumerate valid accounts.
- **Fix:** Make responses uniform (generic success/failure).
- **Implementation:** _pending_
- **Files:** `src/app/auth.py` (register `:88,107`; forgot-password `:343` vs `:381–385`).

### S6 — Password-reset token logged to server output 🟡 ⬜
- **Issue:** When email send fails / SMTP isn't configured, the full reset URL and token are printed to stdout (retained in Railway logs).
- **Fix:** Never log the token; confirm SMTP is configured in production.
- **Implementation:** _pending_
- **Files:** `src/app/auth.py:369–379`; email config `src/utils/email.py`.

### S7 — Weak password policy 🟡 ⬜
- **Issue:** 6-character minimum, no complexity, across register / reset / change.
- **Fix:** Raise the minimum and add basic strength checks.
- **Implementation:** _pending_
- **Files:** `src/app/auth.py:192` (register), `:412` (reset), `:562` (change).

### S8 — Library blueprint is fully CSRF-exempt 🟢 ⬜
- **Issue:** `csrf.exempt(library)` covers the whole blueprint. JSON endpoints are shielded by content-type/CORS, but `/upload` (multipart) is realistically CSRF-able (minor impact).
- **Fix:** Scope the exemption; require a custom header / token on state-changing endpoints.
- **Implementation:** _pending_
- **Files:** `src/app/__init__.py:404`; `src/app/library/**`.

### S9 — Committed virtualenvs 🟢 ⬜
- **Issue:** `.venv/` and `.venv311/` are committed (bloat); `.gitignore` only lists `venv/`.
- **Fix:** `git rm -r --cached .venv .venv311` and add `.venv*/` to `.gitignore`.
- **Implementation:** _pending_
- **Files:** `.gitignore`, `.venv/`, `.venv311/`.

### S10 — Upload decompression-bomb DoS; no body size cap 🟢 ⬜
- **Issue:** Uploaded PDFs/DOCX (≤10MB) are text-extracted in memory; a decompression bomb could OOM the single worker. No Flask `MAX_CONTENT_LENGTH`.
- **Fix:** Add extraction limits/timeouts and a global `MAX_CONTENT_LENGTH`.
- **Implementation:** _pending_
- **Files:** `src/app/library/upload.py`, `src/utils/documents/extract_text.py`, `src/config/settings.py`.

### S11 — CSP allows `unsafe-inline` / `unsafe-eval` 🟢 ⬜
- **Issue:** Script CSP includes `unsafe-inline` and `unsafe-eval`, weakening XSS defense (mitigated today by the escaping markdown filter).
- **Fix:** Tighten the script policy where the frontend allows.
- **Implementation:** _pending_
- **Files:** `src/app/__init__.py:305`.

### S12 — Deactivated user keeps active session 🟢 ⬜
- **Issue:** `is_active` is only checked at login; a deactivated user with an existing session stays logged in.
- **Fix:** Reject inactive users in `get_current_user()`.
- **Implementation:** _pending_
- **Files:** `src/app/access_control.py:17–21`.

---

## Also planned (not code fixes — Week 3 wrap-up)

- Staging/preview environment so changes are tested before students see them.
- Test suite green and running in CI against `updated-edu-tools`.
- A real README/architecture doc for the deployed branch.
- Delete dead branches and stray files so the repo matches reality.
