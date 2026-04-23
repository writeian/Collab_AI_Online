# Architecture

Why this stack and shape exist—not only “what framework.”

---

## Product-shaped problems

1. **Cross-chat memory** — Learning is not one thread. The app stores and retrieves **notes**, **milestones**, and **welcome context** so a *new* chat in the same room is not a blank slate.  
2. **Pin snapshots** — Pin-seeded chats need a **stable corpus** at creation time; `PinChatMetadata` (and related flows) avoid silent drift when pins change in the library.  
3. **Presence** — Collaboration needs **who is here now**, not only message history; heartbeats feed UI and **busy-room** heuristics.  
4. **Prompt assembly** — One model call sits behind **mode prompts**, **optional document chunks**, **tone/length**, **archetypes**, **failover**, and **multi-speaker labeling**—so behavior is a system, not a single string template.  

---

## Backend

- **Flask** (3.x) — modular **blueprints**, explicit routes for chat, rooms, documents, auth, admin  
- **SQLAlchemy 2.x** + **Alembic** — Postgres in production; SQLite possible locally with schema caveats (some features expect Postgres types, e.g. full-text / document indexing)  
- **Session auth** + optional **OAuth** (Google, etc.)  

---

## Frontend

- **Jinja2** templates + **Tailwind**-oriented styling  
- **Vanilla JS** (ES6+), component-style splits, cache-busted static assets under `src/app/static/`  
- **Legacy / landing** assets may live under `Static/` — prefer lowercase `templates/` in docs and Git  

---

## AI layer

- **Anthropic** as primary; **OpenAI** and **template** fallbacks via `AI_FAILOVER_ORDER`  
- **Streaming** and non-streaming paths share preparation logic where possible  
- **Document retrieval** gated by env and room library configuration (`USE_RAILWAY_DOCUMENTS`, etc.)  
- **Weaving** — user turns can be **speaker-prefixed**; system instructions switch between **group** and **individual** framing based on recent distinct participants (`AI_WEAVING_*`)  

---

## Deployment

- **Railway** — common production target; `railway.toml`, release/migrate patterns documented under [DEPLOYMENT.md](DEPLOYMENT.md)  
- **Digital Ocean / Nginx / Gunicorn** — supported in scripts and historical docs  

---

## Repository layout (high level)

```
Collab_AI_Online/
├── src/
│   ├── app/           # Blueprints, routes, Flask static tree
│   ├── models/      # ORM models (chat, room, learning, pins, …)
│   ├── utils/       # AI, learning triggers, documents, …
│   └── config/
├── templates/       # Jinja (lowercase path; Git canonical)
├── migrations/
├── tests/
├── docs/            # Deep dives, incident notes, deployment
├── wsgi.py
└── start.sh
```

Detailed tree (older README): see [DEVELOPMENT.md](DEVELOPMENT.md).

---

## Type safety & quality

- Substantial **type hint** coverage; run `mypy` locally / in CI as configured  
- **flake8** for style  

---

## Further reading

- [RAILWAY_ENV_VERIFICATION.md](RAILWAY_ENV_VERIFICATION.md)  
- `docs/RAILWAY_DEPLOYMENT.md`  
- `SYNTHESIS_MODE_FIXES.md`, rollout / migration notes in repo root  
