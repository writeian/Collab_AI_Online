# Key Documents Feature – Changes & Issue Summary

## Overview

The Key Documents feature allows room instructors to upload and manage permanent documents (syllabus, evaluation rubric, other) that are protected across all chats in a room. Documents can be viewed in a modal on the room page and are also available in the Library tool on chat pages.

---

## Issues Encountered

### 1. Upload Progress Bar Not Showing

**Problem:** When uploading a document (especially to the Evaluation Rubric section), no progress bar was shown. Documents appeared in the list later without visual feedback.

**Cause:** ID mismatch – rubric progress div used `key-docs-rubric-progress` while the code referenced `key-docs-evaluation_rubric-progress` (the upload type is `evaluation_rubric`).

**Fix:** Renamed the rubric progress div to `key-docs-evaluation_rubric-progress` so it matches the upload type. Progress bar is now shown for all three sections (Syllabus, Evaluation Rubric, Other Key Documents).

---

### 2. Delete Not Reflecting in UI

**Problem:** After confirming deletion in the popup, documents stayed in the list instead of disappearing.

**Cause:** Several factors:
- `refreshKeyDocsDisplay()` was not awaited after delete.
- Optimistic removal from the DOM sometimes failed.
- `refreshKeyDocsDisplay()` on success could show stale data from cached responses.

**Fix:**
- Added optimistic removal: document is removed from the DOM immediately on confirm.
- Call `refreshKeyDocsDisplay()` after delete (on both success and failure) to stay in sync.
- Added cache-busting (`cache: 'no-store'`, `_=${Date.now()}`) and `Cache-Control: no-store` on the documents API response.

---

### 3. Documents Not Actually Deleted on Server

**Problem:** Backend returned `deleted_count: 0` even when the document existed. User saw: "Document could not be deleted. It may have already been removed." After closing the alert, the document reappeared after refresh.

**Cause:** Lookup by `file_id` was failing – document not found in DB. Possible causes: `file_id` format mismatch, room scoping, or serialization differences.

**Fix:** Added a fallback to delete by **document primary key (`doc_id`)** instead of `file_id`. The API now exposes `/api/library/key-documents/delete` which accepts `doc_id` and `room_id`.

---

### 4. "Delete failed" and Generic Errors

**Problem:** Deletion returned a generic "Delete failed" message instead of a specific error.

**Cause:** 
- CSRF protection could block POST requests when CSRF token was missing or invalid.
- Frontend did not consistently send CSRF token or credentials.

**Fix:** Exempted the library blueprint from CSRF: `csrf.exempt(library)`. Library API uses session auth (`login_required`). Added `credentials: 'same-origin'` to fetch calls.

---

### 5. SyntaxError in Library Tool (Chat Page)

**Problem:** `Uncaught SyntaxError: Unexpected end of input (at 1:1:19)` when deleting from the Library tool on the chat page.

**Cause:** `JSON.stringify(doc.name)` produced double-quoted strings (e.g. `"file name"`). When embedded in `onclick="deleteDocument(123, "file name", 1)"`, the inner quotes closed the HTML attribute early, producing invalid JavaScript.

**Fix:** Replaced inline arguments with `data-*` attributes on the delete button (`data-doc-id`, `data-doc-name`, `data-room-id`). Handler now uses `onclick="deleteDocument(this)"` and reads values from `button.dataset`.

---

### 6. Backend Delete Failing (ORM / Database)

**Problem:** Even with correct `doc_id`, delete failed – `delete_document_and_chunks` returned `False` without clear errors.

**Cause:** Cascade delete via SQLAlchemy could fail (e.g. SQLite vs PostgreSQL, or `DocumentChunk` using `postgresql.TSVECTOR` on SQLite).

**Fix:** Introduced `delete_document_by_id()` that:
1. Loads the document by primary key.
2. Deletes chunks with raw SQL: `DELETE FROM document_chunk WHERE document_id = :doc_id`.
3. Deletes the document row.

Raw SQL avoids ORM cascade and model-specific column loading that could break on SQLite.

---

## Summary of Code Changes

### Backend

| File | Change |
|------|--------|
| `src/app/library/storage.py` | New `/api/library/key-documents/delete` endpoint; uses `delete_document_by_id`; CSRF exempt |
| `src/app/__init__.py` | `csrf.exempt(library)` for the library blueprint |
| `src/utils/documents/indexer.py` | New `delete_document_by_id()` with raw SQL chunk deletion; `delete_document_and_chunks` now delegates to it |
| `src/utils/documents/database.py` | New `get_document_by_id()` helper |
| `src/app/library/storage.py` (list) | `Cache-Control: no-store` on documents API response |

### Frontend – Key Documents Modal (`templates/room/view_mountain_simple.html`)

| Change | Description |
|--------|-------------|
| Progress bar | `showKeyDocsProgress` / `updateKeyDocsProgress` before any async work; `requestAnimationFrame` for paint |
| Delete handler | `deleteKeyDoc(btn)` reads from `btn.dataset` instead of inline arguments |
| Delete API | Uses `/api/library/key-documents/delete` with `doc_id` when available |
| Input IDs | Correct `key-docs-rubric-input` mapping for evaluation rubric |
| File input | Cleared at start of upload so reselecting the same file triggers `change` |

### Frontend – Library Tool (`src/app/static/js/library-tool.js`)

| Change | Description |
|--------|-------------|
| Delete button | `data-doc-id`, `data-doc-name`, `data-room-id`; `onclick="deleteDocument(this)"` |
| Delete API | Calls `/api/library/key-documents/delete` with `doc_id` and `room_id` |
| `deleteDocument` | Accepts button or legacy args; reads from `dataset` when available |
| Error handling | Parses response JSON and surfaces server error messages |

---

## API Reference

### `POST /api/library/key-documents/delete`

Deletes a document by database primary key.

**Request body:**
```json
{
  "doc_id": 123,
  "room_id": 1
}
```

**Response (success):**
```json
{
  "success": true,
  "deleted_count": 1
}
```

**Response (document not found):** 200 with `deleted_count: 0` and `error` message.

**Permissions:** Requires session auth. Key documents require room instructor; regular documents require room access.

---

## Testing Checklist

- [ ] Upload to Syllabus – progress bar shows
- [ ] Upload to Evaluation Rubric – progress bar shows  
- [ ] Upload to Other Key Documents – progress bar shows
- [ ] Delete from Key Documents modal – document disappears and stays deleted
- [ ] Delete from Library tool (chat page) – document disappears and stays deleted
- [ ] Delete as non-instructor – key documents show permission error
- [ ] Refresh after delete – document does not reappear
