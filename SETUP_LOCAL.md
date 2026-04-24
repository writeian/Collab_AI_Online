# Local Development Setup

Quick reference for running AI Collab Online locally.

## Prerequisites

- Python 3.8+ (3.10+ recommended; 3.9 works with relaxed `click` version)
- `.env` file (copy from `env_template.txt`)

## Setup Steps

### 1. Virtual environment

```bash
cd Collab_AI_Online
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate   # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

**Note:** If `psycopg2-binary` fails (e.g. missing `pg_config`), you can skip it for SQLite-only local dev:

```bash
pip install $(grep -v psycopg2 requirements.txt | grep -v '^#' | tr '\n' ' ')
```

### 3. Environment variables

```bash
cp env_template.txt .env
# Edit .env and add at minimum:
#   SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
#   ANTHROPIC_API_KEY=<your key from console.anthropic.com>
#   ANTHROPIC_MODEL=claude-sonnet-4-6  # optional; code default is Sonnet 4.6. Use claude-haiku-4-5 for speed/cost or claude-opus-4-7 for max quality.
#   FLASK_ENV=development
```

### 4. Database

The app uses **SQLite** by default when `DATABASE_URL` is not set. Tables are created automatically on first run via `db.create_all()`.

- **SQLite:** No setup needed. DB file: `instance/ai_collab.db`
- **PostgreSQL:** Set `DATABASE_URL` in `.env`, then run `alembic upgrade head`

### 5. Run the app

```bash
python run.py
```

- App: http://localhost:5001
- Health: http://localhost:5001/health

## Quick test

```bash
curl http://localhost:5001/health
# Expect: {"status":"ok",...}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `click==8.2.1` not found | Use Python 3.10+ or the relaxed `click>=8.1,<9` in requirements |
| `psycopg2-binary` build fails | Skip it for SQLite; or `brew install postgresql` for PostgreSQL |
| Alembic migrations fail on SQLite | Migrations target PostgreSQL. Use `db.create_all()` (automatic on app start) for SQLite |
| Rate limit warning | Expected in dev; configure Redis for production |
