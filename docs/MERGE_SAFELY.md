# Merge Safely – Without Losing Critical Work or Committing Junk

Use this when bringing in new tools (e.g. from another branch or the Library Tool package) so you keep important changes and avoid committing unnecessary files.

---

## 1. Current state (before merge)

**Branch:** `feature/railway-deployment`

**Modified (candidate to commit):**
- `.gitignore` – e.g. `.venv/bin/` ignore
- `src/app/api/card_view.py` – card preview + card_key / query params
- `migrations/versions/f6g7h8i9j0k1_add_card_comment_table.py` – trivial (e.g. trailing newline)

**Untracked (optional; many are dev-only):**
- Docs: `CARD_VIEW_*.md`, `docs/card-view*.md`, etc.
- Scripts: `scripts/card_view_demo.py`, `scripts/create_test_user.py`, etc.
- Tests: `tests/test_card_*.py`
- Static dev: `src/app/static/css/dev/`, `src/app/static/js/dev/`
- Other: `test_route.py`, `DEBUG_PEEKS.md`, etc.

---

## 2. Recommended: commit only critical changes first

This keeps your card view work in history and makes the merge cleaner.

### Option A – Minimal (code + .gitignore only)

```bash
cd /Users/iread-mba/Collab_AI_Online

# Stage only what you need
git add .gitignore
git add src/app/api/card_view.py
git add migrations/versions/f6g7h8i9j0k1_add_card_comment_table.py

# Commit
git commit -m "feat(card-view): preview card_key + query params; ignore .venv/bin"
```

### Option B – Include Card View docs you care about

```bash
git add .gitignore src/app/api/card_view.py migrations/versions/f6g7h8i9j0k1_add_card_comment_table.py
git add CARD_VIEW_QUICK_START.md docs/card-view-quick-start.md
git commit -m "feat(card-view): preview enhancements + quick-start docs"
```

**Do not add** unless you explicitly want them in the repo:
- `DEBUG_*.md`, `README_Dec_7.md`, `test_route.py`
- One-off scripts you don’t want in history
- Anything under `debug/` or temp files (already in `.gitignore`)

---

## 3. Merge without losing anything

**Untracked files are not touched by merge.** They stay on disk. Only tracked files can get merge conflicts.

### If merging another branch (e.g. `dev` or a tools branch)

```bash
# 1. Save current state (optional; you already committed critical stuff)
git status   # confirm what’s committed vs untracked

# 2. Fetch and merge
git fetch origin
git merge origin/dev   # or your target branch name

# 3. If there are conflicts:
#    - Fix conflicts in the reported files
#    - git add <resolved-files>
#    - git commit (no message needed for merge)
```

### If bringing in the Library Tool from AIC-Final-Merge-Library-Tool-main

- Follow that package’s **MIGRATION_GUIDE** / README.
- Copy only the files it tells you to (e.g. from `new-files/`, and apply `modified-files/`).
- Do **not** do a git merge from that folder unless it’s a real git repo you intend to merge; treat it as a file copy / patch.

---

## 4. After the merge

- Run the app and smoke-test:
  - Health: `http://localhost:5001/health`
  - Card preview: `http://localhost:5001/api/dev/card-preview` (see `CARD_VIEW_QUICK_START.md`)
- If you pulled in new migrations: `alembic upgrade head`
- Your untracked files (extra docs, scripts, dev assets) are still there; add only what you want to keep in the repo.

---

## 5. Quick “don’t commit” checklist

Avoid adding:
- `.env`, `*.db`, `instance/`
- `debug/`, `*.log`, `__pycache__/`
- `.venv/`, `venv/`
- One-off test scripts (e.g. `test_route.py`) unless you mean to keep them
- Personal/debug docs (e.g. `DEBUG_PEEKS.md`, `README_Dec_7.md`) unless you want them in the repo

---

## 6. One-line summary

**Commit only:** `.gitignore` + `src/app/api/card_view.py` + card_comment migration (+ optional Card View quick-start docs). **Then** merge or copy in the new tools. Untracked files won’t be lost.
