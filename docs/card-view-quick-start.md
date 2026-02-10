# Card View Development - Quick Start Guide

**Last Updated:** February 10, 2026  
**Purpose:** Quick reference for working on the Card View feature

---

## 🚀 Quick Start

### Start the Development Server

```bash
cd /Users/iread-mba/Collab_AI_Online
export CARD_VIEW_DEV_ENABLED=true
export FLASK_ENV=development
python run.py
```

**Server will start on:** `http://localhost:5001`

### Access the Card Preview Tool

1. **Open in browser:** `http://localhost:5001/api/dev/card-preview`
2. **Log in** (or create account if needed)
3. **Paste text** in the input area
4. **Click "Segment"** to see how messages are parsed into cards

---

## 📍 Key Files & Locations

### Backend Files
- **API Route:** `src/app/api/card_view.py`
  - Endpoint: `/api/dev/card-segments` (POST)
  - Preview page: `/api/dev/card-preview` (GET)
- **Card Comment Model:** `src/models/card_comment.py`
- **Segmentation Logic:** `src/utils/card_view/`

### Frontend Files
- **Preview Template:** `templates/dev/card_preview.html`
- **Overlay Template:** `templates/dev/card_overlay.html`
- **CSS:** `src/app/static/css/dev/card-overlay.css`
- **JavaScript:** `src/app/static/js/dev/card-overlay.js`

### Documentation
- **Testing Guide:** `CARD_VIEW_TESTING_GUIDE.md`
- **Grid Fixes:** `CARD_VIEW_GRID_FIXES.md`
- **Route Verification:** `VERIFY_CARD_VIEW_ROUTE.md`

---

## 🎯 What is Card View?

The Card View feature segments long messages into individual "cards" that can be:
- **Viewed in a grid layout**
- **Opened in a fullscreen overlay carousel**
- **Commented on individually**
- **Navigated with keyboard/swipe gestures**

### Features

1. **Preview Mode (Simulation)**
   - Paste any text and see how it segments
   - Comments are in-memory only (lost on refresh)
   - AI replies are simulated

2. **Real API Mode**
   - Add `?chat_id=123&message_id=456` to URL
   - Comments persist to database
   - Real AI replies via Anthropic API
   - ⚠️ **Warning:** Preview content may be unrelated to actual message

---

## 🔧 Development Workflow

### Making Changes

1. **Edit backend logic:**
   ```bash
   # Edit segmentation or API logic
   vim src/app/api/card_view.py
   ```

2. **Edit frontend:**
   ```bash
   # Edit preview template
   vim templates/dev/card_preview.html
   
   # Edit styles
   vim src/app/static/css/dev/card-overlay.css
   
   # Edit JavaScript
   vim src/app/static/js/dev/card-overlay.js
   ```

3. **Test changes:**
   - Server auto-reloads in development mode
   - Refresh browser to see changes
   - Check browser console for errors

### Testing Checklist

- [ ] Grid layout renders correctly (2-4 cards per row)
- [ ] Cards are clickable and open overlay
- [ ] Navigation works (arrows, keyboard, swipe)
- [ ] Comments can be added (simulation or real API)
- [ ] AI replies work (simulation or real API)
- [ ] Deep linking works (`#card=<key>`)

---

## 🐛 Troubleshooting

### Server Won't Start

```bash
# Check if port is in use
lsof -ti:5001

# Kill process if needed
lsof -ti:5001 | xargs kill -9

# Restart server
python run.py
```

### Card Preview Shows 403 Forbidden

- Verify `CARD_VIEW_DEV_ENABLED=true` is set
- Verify `FLASK_ENV=development` is set
- Make sure you're logged in

### Changes Not Appearing

- Hard refresh browser (Cmd+Shift+R on Mac)
- Check server logs for errors
- Verify file was saved correctly
- Restart server if needed

### Browser Shows "Connection Refused"

- Check if server is running: `curl http://localhost:5001/health`
- Verify port 5001 is correct (not 5000)
- Check firewall settings

---

## 📝 Recent Changes (Feb 2026)

### Card Key Generation
- Added stable `card_key` generation for preview mode
- Uses negative timestamp to avoid conflicts with real messages
- Always includes `segment_index` and `body_hash`

### Real API Integration
- Added query param support: `chat_id`, `room_id`, `message_id`
- Auto-derives `room_id` from `chat_id` if not provided
- Auto-selects latest `message_id` if missing (with warning)

### Code Cleanup
- Removed non-essential library tool changes
- Kept only card view related modifications
- Prepared for merge with other tools

---

## 🔗 Related Endpoints

### Card View API
- `POST /api/dev/card-segments` - Segment text into cards
- `GET /api/dev/card-preview` - Preview UI page
- `GET /api/dev/card-segments/health` - Health check
- `POST /api/dev/card-segments/cache/clear` - Clear AI cache

### Card Comments API (Real Mode)
- `GET /chat/<chat_id>/cards/<card_key>/comments` - Get comments
- `POST /chat/<chat_id>/cards/<card_key>/comments` - Add comment
- `POST /comments/<comment_id>/ai` - Request AI reply

---

## 💡 Tips

1. **Use Browser DevTools**
   - Network tab: See API calls
   - Console: Check for errors/warnings
   - Elements: Inspect card structure

2. **Test Both Modes**
   - Simulation mode: Fast testing, no DB writes
   - Real API mode: Test persistence and real AI

3. **Sample Test Text**
   ```
   Introduction to Machine Learning
   
   Machine learning is a subset of artificial intelligence. 
   It enables computers to learn from data without explicit programming.
   
   Key Concepts:
   - Supervised learning uses labeled data
   - Unsupervised learning finds patterns
   - Reinforcement learning learns from rewards
   ```

4. **Keyboard Shortcuts**
   - Arrow keys: Navigate cards
   - ESC: Close overlay
   - Enter: Submit comment

---

## 📚 Additional Resources

- **Full Testing Guide:** See `CARD_VIEW_TESTING_GUIDE.md`
- **Grid Implementation:** See `CARD_VIEW_GRID_FIXES.md`
- **Route Details:** See `VERIFY_CARD_VIEW_ROUTE.md`

---

## 🎯 Next Steps

When returning to work:

1. **Start server:** Use the Quick Start commands above
2. **Open preview:** Navigate to `http://localhost:5001/api/dev/card-preview`
3. **Check git status:** `git status` to see what you were working on
4. **Review changes:** `git diff` to see uncommitted modifications

**Current Branch:** `feature/railway-deployment`  
**Modified Files:** `src/app/api/card_view.py`, `migrations/versions/f6g7h8i9j0k1_add_card_comment_table.py`

---

*For questions or issues, check the troubleshooting section or review the detailed testing guide.*
