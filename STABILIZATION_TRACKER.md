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
| R1 | 🔴 Critical | Performance | Live AI call on every page render (modes) | 1 | ✅ |
| S1 | 🔴 Critical | Security | Leaked DB password in git history + committed doc | 1 | ⏸️ |
| S2 | 🟠 High | Security | `SECRET_KEY` hardcoded fallback, not enforced | 1 | ✅ |
| S3 | 🟠 High | Security | Stored XSS in admin password-reset page | 1 | ✅ |
| R7 | 🟠 High | Reliability | Broken migrations; schema hand-patched every boot | 1 | ✅ |
| R8 | 🟠 High | Observability | No error monitoring — failures are invisible | 1 | ✅ |
| S4 | 🟡 Medium | Security | Unauthenticated diagnostic/info endpoints | 1 | ✅ |
| R2 | 🟠 High | Performance | Synchronous AI calls block request threads | 2 | ⬜ |
| R3 | 🟠 High | Reliability | DB connection pool can exceed Railway's limit | 2 | ⬜ |
| R4 | 🟠 High | Reliability | Transaction poisoning → intermittent 500s | 2 | ✅ |
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

### R1 — Live AI call on every page render (modes) 🔴 ✅
- **Issue:** When a chat/room page renders, `get_modes_for_room()` runs, and for a room that has learning goals but no saved modes it calls the model synchronously (with provider failover) *during the page load*. Result: 5–30s page loads, and hangs/failures when the model is slow, rate-limited, or errors. This is the most visible "slow / breaks."
- **Fix:** Generate a room's modes once (at room creation / when goals change) and persist them (as `CustomPrompt` rows or a cached column). Make `get_modes_for_room()` a pure database read that returns instantly, with a template fallback if modes aren't generated yet. No model call on any GET render.
- **Implementation:** `get_modes_for_room()` no longer calls the model on the render path. It returns saved `CustomPrompt` modes if present, else an **instant** template fallback (new `_instant_fallback_modes()`, which infers a template or uses `academic_essay` base modes). When a room has goals but no saved modes, it best-effort enqueues a one-time background job to generate + persist tailored modes, so they appear on a later load. Added `src/workers/mode_backfill_job.py` — runs on the existing `ai_replies` rq queue, is idempotent (skips if modes already exist / on unique-constraint race), and is guarded by a Redis key so a room enqueues at most once per 15 min. If Redis/worker is unavailable, the room simply keeps the instant template modes (no error, no block). `generate_room_modes()` and the creation-time callers are unchanged (creation-time generation is separate — see R2). **Verification:** syntax-checked with `py_compile`; **runtime-verified locally 2026-08-20** on a fresh Python 3.11 venv (both prior venvs were dead cross-machine copies). Drove a real login (`test123`) + room render via the Flask test client with spies on all four model-call paths (`generate_room_modes`, `call_anthropic_api`, `call_anthropic_api_stream`, `call_openai_api`). **Both branches confirmed zero model calls:** (a) room with 5 saved modes rendered in **47 ms**; (b) a throwaway room with goals-but-no-saved-modes rendered in **50 ms** and correctly *scheduled* the background backfill instead of generating inline (enqueue no-ops without `REDIS_URL`, as designed). Backfill upgrade path (Redis + rq worker producing tailored modes on a later load) still unexercised locally — needs Redis, deferred pending the professor's keys.
- **Files:** `src/utils/openai_utils.py` (`get_modes_for_room` made render-safe + new `_instant_fallback_modes`, ~L406); **new** `src/workers/mode_backfill_job.py`. Render call sites now fast automatically: `src/app/chat.py:606,795`, `src/app/room/routes/crud.py:224,660`, `src/app/room/__init__.py:169`, `src/app/dashboard.py:131`, `src/app/achievements.py:114,235`.

### S1 — Leaked DB password in git history + committed doc 🔴 ⏸️
- **Issue:** A real Railway Postgres password was committed in `a0ff8ca` and is still reachable in git history; it's also printed in plaintext inside `SECURITY_INCIDENT_2025-11-27.md`. A later commit says "password rotated."
- **Fix:** (1) Confirm in the Railway dashboard that the password was actually rotated — **needs you**. (2) Redact the plaintext from the incident doc. (3) Purge it from history with `git filter-repo` / BFG.
- **Implementation:** _pending_
- **Files:** `SECURITY_INCIDENT_2025-11-27.md`; full git history (rewrite); Railway dashboard (rotation).

