# Development

Local setup, environment variables, tests, and project conventions.

---

## Prerequisites

- **Python 3.8+**  
- **Anthropic API key** (for AI features)  
- **Google Cloud** project if using Google Docs integration  

---

## Install

```bash
git clone https://github.com/writeian/Collab_AI_Online.git
cd Collab_AI_Online

python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt

cp env_template.txt .env
# Edit .env — see sections below

alembic upgrade head
python run.py
```

Short checklist: [SETUP_LOCAL.md](SETUP_LOCAL.md).

---

## Environment variables

Create `.env` (or set **Railway Variables**). Canonical template: **`env_template.txt`**.

### Required (typical)

```
SECRET_KEY=your_secret
FLASK_ENV=development
DATABASE_URL=postgresql+psycopg2://...   # optional locally; SQLite if your config allows
ANTHROPIC_API_KEY=sk-ant-...
```

### Email (SendGrid)

```
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.***
EMAIL_FROM=your_verified_sender@example.com
EMAIL_FROM_NAME=AI Collab Online
EMAIL_REPLY_TO=support@example.com
```

### Admin

```
ADMIN_EMAILS=you@example.com,other@example.org
```

### Refinement & AI

```
REFINE_V2_ENABLED=true
ENABLE_ARCHETYPE_PROMPTS=true
AI_FAILOVER_ORDER=anthropic,openai,templates
ANTHROPIC_MODEL=claude-sonnet-4-6
OPENAI_MODEL=gpt-4o-mini
AI_MAX_TOKENS=350
AI_MAX_HISTORY=6
# Optional per-mode: AI_MAX_TOKENS_DRAFT=500
```

### Multi-participant weaving (optional)

```
AI_WEAVING_ENABLED=true
AI_WEAVING_PIN_CHATS=false
AI_WEAVING_MIN_DISTINCT_USERS=2
AI_WEAVING_MAX_SPEAKERS_NAMED=3
```

### Limits

```
ROOM_MAX_CHATS=25
```

### Railway / documents (production-oriented)

See [RAILWAY_ENV_VERIFICATION.md](RAILWAY_ENV_VERIFICATION.md) for `USE_RAILWAY_DOCUMENTS`, `ENABLE_RAILWAY_FALLBACK`, etc.

---

## Code quality

```bash
python -m pytest tests/
python -m mypy src/app/ --ignore-missing-imports
python -m flake8 src/ --max-line-length=120
```

**Note:** Some tests expect **Postgres** types (e.g. `TSVECTOR`); full green on **SQLite** alone may not be possible until tests are split or DB is unified. Targeted suites (e.g. `tests/test_weaving_context.py`) run without a full DB.

---

## macOS case sensitivity

The default macOS filesystem is **case-insensitive**. `templates/` may appear as `Templates/` in some tools—they are the same folder. Use **`templates/`** (lowercase) in code and docs to match Git and Linux production.

---

## Project structure

```
Collab_AI_Online/
├── src/                    # Application packages
│   ├── app/               # Blueprints & static (served as /static)
│   ├── models/
│   ├── utils/
│   └── config/
├── templates/             # Jinja2
├── tests/
├── scripts/
├── deployment/
├── wsgi.py
└── start.sh
```

Deeper module map (chat, learning, access control) lived in the historical README; if you need it back in one place, open a PR to extend this section.

---

## Troubleshooting

- **Anthropic 529 (overloaded)** — app may retry and fall back to goal-aware templates; check Anthropic status and org limits; confirm `ANTHROPIC_API_KEY` on the right service.  
- **Railway endpoint slug** — names are globally unique; pick another under *Networking*.  
- **Custom domains** — CNAME to `*.up.railway.app`; with Cloudflare, try **DNS-only** during verification.  
- **Static 404 on Linux** — paths are case-sensitive (`static/` vs `Static/`).  
- **JSON + CSRF** — the app may rely on a fetch wrapper sending `X-CSRFToken`; custom clients must match.  

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
