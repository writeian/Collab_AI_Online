# Chat Improvements - Quick Reference

## 🚀 Quick Commands

### Enable Features (Railway)
```bash
# Phase 1: New Scroll Manager
railway variables set CHAT_NEW_SCROLL_MANAGER=true

# Phase 2: Mobile Scroll Fix
railway variables set CHAT_FIX_MOBILE_SCROLL=true

# Phase 3: Unified Padding
railway variables set CHAT_UNIFIED_PADDING=true

# Phase 4: WebSocket
railway variables set CHAT_WEBSOCKET_ENABLED=true
```

### Disable Features (Instant Rollback)
```bash
railway variables set CHAT_NEW_SCROLL_MANAGER=false
railway variables set CHAT_FIX_MOBILE_SCROLL=false
railway variables set CHAT_UNIFIED_PADDING=false
railway variables set CHAT_WEBSOCKET_ENABLED=false
```

### Local Testing
```bash
# .env file
CHAT_NEW_SCROLL_MANAGER=true
CHAT_FIX_MOBILE_SCROLL=true
CHAT_UNIFIED_PADDING=true
CHAT_WEBSOCKET_ENABLED=true

# Run locally
python run.py
```

---

## 📁 Files Changed Per Phase

### Phase 1: Scroll Manager
```
NEW:
- src/app/static/js/scroll-manager.js

MODIFIED:
- templates/chat/view.html (add feature flag script)
- src/app/static/js/chat-view.js (add conditional skip)
- src/config/settings.py (add flag)
```

### Phase 2: Mobile Scroll Fix
```
NEW:
- src/app/static/js/mobile-scroll-detector.js

MODIFIED:
- src/app/static/js/chat-view.js (update polling logic)
```

### Phase 3: Unified Padding
```
NEW:
- src/app/static/js/input-padding-manager.js

MODIFIED:
- src/app/static/js/chat-view.js (add conditional skip)
- src/app/static/js/chat-input-fixes.js (add conditional skip)
```

### Phase 4: WebSocket
```
NEW:
- src/app/websocket.py
- src/app/static/js/chat-websocket.js

MODIFIED:
- src/app/__init__.py (initialize Socket.IO)
- src/app/chat.py (broadcast messages)
- requirements.txt (add flask-socketio)
- templates/chat/view.html (add Socket.IO CDN)
```

---

## 🔍 Testing Checklist

### Before Each Phase Deployment
- [ ] Code review completed
- [ ] Local testing passed
- [ ] Linter checks passed (`flake8`, `mypy`)
- [ ] Feature flag defaults to `false`
- [ ] Rollback procedure documented
- [ ] Smoke tests written

### After Deployment (Flag OFF)
- [ ] App still works with flag disabled
- [ ] No console errors
- [ ] No breaking changes

### After Enabling (Flag ON)
- [ ] New feature works as expected
- [ ] No regressions in existing features
- [ ] Mobile testing completed
- [ ] Desktop testing completed
- [ ] Monitor logs for 24 hours

---

## 🚨 Emergency Contacts & Procedures

### If Chat Breaks in Production

**Step 1: Immediate Mitigation (1 minute)**
```bash
# Disable ALL new features
railway variables set CHAT_NEW_SCROLL_MANAGER=false
railway variables set CHAT_FIX_MOBILE_SCROLL=false
railway variables set CHAT_UNIFIED_PADDING=false
railway variables set CHAT_WEBSOCKET_ENABLED=false
```

**Step 2: Verify Rollback (2 minutes)**
- Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)
- Check chat functionality
- Verify in browser console: `window.CHAT_FEATURES` should show all false

**Step 3: Investigate (5-10 minutes)**
- Check Railway logs: `railway logs`
- Check browser console errors
- Review recent commits

**Step 4: Deploy Fix or Full Rollback**
```bash
# Option A: Deploy hotfix
git checkout -b hotfix/chat-issue
# ... fix code ...
git push origin hotfix/chat-issue

# Option B: Revert to previous deployment
railway rollback --to-version <previous-version>
```

---

## 📊 Monitoring Dashboards

### Browser Console Checks
```javascript
// Check feature flags
console.log(window.CHAT_FEATURES);

// Check active systems
console.log('Scroll:', window.chatScroll ? 'new' : 'legacy');
console.log('WebSocket:', window.chatWebSocket?.connected);
console.log('Padding:', window.__SKIP_LEGACY_PADDING__ ? 'unified' : 'legacy');

// Check metrics
console.log(window.CHAT_METRICS);
```

### Server-Side Monitoring
```bash
# Railway logs
railway logs --tail

# Check for errors
railway logs | grep ERROR

# Check WebSocket connections
railway logs | grep WebSocket
```

---

## 🎯 Gradual Rollout Percentages

### Conservative Rollout (Recommended)
```
Week 1: Admins only (manual testing)
Week 2: 1% of users
Week 3: 5% of users
Week 4: 25% of users
Week 5: 50% of users
Week 6: 100% of users
```

### Aggressive Rollout (if timeline is tight)
```
Day 1: Admins only
Day 2: 10% of users
Day 3: 50% of users
Day 4: 100% of users
```

---

## 📝 Git Workflow

### Branch Naming
```
feature/scroll-manager
feature/mobile-scroll-fix
feature/unified-padding
feature/websocket-realtime
```

### Commit Message Format
```
feat: add ScrollManager with feature flag
fix: mobile scroll detection in polling
refactor: consolidate padding logic
docs: update WebSocket implementation plan
test: add scroll manager unit tests
```

### PR Template
```markdown
## Changes
- [ ] Phase X: [Feature Name]

## Testing
- [ ] Local testing completed
- [ ] Mobile testing completed
- [ ] Feature flag tested (on/off)

## Rollback Plan
- Feature flag: `CHAT_[FEATURE]_ENABLED=false`
- Revert commit: `git revert [hash]`

## Checklist
- [ ] Code reviewed
- [ ] Tests added
- [ ] Docs updated
- [ ] Feature flag defaults to false
```

---

## 🔗 Related Documentation

- [Full Implementation Plan](./chat-improvements-implementation-plan.md)
- [Chat Architecture Overview](./chat-architecture.md) _(you created this earlier)_
- [Feature Roadmap](./FEATURE_ROADMAP.md)
- [Deployment Guide](../RAILWAY_DEPLOYMENT.md)

---

**Last Updated**: October 4, 2025