### S2 — `SECRET_KEY` hardcoded fallback, not enforced 🟠 ✅
- **Issue:** `SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"`. If the env var is ever missing in production, sessions are signed with a key that's public in the repo → forgeable sessions / auth bypass.
- **Fix:** In production, fail fast at startup if `SECRET_KEY` is unset instead of falling back to the hardcoded default.
- **Implementation:** The insecure default is now the named module constant `DEV_FALLBACK_SECRET_KEY`; the base `Config` still falls back to it so **local dev/testing keep working with no env var set**. `ProductionConfig.init_app()` (which `create_app()` calls at startup only when `FLASK_ENV=production`) now raises `RuntimeError` if the effective `SECRET_KEY` is missing, empty/whitespace, or equal to that default — halting boot with a message telling you to set a strong key (`python -c "import secrets; print(secrets.token_hex(32))"`). Development is unaffected (it uses the base no-op `init_app`). **Verification:** `py_compile` clean; guard unit-tested in isolation — default/empty/blank keys are blocked, a strong key starts. Runtime confirmation on Railway happens naturally (a bad deploy fails loudly instead of silently using the public key).
- **Files:** `src/config/settings.py` (new `DEV_FALLBACK_SECRET_KEY` constant ~L19; `Config.SECRET_KEY` ~L26; guard in `ProductionConfig.init_app` ~L203).

### S3 — Stored XSS in admin password-reset page 🟠 ✅
- **Issue:** The reset page builds an HTML message via f-string containing user-controlled `display_name` / `username` / `email`, then renders it with `{{ message|safe }}`. A user who registers with a `<script>` display name executes JS in the admin's browser when that user's password is reset.
- **Fix:** Escape the values (drop `|safe`, or build the message with escaping). Do not render user-controlled strings as raw HTML.
- **Implementation:** Dropped `|safe` — the template now renders `{{ message }}`, which Flask 3.1.1 auto-escapes (`render_template_string` → `select_jinja_autoescape(None)` returns `True`, **verified empirically**). The success message is now built with `markupsafe.Markup("""…{display_name}…""").format(email=…, username=…, display_name=…, password=…)`: the intended `<strong>`/`<br>`/`<pre>`/`<code>` formatting stays as trusted markup while **every interpolated user value is escaped** (a `<script>` display name renders as inert `&lt;script&gt;`). Error messages remain plain strings and are auto-escaped by the template. Form fields (`{{ email }}`, `{{ suggested_password }}`) were already safe (auto-escaped). **Verification:** `py_compile` clean; no `|safe` remains; escaping confirmed against real `markupsafe==3.0.2` (user value escaped, intended markup preserved) and real `flask==3.1.1` (error-path string auto-escaped).
- **Files:** `src/app/admin_password_reset.py` (import of `Markup`; template `{{ message }}` ~L39; message build via `Markup(...).format(...)` ~L111–140).

