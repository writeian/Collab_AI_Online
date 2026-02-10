# Abandoned Feature: Opaque Room Tokens & Access Codes

**Date:** December 7, 2025  
**Status:** Abandoned  
**Commits Reverted:** `ded2d16`, `2a074a8`, `e86d13f`

---

## What Was Attempted

### Feature: Opaque Room URLs + Password Protection

The goal was to replace numeric room IDs in URLs (e.g., `/room/123`) with opaque tokens (e.g., `/room/Ks8mQ7vL2xNpRtYw-_Z3cA`) for:

1. **Privacy** - Hide sequential room IDs that reveal how many rooms exist
2. **Security** - Make room URLs unguessable
3. **Access Control** - Optional password protection for rooms

### Changes Made

| File | Change |
|------|--------|
| `src/models/room.py` | Added `public_token` (22-char URL-safe) and `access_code_hash` columns |
| `src/app/room/services/room_service.py` | Added `get_room_by_token()` and `get_room_by_token_or_id()` |
| `src/app/__init__.py` | Added token backfill at app startup |
| `railway.toml` | Added `releaseCommand = "alembic upgrade head"` |
| `migrations/versions/f6g7h8i9j0k1_...` | Migration to add columns and backfill tokens |

### Code Examples

**New Room Model Fields:**
```python
public_token = db.Column(
    db.String(22), unique=True, index=True, nullable=True,
    default=lambda: secrets.token_urlsafe(16)
)
access_code_hash = db.Column(db.String(256), nullable=True)
```

**Token Generation:**
```python
@staticmethod
def generate_token() -> str:
    return secrets.token_urlsafe(16)  # 22-char URL-safe string
```

---

## Why It Was Abandoned

1. **Broke Production** - The migration/backfill caused issues on deploy
2. **Not Currently Needed** - The existing numeric room IDs work fine for current use cases
3. **Complexity vs. Value** - Added significant complexity for marginal security benefit
4. **Route Changes Required** - Would require updating all room URL routes to accept tokens

### Current Access Control Is Already Sufficient

The existing system enforces privacy through **membership checks**, not URL obscurity:

- `@require_room_access` decorator guards all room routes
- `@require_chat_access` decorator guards all chat routes
- Non-members hitting `/room/123` get rejected by the access guard
- Room membership is controlled via invite system

**Bottom line:** A non-member cannot access a room even if they know the numeric ID. The opaque tokens would have added "security through obscurity" on top of real access control - unnecessary complexity.

---

## If Revisited Later

To implement this properly in the future:

1. **Test migration thoroughly** in staging before production
2. **Make tokens optional** - Don't require them for existing routes
3. **Add routes gradually** - Support both `/room/123` and `/room/token` simultaneously
4. **Consider simpler alternatives** - Maybe just add access codes without changing URLs

---

## Files to Reference

The reverted code can be viewed via:

```bash
git show ded2d16 -p  # Room model + service changes
git show 2a074a8 -p  # Railway config
git show e86d13f -p  # Startup backfill
```

---

## Related

- Current room access: Uses numeric IDs with membership checks
- Room sharing: Currently via invite system (email-based)

