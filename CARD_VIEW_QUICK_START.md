# Card View - Quick Reference

**Quick start commands and key info for Card View development**

## 🚀 Start Server

```bash
cd /Users/iread-mba/Collab_AI_Online
export CARD_VIEW_DEV_ENABLED=true
export FLASK_ENV=development
python run.py
```

## 🌐 Access URLs

- **Card Preview:** http://localhost:5001/api/dev/card-preview
- **Health Check:** http://localhost:5001/health
- **Main App:** http://localhost:5001

## 📁 Key Files

- **API:** `src/app/api/card_view.py`
- **Template:** `templates/dev/card_preview.html`
- **CSS:** `src/app/static/css/dev/card-overlay.css`
- **JS:** `src/app/static/js/dev/card-overlay.js`

## 🐛 Troubleshooting

**Port in use?**
```bash
lsof -ti:5001 | xargs kill -9
```

**Connection refused?**
- Check server is running: `curl http://localhost:5001/health`
- Verify environment variables are set

**403 Forbidden?**
- Make sure `CARD_VIEW_DEV_ENABLED=true`
- Make sure you're logged in

## 🔀 Merge / Bring in other tools

**Before merging:** Commit only critical card view changes, then merge. See **`docs/MERGE_SAFELY.md`** so you don’t lose anything or commit unnecessary files.

## 📚 Full Documentation

See `docs/card-view-quick-start.md` for complete guide.
