# Library Tool - Local Testing Guide

## Quick Start

### 1. Verify Dependencies
```bash
python -c "from pypdf import PdfReader; from docx import Document; print('✓ Dependencies OK')"
```

### 2. Set Environment Variables
In `.env`:
```bash
USE_RAILWAY_DOCUMENTS=true
```

### 3. Database Setup

**Option A: PostgreSQL (Recommended for Library Tool)**
```bash
# Install PostgreSQL locally
# Create database
createdb ai_collab

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_collab

# Run migrations
alembic upgrade head
```

**Option B: SQLite (UI Testing Only)**
```bash
# Migration will fail on pg_trgm line - that's expected
# Library Tool UI will appear but upload/search won't work
# Good for testing sidebar integration only
```

### 4. Start Application
```bash
python run.py
```

### 5. Test Library Tool

1. **Navigate to Chat**: Log in and open any chat
2. **Check Sidebar**: Look for "Library" tool card in Tools section
3. **Test Upload** (PostgreSQL only):
   - Click "Choose File"
   - Upload a PDF/DOCX/TXT file
   - Verify file appears in documents list
4. **Test Search** (PostgreSQL only):
   - Send a chat message that should match document content
   - Verify AI response includes document context

## Troubleshooting

**Migration fails with "pg_trgm" error**:
- Expected on SQLite (PostgreSQL-only feature)
- Use PostgreSQL for full Library Tool testing

**Library Tool doesn't appear**:
- Check browser console for JavaScript errors
- Verify `library-tool.js` loads (Network tab)
- Check `USE_RAILWAY_DOCUMENTS=true` in .env

**Upload fails**:
- Check database migration ran successfully
- Verify `document` and `document_chunk` tables exist
- Check browser console for API errors

## Migration Verification

Before running Library Tool migration:
```bash
# Check current migration
alembic current

# Should show: f6g7h8i9j0k1 (or later)
# If not, run: alembic upgrade f6g7h8i9j0k1 first
```

