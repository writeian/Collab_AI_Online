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
| R2 | 🟠 High | Performance | Synchronous AI calls block request threads | 2 | ✅ |
| R3 | 🟠 High | Reliability | DB connection pool can exceed Railway's limit | 2 | ⬜ |
| R4 | 🟠 High | Reliability | Transaction poisoning → intermittent 500s | 2 | ✅ |
| R5 | 🟡 Medium | Performance | N+1 queries on dashboard / member lists | 2 | ✅ |
| R6 | 🟡 Medium | Config | Dead gunicorn config, 300s timeout, hot-path logging | 2 | ✅ |
| S5 | 🟡 Medium | Security | Account enumeration (register + forgot-password) | 3 | ✅ |
| S6 | 🟡 Medium | Security | Password-reset token logged to server output | 3 | ✅ |
| S7 | 🟡 Medium | Security | Weak password policy (6 chars, no checks) | 3 | ✅ |
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

### R2 — Synchronous AI calls block request threads ✅ (high-frequency paths async; two low-frequency calls intentionally sync + honest)
- **Issue:** Some actions call the model in-request, holding one of ~24 server threads (3 workers × 8) for the whole call: message-send fallback (`sync_blocking`), "continue generating", and Google-Doc import on chat creation. Under a class this starves the thread pool → slow, then 5-minute timeouts → 500s.
- **Fix:** Route all model calls through the existing Redis + rq worker; make any in-request AI optional and time-boxed. Keep graceful fallback but stop masking errors with a canned greeting.
- **Findings that reframed the fix:**
  - The **main chat reply already has a working async path**: when the client sends `X-AI-Async: 1` and `REDIS_URL` is set, the POST returns `202` and a Redis+rq worker (`src/workers/ai_reply_job.py`) streams the reply over Redis pub/sub → SSE and persists it. It falls back to in-request SSE, then to the sync path.
  - **In-request AI is already time-boxed at 30s**: `call_anthropic_api` / `call_anthropic_api_stream` default `timeout=30` and pass it to the SDK; the OpenAI fallback uses `requests(..., timeout=30)`. So the "5-minute 500s" premise is largely already mitigated — a hung provider frees the thread in ~30s, not 5 min. Residual risk is thread-pool **saturation** under burst (many ~30s holds), not 5-minute hangs.