### R7 — Broken migrations; schema hand-patched every boot 🟠 ✅ (pragmatic reconciler; full migration rehab deferred)
- **Issue:** Alembic migrations aren't clean, so on every startup the app runs a large block of manual `CREATE TABLE` / `ALTER TABLE` statements to patch the schema. Fragile; a bad deploy can leave a half-built table. **Confirmed reproducible drift (2026-08-20, local run):** loading/deleting a `document` row crashed with `sqlite3.OperationalError: no such column: document.key_document_type` (hit while cascade-deleting a room; would also break the Library tool). **Root cause, fully diagnosed:** (1) **15 of 17 migrations are Postgres-only** — they gate on `information_schema`, so `alembic upgrade head` crashes on the first one on SQLite → the local DB is **never stamped** (no `alembic_version` table) and Alembic never owns it. (2) `db.create_all()` only creates missing *tables*, never adds columns to existing ones. (3) **`src/models/__init__.py` never imports `document.py`**, so the `Document`/`DocumentChunk` models aren't registered in `db.metadata` when `create_all()` runs — which is the very reason those tables are hand-created in raw SQL, and the raw SQL's column list had fallen behind the model (missing `key_document_type`). Note: `document_chunk.search_vector` is `postgresql.TSVECTOR` — **Postgres-only**, so its absence on SQLite is expected, not a bug.
- **Fix (chosen scope — pragmatic reconciler):** Add one dialect-aware, additive-only schema reconciler that runs at boot after `create_all()`, so model↔schema drift can't silently recur. Deferred by explicit decision: rewriting the 15 Postgres-only migrations to be dialect-agnostic, stamping the DBs, and deleting the boot-time hand-DDL (the "correct" end-state, but 15-file surgery with real risk to the working prod path — a calmer Week-3/post-class task).
- **Implementation:** New `_reconcile_missing_columns(app, db)` in the app factory, called right after the document-table block inside `create_app`'s `with app.app_context()`. It first imports **all** modules under `src/models` (so tables like `document`/`document_chunk` that `__init__` omits get registered in `db.metadata`) — done *after* `create_all()` on purpose, because registering the document models earlier would make `create_all()` try to emit their Postgres-only `TSVECTOR` on SQLite and fail. It then compares every mapped table to the live schema via the SQLAlchemy inspector and `ALTER TABLE … ADD COLUMN`s anything missing. Deliberately conservative: additive only (never drops/alters), skips brand-new tables (`create_all` owns those), **skips column types the dialect can't compile** (e.g. `TSVECTOR` on SQLite — logged and left alone), adds every reconciled column **NULLABLE** (safe for tables with existing rows) and warns when the model wanted NOT NULL so a real migration can still enforce it. Wrapped so it can **never crash startup**. Runs on both SQLite (fixes local drift incl. `key_document_type`) and Postgres (safety net). The existing `run_production_migrations` PHASE DDL is left in place for now (harmless where it works); the reconciler now supersedes its column-adding role and those phases can be retired once confirmed redundant. `src/models/__init__.py` was intentionally **not** changed to export the document models (that would break `create_all()` on SQLite as above).
- **Verification (2026-08-20, local, fresh venv):** py_compile clean. On a throwaway SQLite DB seeded with a `document` table missing `key_document_type`, boot **adds exactly that column and skips `search_vector`** (`reconcile: added 1 missing column(s): document.key_document_type`; `reconcile: skipping document_chunk.search_vector — TSVECTOR not supported on sqlite`). The original crash is gone: cascade-deleting a room now succeeds. **Idempotent** — a second reconcile adds nothing; column present exactly once. Full-app regression clean: `DB_INIT_STATUS=success`, `/health`=200, S4 `/metrics` still 302→login. Drift scan on the real dev DB now shows only the expected `document_chunk.search_vector` (Postgres-only). Scripts: `scratchpad/boottest_r7.py`, `verify_r7.py`, `idempotency_r7.py`, `cleanup_and_drift.py`.
- **Files:** `src/app/__init__.py` (**new** `_reconcile_missing_columns` ~L186; call site inside `create_app` after the document-table block). Deferred-work files (unchanged): `src/main.py` (`run_production_migrations` + PHASE DDL), the 15 Postgres-only files in `migrations/versions/`, `alembic.ini`.

### R8 — No error monitoring (failures are invisible) 🟠 ✅ (code done; set `SENTRY_DSN` to activate)
- **Issue:** The app swallows many errors (`try/except → print → continue`), so crashes students hit are never seen. You can't fix "it breaks" without watching it break.
- **Fix:** Add error monitoring (e.g., Sentry free tier) so every unhandled error is captured with a stack trace and request context.
- **Implementation:** Added `_init_sentry(app)` in the app factory, called right after config load. It is **dormant by default**: with no `SENTRY_DSN` set (local dev, or before a Sentry project exists) it is a no-op and the app runs normally. Set the `SENTRY_DSN` env var to turn on capture — no code change needed. Uses the Sentry `FlaskIntegration`, so unhandled exceptions (the 500s students hit) are captured automatically with stack trace + request context. Privacy-conscious defaults: `send_default_pii=False` (no cookies/bodies/student PII shipped) and `traces_sample_rate=0.0` (errors only, no perf tracing — free-tier friendly); both, plus `environment`/`release`, are env-tunable. Fully defensive: if `SENTRY_DSN` is set but the SDK isn't installed, or init fails, it logs a warning and the app still starts. A module-level guard prevents double-init when a worker reuses `create_app()`. **Activation (your 2-min step):** create a free project at https://sentry.io (Python/Flask), copy its DSN into `SENTRY_DSN` (Railway env var + local `.env`), redeploy. **Verification:** both files `py_compile` clean; validated against real `sentry-sdk 2.68.0` that the `FlaskIntegration` import path and the exact `init(...)` kwargs are accepted.
- **Files:** `src/app/__init__.py` (`_init_sentry` helper + call in `create_app`); `src/config/settings.py` (`SENTRY_DSN`/`SENTRY_ENVIRONMENT`/`SENTRY_RELEASE`/`SENTRY_TRACES_SAMPLE_RATE`); `requirements.txt` (`sentry-sdk[flask]>=2.14.0`); `env_template.txt` (documented `SENTRY_DSN`).

