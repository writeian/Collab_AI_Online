# AI Collab Online: Onboarding Guide

For anyone picking up this codebase. Written 2026-10-16 from the repo at commit `3d205dd` on branch `main`.

## What the project is

A Flask web app for collaborative learning. Students, writing groups and small teams work in shared **rooms** that follow a structured **journey** (for example an academic essay or a study group). The AI keeps context across chats in a room through milestone notes and welcome messages, so a new chat doesn't start from zero.

- Live app: https://collab.up.railway.app (health check at `/health`)
- GitHub: writeian/Collab_AI_Online
- Stack: Python 3.11, Flask, SQLAlchemy, Postgres in production (SQLite locally), Alembic migrations, Claude as the main AI (OpenAI as fallback), Redis + RQ background worker, Gunicorn, Railway hosting, Jinja templates with Tailwind via CDN.

## Root files

**Read these:**

- `README.md`: the best overview of the project. Read it first.
- `STABILIZATION_TRACKER.md`: the previous developer's work log. For each fix it lists the problem, what was changed and which files.
- `ARCHITECTURE.md`: why the app is built this way (memory across chats, pin snapshots, presence, how prompts are put together).
- `SECURITY_INCIDENT_2025-11-27.md`: about a leaked database password. It still contains that password in plain text.

**Reference, read when needed:**

- `FEATURES.md`: full list of features.
- `CHANGELOG.md`: product history by version.
- `DEVELOPMENT.md`: environment variables and coding conventions.
- `SETUP_LOCAL.md`: short checklist for running the app locally.
- `DEPLOYMENT.md`: how to deploy.
- `DEMO.md`: screenshots. `EXAMPLES.md` just points to it.

**Run and deploy plumbing:**

- `run.py`: starts the app locally on port 5001.
- `wsgi.py`: production entry point that Gunicorn loads.
- `start.sh`, `Procfile`, `railway.toml`, `gunicorn_conf.py`: how Railway starts the web server and the background AI worker.
- `requirements.txt`, `requirements_production.txt`, `requirements_railway.txt`: Python dependencies.
- `env_template.txt`: copy to `.env` and fill in secrets.
- `alembic.ini` and `migrations/`: database schema changes for production Postgres. Each file in `migrations/versions/` adds one table or column.
- `db/create_chat_notes_table.sql`: a one-off SQL script.
- `pytest.ini`: test settings.

## `src/`: the application

**Startup and config:**

- `main.py`: builds the app and adds the health checks.
- `app/__init__.py`: `create_app()`. Wires up config, security headers and all the route modules.
- `config/settings.py`: development and production settings, including database pool sizes and upload limits.

**`models/`: database tables**, one file per concept. Core: `user`, `room`, `chat`, `document`, `pin`. Others: `quiz`, `flashcards`, `mindmap`, `card_comment`, `rubric`, `analytics`, `custom_prompt` (the AI "modes"), `refinement`, `learning`, `google_auth`.

**`app/`: pages and APIs**

- `chat.py` (1,682 lines): the heart of the app. Sending messages, streaming AI replies, pins, comments.
- `room/`: creating and editing rooms, invitations, learning steps, AI "refinement" of a room's description. Logic lives in `services/room_service.py`.
- `goals/`: one file per room template (academic essay, study group, business hub, creative studio, community space, learning lab, writing workshop). Each defines that template's steps and goals.
- `auth.py`, `google_auth.py`: login, registration, password reset, Google sign-in.
- `access_control.py`: who can see what. Every permission check goes through it.
- `dashboard.py`: the signed-in home page.
- `library/`: document upload, storage and search.
- `documents.py`, `google_docs.py`: Google Docs import and exports.
- `quiz/`, `flashcards/`, `mindmap/`, `narrative/`: study tool generators (`narrative/routes.py` is 1,362 lines).
- `api/`: card view and card comments APIs.
- `admin.py`, `admin_password_reset.py`, `analytics.py`: admin tools.
- `achievements.py`, `tutorial.py`, `trial.py`, `room_v2.py`: smaller features. `room_v2.py` looks like an experiment.
- `static/`: the app's CSS, JavaScript and images.