- **Implementation (this pass — honest errors + de-fragilize, no Redis/frontend change needed):**
  - `src/app/chat.py` **sync fallback**: removed the canned `"Hello! I'm here to help you with your research…"` reply that masked a real outage as if the AI had answered. Now rolls back, logs, flashes an honest "AI temporarily unavailable — your message was saved, try again", and 303-redirects. The user's message is preserved; **no fake assistant turn is persisted**.
  - `src/app/chat.py` **`continue_message`**: the AI call was unguarded → any failure 500'd. Wrapped it so a failure rolls back and flashes an honest message instead.
  - `src/app/room/routes/crud.py` **doc import**: commit the imported Google-Doc message **first** (so an AI failure can't lose the import), then make the AI reply best-effort/guarded so a model failure can't 500 chat creation.
  - `src/app/api/card_comments.py`: already returns an honest `503`/`500` (no masking) — left as-is.
  - **Verification (local, isolated temp DB):** forced `get_ai_response` to raise on the sync path → endpoint returns **303**, exactly **1 user message** persisted, **0 assistant messages**, canned greeting absent. Suite green (114 passed / 21 skipped / 0 failed); all three files `py_compile` clean.
- **Implementation (Phase 2 — worker path proven locally, `continue` routed through it):**
  - **Stood up Redis locally** (`brew install redis`) and proved the async path end-to-end: `enqueue_ai_reply_job` → rq worker dequeues → `process_ai_reply_job` streams chunks over Redis pub/sub → assistant message persisted. Verified twice — once with a stubbed model (deterministic) and once with a **real Anthropic streaming call** (start + 4 chunks + done, ~2.4s to first token, persisted text == streamed text).
  - **Frontend audit:** the **main reply is already async in production** — `chat-view.js` sends `X-AI-Async: 1` whenever `ai_async_available` (Redis configured); the sync path is only the fallback. So Phase 2's real surface was the secondary flows.
  - **`continue` now routes through the worker.** When `_ai_async_configured()`, `continue_message` writes `ai_stream_meta:{token}` with `user_message_id = the truncated message` + `critique_instructions = continuation_prompt` and returns **202** + `stream_url`; the existing `chat_ai_stream` SSE endpoint enqueues the job and relays it. The worker's `through_message`/`extra_system` params express a continuation exactly (same `parent_message_id` as the old sync code) — **no worker changes needed**. Sync path kept as the fallback. `continue-messages.js` updated to handle the 202 (open `EventSource`, reload on `done`, honest reset on `error`, best-effort reload on stream drop); cache-buster bumped `?v=1.5`→`1.6`.
  - **Verification (local Redis, isolated DB):** `continue` POST → **202** with `async:true`; **no** synchronous generation on the POST thread; meta targets the truncated message with the continuation prompt; feeding that meta to the worker persists a continuation with `parent_message_id` = the truncated message. `node --check` clean on the JS; suite 114/21/0.
- **Intentionally left synchronous (honest + 30s time-boxed), by design:** **Google-Doc import** (rare; happens during chat creation, a redirect flow with no SSE client on that page) and **card-comment AI replies** (already returns an honest 503). Async-routing these is low-value at class scale and would need extra frontend wiring; the high-frequency paths (every message, plus continue) are what matter for thread starvation, and those are async.
- **Follow-up before relying on the JS:** the `continue-messages.js` change passed `node --check` but should get a 1-minute real-browser smoke (click Continue on a truncated reply with Redis up) before the class. The sync fallback + defensive `onerror` reload bound the risk if anything's off.
- **Files:** `src/app/chat.py` (sync fallback ~L444, `continue_message` async branch ~L1303), `src/app/room/routes/crud.py` (doc import ~L638), `src/app/static/js/continue-messages.js`, `templates/base.html` (cache-buster). Unchanged: `src/app/api/card_comments.py` (already honest), worker `src/workers/ai_reply_job.py` (already built, reused as-is).

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

### R5 — N+1 queries on dashboard / member lists 🟡 ✅
- **Issue:** Member rendering runs one query per member (`[User.query.get(m.user_id) for m in members]`); the dashboard `index()` runs **six** count/aggregate queries **per room** in a loop (members, chats, messages, last-activity, prompts, comments). Both scale with N → sluggish at class scale (an instructor with many rooms, or a room with many students).
- **Fix:** Batch with `User.query.filter(User.id.in_(ids))` and grouped aggregate counts (`GROUP BY room_id`) so the query count is constant regardless of N.
- **Implementation:** `dashboard.index()` — replaced the per-room loop (≈6×N queries) with six grouped queries over `room_id IN (...)`, then a dict lookup per room; identical stats semantics (owner still `+1` on member_count, message/comment counts still via the Chat join, `last_activity` still `max(timestamp)`). `RoomService.get_room_members()` — replaced the per-member `User.query.get()` with a single `User.query.filter(User.id.in_(...))` batch (owner folded into the same query), preserving membership order and the owner-append behavior; this is on the **live room view** (`crud.py:200`, also api/invitations). Left alone: the `dashboard.room_detail()` N+1 at ~L294 is **dead code** (the route redirects to the new room view before reaching it). **Verification (local, fresh venv):** py_compile clean; suite green (114 passed); grouped counts proven equal to the old per-room counts (members/chats/messages MATCH); and a query-counter test shows the dashboard render is **flat at 10 queries for 1 room and for 8 rooms** (was ~6/room → would be ~52 at 8) — the N+1 is gone.
- **Files:** `src/app/dashboard.py` (`index()` grouped stats ~L47), `src/app/room/services/room_service.py` (`get_room_members()` batch ~L360).

### R6 — Config footguns: dead gunicorn config, timeout, hot-path logging 🟡 ✅ (config consolidated + logging fixed; timeout cut deferred to R2 by design)
- **Issue:** Railway starts via `start.sh`, which ignored `gunicorn_conf.py` (two disagreeing config sources — threads 8 vs 12, graceful 60 vs 30, keepalive default vs 5). `require_room_access` logged **6 ERROR lines on every room visit** (pure debug tracing), which now floods the ERROR stream that Sentry (R8) watches.
- **Fix:** Consolidate to one gunicorn config; drop the per-request ERROR logs to debug; make the request timeout a single tunable knob (actual lowering happens with R2).
- **Implementation:**
  - **Single source of truth:** `gunicorn_conf.py` is now authoritative and every knob is env-overridable. `start.sh` was reduced to `export PORT` + `exec gunicorn -c gunicorn_conf.py wsgi:app`; the `Procfile` `web:` line already used `-c gunicorn_conf.py`, so both paths now agree. Defaults were reconciled to match what was **live** in `start.sh` (workers 3, threads 8, graceful_timeout 60, keepalive 2, `preload_app=False`) — a pure consolidation with **no** prod concurrency change. `railway.toml` `startCommand` unchanged.
  - **Timeout (deferred, intentionally):** left at 300s. Correction to the original issue framing — with `gthread` workers `--timeout` is the worker *heartbeat* timeout, **not** a per-request kill (per gunicorn docs, non-sync workers aren't tied to request duration), so a streaming AI reply is never truncated and lowering it wouldn't free a busy thread mid-call. It only makes sense to lower once AI work moves off the request thread (**R2**). Documented inline in `gunicorn_conf.py`.
  - **Hot-path logging:** in `require_room_access`, removed the 3 pure-trace `logger.error` lines (LOOKING UP ROOM / ROOM LOOKUP RESULT / ACCESS GRANTED) and demoted the 3 control-flow ones (no-user redirect, 404, access-denied) to `logger.debug` with lazy `%`-args (no string cost when debug is off). ERROR stream is now clean on normal room visits.
  - **Verification:** `gunicorn -c gunicorn_conf.py --print-config wsgi:app` resolves to the intended values and imports `wsgi:app`; `sh -n start.sh` clean; test suite 114 passed / 21 skipped / 0 failed (unchanged baseline).
- **Files:** `start.sh`, `gunicorn_conf.py` (rewritten); `src/app/access_control.py:261–290` (logging). `railway.toml`, `Procfile` unchanged (already consistent).

---

## Week 3 — Smooth it & harden

### S5 — Account enumeration ✅ (forgot-password closed; register email is an accepted residual)
- **Issue:** Registration ("Username already exists" / "Email already registered") and forgot-password (different message when the email exists vs. not) let an attacker enumerate valid accounts.
- **Fix:** Make responses uniform (generic success/failure).
- **Implementation:** **forgot-password** now returns an identical generic response ("If an account with that email exists, a password reset link has been sent.") whether or not the address is registered, **and** whether or not the email actually sends. The old flow flashed "email sent / check your inbox" (or "link logged on server") for real accounts vs. the generic line for unknown ones — that difference was the enumeration signal. The reset token is still issued + emailed for real accounts (flow intact). **Register left as-is by design:** username-taken feedback is a UX necessity (usernames are a public namespace, shown throughout the app), and closing register *email* enumeration properly needs an email-verification signup flow (a feature, not a patch) — logged as a residual for after the class. Worth adding later: a rate limit on `/forgot-password` to blunt mass probing. **Verified:** existing vs. unknown email produce identical user-facing responses; token still issued internally for the real user.
- **Files:** `src/app/auth.py` `forgot_password()` (rewritten ~L340).

### S6 — Password-reset token logged to server output ✅ (code) — SMTP config is on Ian
- **Issue:** When email send fails / SMTP isn't configured, the full reset URL and token are printed to stdout (retained in Railway logs).
- **Fix:** Never log the token; confirm SMTP is configured in production.
- **Implementation:** Removed both `print(...)` blocks that dumped the reset URL + raw token to stdout on send-failure / unconfigured-SMTP (they persisted in Railway logs — anyone with log access could reset any account). Replaced with a `current_app.logger.warning` that records only that delivery failed for `user id=<id>` — **no token, no URL, no email address**. **Verified:** no `PASSWORD RESET LINK` / `Reset URL` / `Token:` prints remain in `auth.py`, and the forgot-password responses contain none of that text. **On Ian (ops):** confirm an email provider is actually configured in Railway (`EMAIL_PROVIDER` etc.) so resets deliver — otherwise a reset silently no-ops (token issued, no email arrives).
- **Files:** `src/app/auth.py` `forgot_password()` (~L355–375); email config `src/utils/email.py` (ops).

### S7 — Weak password policy ✅
- **Issue:** 6-character minimum, no complexity, across register / reset / change.
- **Fix:** Raise the minimum and add basic strength checks.
- **Implementation:** Added one `validate_password_strength(password, *, username, email)` helper (NIST-style — length over composition) and wired it into **all three** password-set paths so the rule can't drift: register, reset, change. Rules: **min 8 chars** (was 6), reject all-numeric, reject a small common-password blocklist, and reject passwords that contain the username or the email local-part. No forced symbol/case rules (they frustrate users for little gain). **Verified:** 6-char / all-digits / "password" / contains-username all rejected with clear messages; ordinary passphrases accepted; suite 114/21/0.
- **Files:** `src/app/auth.py` (`validate_password_strength` helper + register/reset/change call sites).

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
