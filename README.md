# AI Collab Online

Collaborative learning rooms where students and AI work together through structured journeys. Learners and teams progress through guided steps, carry context across chats (not just the latest thread), and export real artifacts, rather than treating the product as one more chatbot pasted into a document.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat&logo=github)](https://github.com/writeian/Collab_AI_Online)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)

**Live app:** https://collab.up.railway.app  ·  **Health check:** https://collab.up.railway.app/health

---

## Contents

- [Overview](#overview)
- [Screenshots](#screenshots)
- [Features](#features)
- [How it works](#how-it-works)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started (local)](#getting-started-local)
- [Configuration](#configuration)
- [Database and migrations](#database-and-migrations)
- [Testing](#testing)
- [Deployment](#deployment)
- [Branches and workflow](#branches-and-workflow)
- [Troubleshooting](#troubleshooting)
- [Further documentation](#further-documentation)
- [License and credits](#license-and-credits)

---

## Overview

| | |
|:---|:---|
| **What it is** | A web app built around **rooms**, **structured journeys** (for example writing or study paths), **multi user chat**, and **context aware AI** tied to a room's goals and history. |
| **Who it is for** | Students, writing groups, educators, and small teams who learn through dialogue and need continuity between sessions. |
| **The problem** | Plain chat and static forums lose the thread and lose progress. A generic AI assistant forgets earlier work in the same course or project. |
| **What makes it different** | Cross chat memory (notes, welcomes, progression), pin seeded focus chats, presence aware collaboration, and prompt assembly tuned to mode, tone, length, attached documents, and multi speaker threads. |

### Why it is not "ChatGPT in a Google Doc"

| Typical setup | AI Collab Online |
|---|---|
| Shared doc plus a side chat | A room plus a journey is the spine. Chats are steps in a path, not loose margin notes. |
| A copilot inside one document | Cross chat context: milestones, notes, and welcome messages that reference prior chats in the same room. |
| Slack or Discord plus a bot | Structured templates (essay steps, study group modes), rubric style controls, and exports (notes, outlines, docx). |
| An LMS discussion board | Real time collaboration, presence, pin seeded synthesis chats, and adaptive AI, all in one product. |

---

## Screenshots

| Learning journey: progress, modules, collaboration | Home: rooms, goals, activity |
|:---:|:---:|
| ![Learning journey with steps, completion, and avatars](docs/screenshots/learning-journey.png) | ![Dashboard showing learning spaces](docs/screenshots/dashboard-learning-spaces.png) |

| Study group setup wizard | Chat: tone and length, presence, structured AI |
|:---:|:---:|
| ![Study group setup wizard](docs/screenshots/study-group-setup-wizard.png) | ![Chat with tone, length, participants, and an AI reply](docs/screenshots/chat-tone-length-collaboration.png) |

---

## Features

**Rooms and journeys**
- Rooms group a cohort or team, with an owner (instructor) and members.
- Structured templates lay out a sequence of steps (for example an academic essay path or a study group mode).
- Progression tracking shows where a learner is in the journey and suggests the next step.

**Context aware chat**
- Multi user chat inside a room, with per message comments and pinning.
- Cross chat memory: milestone notes and welcome messages can reference earlier chats in the same room, so a new chat does not start from zero.
- Pin seeded chats capture a frozen snapshot of the pinned sources, so the AI context does not drift when the originals change later.
- Tone and length controls let each learner tune how supportive or critical the AI is, and how long replies run.

**Document library**
- Upload PDF, DOCX, or plain text into a room library.
- Uploaded documents are chunked and indexed, then retrieved into the AI context when relevant.
- Instructors can mark key documents (syllabus, evaluation rubric) that shape the room's guidance.

**Collaboration**
- Presence heartbeats show who is active in a room.
- Real time delivery of new messages, with a queue notice when the AI is busy.

**Study tools**
- Quiz, flashcards, mind map, and narrative generators built on top of a room's material.

**Exports**
- Turn a chat or its notes into an outline, transcript, or Word document.

A fuller capability list lives in [FEATURES.md](FEATURES.md).

---

## How it works

### The AI reply pipeline

The core design goal is that a slow model call never blocks the web server. When a learner sends a message:

1. The browser posts the message with an `X-AI-Async` header.
2. If Redis is configured, the server saves the user message, returns **HTTP 202** with a stream URL, and does not generate the reply inline.
3. The browser opens that URL as a Server Sent Events (SSE) stream. Opening it enqueues a job on the `ai_replies` queue.
4. A separate **RQ worker** process picks up the job, calls the model, streams the reply chunks over Redis pub/sub, and persists the finished assistant message.
5. The SSE endpoint relays those chunks to the browser as they arrive.

If Redis is not configured, the server falls back to streaming inside the request, and then to a plain synchronous reply. In request model calls are time boxed at 30 seconds so a stalled provider frees the thread quickly instead of tying up a worker.

The "continue a truncated reply" action uses the same worker path.

### Cross chat memory

When a chat reaches a milestone, the app can generate notes and welcome messages that summarise progress. Those are stored against the room and pulled into the prompt for later chats, which is how context accumulates across separate conversations instead of resetting each time.

### Blueprints and routes

The Flask app is organised into blueprints, mounted under these prefixes:

| Blueprint | Prefix | Responsibility |
|---|---|---|
| `auth` | `/auth` | Register, log in, password reset, profile |
| `chat` | `/chat` | The chat view, message send, SSE streaming, pins, comments |
| `room` | `/room` | Room creation, membership, invitations, learning steps |
| `dashboard` | `/dashboard` | The signed in home and activity stats |
| `library` | `/api/library` | Document upload, search, and storage |
| `documents` | `/documents` | Google Docs import and export generation |
| `quiz`, `flashcards`, `mindmap`, `narrative` | `/api/...` | Study tool generators |
| `analytics` | `/analytics` | Usage analytics |
| `admin`, `admin_reset` | `/` | Admin utilities (gated by `ADMIN_EMAILS`) |
| `google_auth` | `/auth/google` | Google OAuth for user Docs access |

---

## Tech stack

- **Language and framework:** Python 3.11, Flask (application factory pattern in `create_app`).
- **Data:** SQLAlchemy with Flask SQLAlchemy. PostgreSQL in production, SQLite locally. Alembic for production migrations.
- **AI:** Anthropic Claude as the primary provider, with an OpenAI fallback path.
- **Async work:** Redis plus RQ, with a dedicated worker on the `ai_replies` queue.
- **Web server:** Gunicorn with the `gthread` worker class.
- **Security:** Flask WTF (CSRF), Flask Limiter (rate limiting), server side sessions, security headers, and a content security policy.
- **Frontend:** Jinja2 templates, Tailwind (via CDN) with custom CSS, and Lucide icons.
- **Monitoring:** Optional Sentry integration, dormant unless `SENTRY_DSN` is set.

---

## Project structure

```
Collab_AI_Online/
├── run.py                  # Local dev entry point (serves on port 5001)
├── wsgi.py                 # WSGI target for Gunicorn in production
├── start.sh                # Railway start command; execs gunicorn -c gunicorn_conf.py
├── gunicorn_conf.py        # Single source of truth for Gunicorn tuning (env overridable)
├── Procfile                # web and worker process definitions
├── railway.toml            # Railway build and deploy config (nixpacks)
├── requirements.txt        # Python dependencies
├── env_template.txt        # Copy to .env and fill in
├── alembic.ini             # Alembic (production migrations) config
├── migrations/             # Alembic migration scripts (PostgreSQL only)
├── templates/              # Jinja2 templates
├── tests/                  # Pytest suite
├── docs/                   # Additional documentation and screenshots
└── src/
    ├── main.py             # Builds the app object
    ├── config/settings.py  # Config classes (base, development, production)
    ├── models/             # SQLAlchemy models
    ├── utils/              # Prompt assembly, document extraction, AI clients, helpers
    ├── workers/            # RQ jobs (ai_reply_job, learning_jobs, mode_backfill_job)
    └── app/                # Flask app package
        ├── __init__.py     # create_app: config, extensions, blueprints, schema
        ├── access_control.py
        ├── auth.py, chat.py, dashboard.py, documents.py, analytics.py, admin.py
        ├── room/           # Room feature (routes, services)
        ├── library/        # Document library (upload, search, storage)
        ├── quiz/, flashcards/, mindmap/, narrative/   # Study tools
        ├── api/            # JSON APIs (card view, card comments)
        └── static/         # Served CSS, JS, and images
```

---

## Getting started (local)

**Prerequisites:** Python 3.11 and an Anthropic API key. Redis is optional locally (needed only to exercise the async worker path).

```bash
git clone https://github.com/writeian/Collab_AI_Online.git
cd Collab_AI_Online

python3.11 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp env_template.txt .env            # then edit .env (see Configuration below)

python run.py                       # serves http://localhost:5001
```

On first boot the app creates its local SQLite schema automatically (`db.create_all()` plus an additive column reconciler), so there is no separate migration step for local development. The database file lives at `instance/ai_collab.db`.

At a minimum, set `SECRET_KEY` and `ANTHROPIC_API_KEY` in `.env` before starting. A short checklist is in [SETUP_LOCAL.md](SETUP_LOCAL.md).

### Running the async worker locally (optional)

To test the async AI path end to end, run Redis and an RQ worker alongside the app:

```bash
redis-server --port 6379 &                       # or: brew services start redis
export REDIS_URL=redis://localhost:6379/0
rq worker --url $REDIS_URL ai_replies             # in a second terminal
python run.py                                     # in a third, with REDIS_URL set
```

With `REDIS_URL` set, the chat page uses the async worker path; without it, the app streams inside the request instead.

---

## Configuration

Configuration is read from environment variables (loaded from `.env` locally). The full annotated list is in `env_template.txt`. The most important variables:

| Variable | Required | Purpose |
|---|---|---|
| `SECRET_KEY` | Yes | Signs sessions. Production refuses to boot if this is missing or left at the insecure default. |
| `ANTHROPIC_API_KEY` | Yes | Primary AI provider. |
| `OPENAI_API_KEY` | No | Enables the OpenAI fallback path. |
| `DATABASE_URL` | Prod | PostgreSQL connection string. Falls back to local SQLite when unset. |
| `REDIS_URL` | Prod | Enables the async AI worker and shared rate limiting. |
| `AI_ASYNC_ENABLED` | No | Set to `false` to force in request AI even when Redis is available. Defaults to on. |
| `EMAIL_PROVIDER` | Prod | Configures outbound email so password resets are delivered. |
| `SENTRY_DSN` | No | Enables error monitoring when set. |
| `ADMIN_EMAILS` | No | Comma separated allowlist for admin routes. |
| `MAX_CONTENT_LENGTH_MB` | No | Hard cap on request body size (default 16). |
| `DB_POOL_SIZE`, `DB_POOL_MAX_OVERFLOW` | No | Per worker PostgreSQL pool sizing. Keep `workers x (pool + overflow)` under the database's connection limit. |
| `GUNICORN_WORKERS`, `GUNICORN_THREADS`, `GUNICORN_TIMEOUT` | No | Gunicorn tuning. Defaults target roughly 20 concurrent users. |
| `AI_MAX_TOKENS`, `AI_MAX_HISTORY` | No | Reply length cap and how many turns of history to include. |

---

## Database and migrations

- **Local (SQLite):** the schema is created and reconciled on boot. No migration command is needed.
- **Production (PostgreSQL):** Alembic manages the schema. The migration scripts gate on `information_schema` and are PostgreSQL specific, so they do not run against SQLite. Apply them with `alembic upgrade head` against the production database.

The additive column reconciler that runs on boot adds any model columns missing from existing tables, so the running schema does not silently drift from the models. It never drops or rewrites columns.

---

## Testing

```bash
PYTHONPATH="$PWD" ./venv/bin/pytest -q
```

The suite uses an isolated temporary SQLite database (configured in `tests/conftest.py`), so running tests never touches your development database. Tests that make real network or AI calls are marked and deselected by default.

---

## Deployment

Production runs on **Railway**, built with nixpacks from `railway.toml`.

- **Start command:** `sh start.sh`, which exports `PORT` and execs `gunicorn -c gunicorn_conf.py wsgi:app`. All server tuning lives in `gunicorn_conf.py` and is overridable through environment variables.
- **Processes:** the `Procfile` defines a `web` process (Gunicorn) and a `worker` process (`rq worker --url $REDIS_URL ai_replies`). The worker must be running for the async AI path to complete.
- **Health check:** `/health`, used by Railway to gate deploys.
- **Static assets:** cache busted by a version query string. After a deploy, hard refresh the browser so new CSS and JS are picked up.

Set `SECRET_KEY`, `ANTHROPIC_API_KEY`, `DATABASE_URL`, and `REDIS_URL` in the Railway environment, plus `EMAIL_PROVIDER` for password reset delivery and `SENTRY_DSN` for error monitoring. More detail is in [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Branches and workflow

- **`updated-edu-tools`** is the production branch. Railway builds and deploys from it. Changes land through reviewed pull requests.
- **`dev`** is a legacy skeleton kept for history. It is not the current product, so do not branch new work from it.

Typical flow:

```bash
git checkout updated-edu-tools
git pull --ff-only
git checkout -b your-feature-branch
# make changes, run the tests
# open a pull request into updated-edu-tools
```

---

## Troubleshooting

- **Production will not boot, "SECRET_KEY" error:** set a real `SECRET_KEY` in the environment. The default is refused in production on purpose.
- **AI replies never arrive in production:** confirm the `worker` process is running and `REDIS_URL` is set. Without the worker, enqueued jobs are never processed.
- **Password reset emails do not send:** set `EMAIL_PROVIDER` (and its related variables). When email is not configured, a reset token is issued but no message is delivered.
- **"too many connections" under load:** lower `DB_POOL_SIZE` and `DB_POOL_MAX_OVERFLOW` so `workers x (pool + overflow)` stays under the database limit.
- **Old styles after a deploy:** hard refresh. Static assets are cached aggressively and busted by version query strings.

---

## Further documentation

| Document | Contents |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Stack and high level design choices. |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Environment variables, tests, and the project tree. |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Railway and production entry points. |
| [FEATURES.md](FEATURES.md) | Full capability breakdown. |
| [CHANGELOG.md](CHANGELOG.md) | Recent notable changes. |

---

## Contributing

1. Branch off `updated-edu-tools`.
2. Make your change and run the test suite (`pytest -q`).
3. Open a pull request into `updated-edu-tools` with a clear description.

Report bugs and ideas through [GitHub Issues](https://github.com/writeian/Collab_AI_Online/issues).

---

## License and credits

Released under the [MIT License](LICENSE).

Built with Flask and the wider Python ecosystem, Anthropic Claude for AI, and Tailwind for styling. Made for educators, students, and writing teams who want learning to accumulate rather than reset with every new chat.