### S4 — Unauthenticated diagnostic/info endpoints 🟡 ✅
- **Issue:** `/routes` (full URL map), `/metrics` (live user/room/message counts), `/version`, `/__tpl`, `/__tpl_base`, `/__static_check`, `/__landing_assets_check` are all public.
- **Fix:** Gate behind `@require_admin` or remove them in production.
- **Implementation:** Added `@require_admin` to all seven endpoints (kept them available to admins for debugging rather than deleting). In `main.py`, `require_admin` is imported at module level (safe: `src.app` is already loaded by then). In `src/app/__init__.py` the import is **function-level inside `create_app`** to avoid the circular import (`access_control` imports from this package). `require_admin` uses the `ADMIN_EMAILS` allowlist and fails closed — non-admins/anonymous get a redirect (or 403 for JSON `Accept`), so no data leaks. Public routes untouched: `/health` and the readiness probe stay open (Railway health checks), as do `/`, `/about`, `/landing`, and the CSS/asset-serving routes. **Caveat:** to *use* these endpoints in prod as an admin, `ADMIN_EMAILS` must be set on Railway (already required by the admin password-reset page). If any external uptime monitor was pointed at `/metrics`, repoint it to `/health`. **Verification:** both files `py_compile` clean; grep-confirmed all 7 gated and the public routes not gated.
- **Files:** `src/main.py` (import + `/routes` ~L670, `/version` ~L688); `src/app/__init__.py` (function-level `require_admin` import ~L487; `/__tpl` ~L492, `/__tpl_base` ~L505, `/metrics` ~L557, `/__static_check` ~L603, `/__landing_assets_check` ~L716).

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

### R4 — Transaction poisoning → intermittent 500s 🟠 ✅ (core loop; broader audit deferred)
- **Issue:** Swallowed exceptions after a DB operation without a rollback leave the session's transaction **aborted**; on Postgres every subsequent query in that request errors with "current transaction is aborted" → intermittent 500s that clear on restart. **Confirmed in the core page (`view_chat`):** the render does a *sequence* of best-effort queries (comments, pin metadata, room chats) each wrapped in `except → log → set empty → continue` with **no rollback** — the comments one even says "likely pending migration" (i.e. it fails on schema drift). One failed query there poisons the session and cascades every later query in the render into a 500.
- **Fix:** Roll back in the `except` at each swallow-and-continue-after-DB-op site so the session recovers within the request; add a `teardown_request` safety net so a request that ends in an exception never returns a poisoned connection to the pool. (Cross-request is already largely covered: `db` is standard Flask-SQLAlchemy — its `session.remove()` at app-context teardown rolls back — and prod has `pool_pre_ping=True`.)
- **Implementation:** Added `db.session.rollback()` to the 7 swallow sites in the core loop `src/app/chat.py`: the message-send path (auto-note trigger, mode-suggestion block) and the `view_chat` render cascade (comments, pin metadata, room chats) and the in-request SSE stream (persist failure, note trigger). Added `@app.teardown_request _r4_rollback_on_error` in the app factory that rolls back when a request ends with an exception (complements the existing 500-handler rollback and the per-site rollbacks; only acts on the error path, so it never disturbs streaming/SSE success responses). **Verification (local, fresh venv):** py_compile clean; suite still green (114 passed); teardown confirmed registered; `/chat/1` renders 200 (happy path unaffected); and with the comments query forced to raise, the page now renders **200** (rollback lets the render continue) instead of cascading to 500. **Deferred:** the same `except`-without-rollback pattern exists in lower-traffic paths (`src/app/dashboard.py`, `src/app/room/**`, others) — the teardown net + FSA cover the cross-request cascade there; per-site within-request rollbacks are a follow-up.
- **Files:** `src/app/chat.py` (7 rollbacks: ~L468, 527, 560, 604, 620, 1118, 1139); `src/app/__init__.py` (`@app.teardown_request` ~L876, above the existing 500 handler). Deferred: `src/app/dashboard.py`, `src/app/room/**`.

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