**`utils/`: logic underneath**

- `openai_utils.py` (2,482 lines, the biggest file): all AI calls. Despite the name, it handles Claude as the main provider, OpenAI as fallback, prompt building and modes.
- `documents/`: pulls text out of PDFs and Word files, splits it into chunks, indexes it for the AI.
- `learning/`, `smart_welcome.py`, `progression.py`: memory across chats and journey progress.
- `pin_helpers.py`, `pin_synthesis.py`: chats seeded from pins.
- `card_view/`: splits AI replies into cards.
- `room_presence.py`, `ai_load_tracker.py`: who's online, and detecting when the AI is busy.
- Small helpers: `email.py`, `title_generator.py`, `room_descriptions.py`, `helpers.py`, `message_display.py`, `ai_stream_logging.py`.

**`workers/`: background jobs run by the separate worker process**

- `ai_reply_job.py`: generates AI replies off the web server.
- `mode_backfill_job.py`: generates a room's AI modes in the background.
- `learning_jobs.py`: background jobs for learning-progress features.

## Other folders

- `templates/`: HTML pages, mirroring the routes (`chat/`, `room/`, `dashboard/`, `components/` for panels). `room/templates/` holds the page for each room template.
- `Static/` (capital S): landing page images and CSS. Separate from `src/app/static`.
- `tests/`: 15 test files, about 114 tests, all passing per the tracker.
- `docs/`: about 45 older design notes and incident write-ups, many from October 2025. Skim only when working in that area.
- `scripts/`: admin one-offs (create a test user, reset a password, list rooms).
- `deployment/`: older non-Railway setup (DigitalOcean + Nginx). Probably unused.
- `.github/workflows/`: automated tests (`ci.yml`) and Railway deploys.

## How an AI reply works

1. The browser posts the message with an `X-AI-Async` header.
2. If Redis is set up, the server saves the message and returns HTTP 202 with a stream URL.
3. The browser opens that URL as a Server-Sent Events stream, which queues a job on `ai_replies`.
4. The RQ worker calls the model, streams chunks over Redis pub/sub, and saves the finished reply.
5. Without Redis, the server streams inside the request instead, with a 30-second limit on model calls.

## Where to start

1. **Run it locally.** Use Python 3.11, `pip install -r requirements.txt`, copy `env_template.txt` to `.env`, add `SECRET_KEY` and `ANTHROPIC_API_KEY`. Then `python run.py` and `pytest`.
2. **Get access.** GitHub repo, Railway project, API keys. The tracker mentions waiting on "the professor's keys," so there's someone to ask.
3. **Check which branch is live.** The README says Railway deploys from `updated-edu-tools`, but GitHub has no branch by that name. Recent pull requests (#8 to #10) merged into `main`. Confirm in Railway's settings before pushing anything.
4. **Close S1 (critical security item).** Check in Railway that the database password was changed, then remove it from `SECURITY_INCIDENT_2025-11-27.md`. Ideally also scrub it from git history.
5. **Fix R3 (last open reliability item).** Look up the Postgres plan's connection limit and set `DB_POOL_SIZE` and `DB_POOL_MAX_OVERFLOW` in Railway so workers × (pool + overflow) stays under it. See `src/config/settings.py` around lines 40 to 46.
6. **Learn the main code path.** Follow one message from `templates/chat/view.html` to `app/chat.py`, then `utils/openai_utils.py`, then `workers/ai_reply_job.py`.

## Known open items (from STABILIZATION_TRACKER.md)

- **S1:** leaked database password in git history and in the incident doc. Blocked on confirming the password was changed.
- **R3:** database connection pool can exceed Railway's limit. Not started.
- Deferred follow-ups: missing rollbacks in lower-traffic paths (`dashboard.py`, `room/**`); full protection against decompression-bomb uploads; tightening the CSP (needs a compiled Tailwind build and removing inline scripts).
- Planned: a staging environment, CI against the deployed branch, cleaning up dead branches.
