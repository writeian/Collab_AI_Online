# Verify Card View Route Access

## Correct URL

The Card View preview page is at:
```
http://127.0.0.1:5001/api/dev/card-preview
```

**NOT** `/chat/` or `/room/` or any other path.

## Requirements

1. **Must be signed in** (route has `@require_login`)
2. **Dev API must be enabled** (one of):
   - `FLASK_ENV=development` OR
   - `CARD_VIEW_DEV_ENABLED=true` OR
   - Your email in `ADMIN_EMAILS` env var

## Quick Test

1. Start server:
   ```bash
   export CARD_VIEW_DEV_ENABLED=true
   export FLASK_ENV=development
   flask run --port 5001 --host 127.0.0.1
   ```

2. Sign in at: `http://127.0.0.1:5001/auth/login`
   - Username: `testuser`
   - Password: `testpass123`

3. Navigate directly to: `http://127.0.0.1:5001/api/dev/card-preview`

## What You Should See

- Page title: "Card View Preview - Dev"
- Header with "Card View Preview" and "DEV" badge
- Input panel on left with textarea
- Output panel on right with "Cards" header
- Empty state: "Paste text and click 'Segment' to see cards"

## If You See Legacy Chat Cards Instead

1. **Check the URL** - Make sure it's exactly `/api/dev/card-preview`
2. **Check browser cache** - Hard refresh (Cmd+Shift+R or Ctrl+Shift+R)
3. **Check environment variables** - Verify `CARD_VIEW_DEV_ENABLED=true`
4. **Check server logs** - Look for route access logs
5. **Check if you're signed in** - Route requires login

## Debugging

Check server logs when accessing the route:
```bash
# Should see logs like:
# INFO: Accessing /api/dev/card-preview
# INFO: Rendering template: dev/card_preview.html
```

If you see 403 Forbidden:
- Dev API is not enabled
- Set `CARD_VIEW_DEV_ENABLED=true` and restart server

If you see redirect to login:
- You're not signed in
- Sign in first, then access the route


