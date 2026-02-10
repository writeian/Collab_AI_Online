# Card View Feature — Complete Documentation

> **Status:** Dev Preview (accessible at `/api/dev/card-preview`)  
> **Last Updated:** December 2024

## Table of Contents

1. [Overview](#overview)
2. [Goals & Rationale](#goals--rationale)
3. [Architecture](#architecture)
4. [Segmentation Engine](#segmentation-engine)
5. [AI Integration](#ai-integration)
6. [Per-Card Comments](#per-card-comments)
7. [AI Reply Feature](#ai-reply-feature)
8. [UI/UX Design](#uiux-design)
9. [Accessibility](#accessibility)
10. [API Reference](#api-reference)
11. [Configuration & Limits](#configuration--limits)
12. [Known Limitations](#known-limitations)
13. [Future Enhancements](#future-enhancements)

---

## Overview

Card View transforms long AI responses into structured, digestible learning units called **cards**. Instead of presenting users with a wall of text, the feature segments content into 3–9 logical chunks, each with:

- A **header** summarizing the card's content
- The **body** containing the actual content
- Optional **comments** for discussion
- **Relationship hints** explaining how cards connect

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Segmenter | `src/utils/card_view/segmenter.py` | Python-based content chunking |
| Detector | `src/utils/card_view/detector.py` | Structure detection (bullets, code, headings) |
| AI Helpers | `src/utils/card_view/ai_helpers.py` | Guiding questions & relationship hints |
| Card View API | `src/app/api/card_view.py` | Blueprint for segmentation endpoint |
| Comments API | `src/app/api/card_comments.py` | Blueprint for per-card comments |
| Preview UI | `templates/dev/card_preview.html` | Dev-only testing interface |

---

## Goals & Rationale

### Problem Statement

Long AI responses (500+ words) overwhelm learners:
- Difficult to track reading progress
- No natural pause points for reflection
- Hard to reference specific parts in discussion
- Cognitive overload reduces retention

### Solution: Card View

Break responses into **cards** that:

1. **Chunk content logically** — Respect structure (bullets stay together, code blocks intact)
2. **Generate meaningful headers** — Each card has a title for quick scanning
3. **Show relationships** — AI-generated hints explain how cards connect
4. **Enable focused discussion** — Comments attach to specific cards, not the whole message

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Request                              │
│                    POST /api/dev/card-segments                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Segmentation Engine                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Detector   │→ │  Segmenter  │→ │  Header Generator       │  │
│  │ (structure) │  │ (chunking)  │  │ (heuristic + AI fallback)│  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI Enrichment (optional)                    │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐   │
│  │  Guiding Question   │  │  Relationship Hints (batched)   │   │
│  │  (1 AI call)        │  │  (N-1 AI calls for N cards)     │   │
│  └─────────────────────┘  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Response                                 │
│  { segments, guiding_question, relationships, is_complete }     │
└─────────────────────────────────────────────────────────────────┘
```

### Module Structure

```
src/
├── utils/
│   └── card_view/
│       ├── __init__.py          # Package exports
│       ├── segmenter.py         # Core segmentation logic
│       ├── detector.py          # Structure detection helpers
│       ├── ai_helpers.py        # AI generation functions
│       └── prompts.py           # AI prompt templates
├── app/
│   └── api/
│       ├── card_view.py         # /api/dev/card-segments endpoint
│       └── card_comments.py     # Per-card comments CRUD
└── models/
    └── card_comment.py          # CardComment SQLAlchemy model
```

---

## Segmentation Engine

### Detection Phase (`detector.py`)

Identifies structural elements in the text:

| Element | Detection Method |
|---------|------------------|
| Markdown headings | Regex: `^#{1,6}\s+(.+)$` (outside code blocks) |
| Bullet lists | Lines starting with `- `, `* `, `• `, or `1. ` |
| Code blocks | Fenced with triple backticks |
| Paragraphs | Double newline separation |

### Chunking Phase (`segmenter.py`)

#### Core Algorithm

```python
def segment_text(text: str, min_segments=3, max_segments=9) -> List[Segment]:
    # 1. Detect and isolate code blocks
    # 2. Split by markdown headings (if any)
    # 3. Split by double newlines (paragraphs)
    # 4. Merge tiny segments (<100 chars) into neighbors
    # 5. Split oversized segments at sentence boundaries
    # 6. Apply tail-merge for incomplete last cards
    # 7. Enforce min/max constraints
```

#### Segment Data Class

```python
@dataclass
class Segment:
    body: str
    header: str
    segment_type: str        # 'text', 'code', 'list', 'heading'
    confidence: float        # Header confidence (0.0–1.0)
    is_truncated: bool       # True if incomplete (e.g., unclosed code block)
    
    @property
    def is_complete(self) -> bool:
        """Complete if not truncated AND ends with sentence punctuation."""
        return not self.is_truncated and self._ends_with_punctuation()
```

#### Header Generation

Headers are generated using a **heuristic-first** approach:

1. **Section title heuristic**: Short lines ending with `:` or in Title Case
2. **First sentence extraction**: First complete sentence under 80 chars
3. **AI fallback**: If heuristic confidence < 0.7, call AI to generate

```python
def generate_header(body: str, use_ai_fallback: bool = True) -> tuple[str, float]:
    # Try section title (e.g., "Key Concepts:")
    title = extract_section_title(body)
    if title:
        return normalize_header(title), 0.9
    
    # Try first sentence
    first_sentence = extract_first_sentence(body)
    if first_sentence and len(first_sentence) < 80:
        return normalize_header(first_sentence), 0.7
    
    # AI fallback
    if use_ai_fallback:
        return ai_generate_header(body), 0.85
    
    return "Content", 0.3
```

#### Header Normalization

- ALL CAPS → Title Case
- Remove trailing colons
- Trim to max 60 characters

#### Tiny-Card Merge Pass

Cards under 100 characters are merged into neighbors:

```python
def merge_tiny_cards(segments: List[Segment], min_chars=100) -> List[Segment]:
    for i, seg in enumerate(segments):
        if len(seg.body) < min_chars and len(segments) > MIN_SEGMENTS:
            # Merge into previous or next card
            neighbor = segments[i-1] if i > 0 else segments[i+1]
            neighbor.body += "\n\n" + seg.body
            segments.remove(seg)
```

#### Tail-Merge Pass

Incomplete or tiny last cards are merged into the previous:

```python
def tail_merge(segments: List[Segment]) -> List[Segment]:
    if len(segments) > 1:
        last = segments[-1]
        if last.is_truncated or len(last.body) < MIN_CHARS:
            segments[-2].body += "\n\n" + last.body
            segments[-2].is_truncated = last.is_truncated
            segments.pop()
```

#### Completeness Detection

A segment is marked **truncated** if:

- Unclosed code fence (opens ` ``` ` but never closes)
- Trailing incomplete list item (ends mid-bullet)
- Too short AND no sentence-ending punctuation

**Exception**: List bodies (containing `-`, `•`, numbered items) are considered complete even without terminal punctuation.

---

## AI Integration

### Guiding Question

A single, concise question that summarizes the entire message's learning objective.

**When generated:**
- Only if `use_ai=true` in request
- Only for messages > 200 characters
- Cached per message hash (TTL: 5 minutes)

**Prompt template:**

```
You are helping a learner understand an AI response. Generate ONE concise 
guiding question (1 sentence, max 15 words) that captures the main learning 
objective of this content.

Message (truncated):
{message_text[:2000]}

Respond with ONLY the question, no preamble.
```

### Relationship Hints

Short explanations of how adjacent cards connect logically/thematically.

**When generated:**
- Only if `use_ai=true` and guiding question exists
- Batched: all hints generated in one API call
- Cached per card-pair hash (TTL: 5 minutes)

**Prompt template:**

```
Given this guiding question: "{guiding_question}"

And these consecutive cards from an AI response:

Card A ({header_a}):
{body_a[:500]}

Card B ({header_b}):
{body_b[:500]}

Write ONE sentence (max 25 words) explaining how Card A leads to Card B 
and how both relate to the guiding question. Focus on logical/thematic 
connection, not summarization.
```

### AI Client Detection

```python
def get_ai_client():
    """Returns (client, client_type) or (None, None)"""
    # Priority: Anthropic > OpenAI
    if os.getenv('ANTHROPIC_API_KEY'):
        return Anthropic(), 'anthropic'
    if os.getenv('OPENAI_API_KEY'):
        return OpenAI(), 'openai'
    return None, None
```

### Caching

**⚠️ Per-process only** — Cache is not persisted across restarts or shared between workers.

```python
# In-memory cache with TTL
_ai_cache = {}  # key -> (value, expiry_timestamp)
AI_CACHE_TTL = 300  # 5 minutes

def cache_get(key: str) -> Optional[str]:
    if key in _ai_cache:
        value, expiry = _ai_cache[key]
        if time.time() < expiry:
            return value
        del _ai_cache[key]
    return None
```

---

## Per-Card Comments

### Data Model

```python
class CardComment(db.Model):
    __tablename__ = 'card_comment'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chat.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)
    message_id = Column(Integer, ForeignKey('message.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    card_key = Column(String(40), nullable=False)      # SHA1 hash
    segment_index = Column(Integer, nullable=False)
    segment_body_hash = Column(String(16), nullable=True)  # MD5 prefix
    
    content = Column(Text, nullable=False)
    content_type = Column(String(4), default='user')   # 'user' or 'ai'
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    deleted_at = Column(DateTime, nullable=True)       # Soft delete
```

### Card Key Generation

```python
def generate_card_key(message_id: int, segment_index: int, segment_body: str) -> str:
    """Stable identifier: SHA1(message_id:segment_index:body[:200])"""
    content = f"{message_id}:{segment_index}:{segment_body[:200]}"
    return hashlib.sha1(content.encode()).hexdigest()
```

### Mismatch Detection

If segmentation changes (e.g., AI regenerates cards), the `segment_body_hash` may no longer match:

```python
def generate_body_hash(segment_body: str) -> str:
    """MD5 prefix for quick comparison"""
    return hashlib.md5(segment_body.encode()).hexdigest()[:16]
```

UI shows a warning banner if hash mismatch is detected.

### Indexes

```sql
CREATE INDEX ix_card_comment_card_key ON card_comment(card_key);
CREATE INDEX ix_card_comment_chat_card_created ON card_comment(chat_id, card_key, created_at);
CREATE INDEX ix_card_comment_user_created ON card_comment(user_id, created_at);
```

---

## AI Reply Feature

Allows AI to generate comments on specific cards, fostering discussion.

### Consecutive Guard

**Rule:** Max 2 consecutive AI replies per user per card.

```python
@classmethod
def count_consecutive_ai_for_user(cls, card_key: str, user_id: int, 
                                   limit: int = 2, chat_id: int = None) -> int:
    """Count consecutive AI comments by this user (most recent first)"""
    query = cls.query.filter(
        cls.card_key == card_key,
        cls.user_id == user_id,
        cls.deleted_at.is_(None)
    )
    if chat_id:
        query = query.filter(cls.chat_id == chat_id)
    
    recent = query.order_by(cls.created_at.desc()).limit(limit).all()
    
    count = 0
    for comment in recent:
        if comment.is_ai:
            count += 1
        else:
            break  # Streak broken by user comment
    return count
```

### AI Reply Prompt

```python
AI_REPLY_SYSTEM_PROMPT = """You are a thoughtful learning companion participating 
in a discussion about educational content. Your role is to:
- Ask clarifying questions that deepen understanding
- Offer brief insights that connect ideas
- Encourage critical thinking without lecturing

Context:
- Room goals: {room_goals}
- Chat purpose: {chat_purpose}
- Guiding question: {guiding_question}

Card being discussed:
Header: {card_header}
Content: {card_body}

Recent discussion:
{recent_comments}

Write a SHORT comment (1 paragraph or ≤5 bullets, max 150 words). Be conversational, 
not preachy. If asking a question, make it specific and thought-provoking.
"""
```

### Response Cleaning

```python
def _clean_ai_reply(text: str) -> str:
    """Remove preambles, normalize bullets, trim length"""
    # Remove "Here's a comment:" type prefixes
    preambles = ["Here's", "My comment:", "Comment:", ...]
    for p in preambles:
        if text.startswith(p):
            text = text[len(p):].lstrip(": ")
    
    # Normalize bullet styles
    text = re.sub(r'^[•◦▪]\s*', '- ', text, flags=re.MULTILINE)
    
    # Hard cap
    if len(text) > AI_REPLY_MAX_CHARS:
        text = text[:AI_REPLY_MAX_CHARS] + '...'
    
    return text.strip()
```

### Rate Limits

| Endpoint | Limit |
|----------|-------|
| POST `.../comments` (human) | 30/minute |
| POST `.../comments/ai` | 5/minute |
| GET `.../comments` | 60/minute |

---

## UI/UX Design

### Card Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ 🎯 Guiding Question: What are the key principles of...?        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ▼ Introduction to Concepts                              💬 3   │
├─────────────────────────────────────────────────────────────────┤
│ Card body content here...                                       │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 💬 Comments (3)                                             │ │
│ │ ┌─────────────────────────────────────────────────────────┐ │ │
│ │ │ 👤 Alice: Great point about...                          │ │ │
│ │ │ 🤖 AI: Have you considered...                           │ │ │
│ │ │ 👤 Bob: I agree, but...                                 │ │ │
│ │ └─────────────────────────────────────────────────────────┘ │ │
│ │ [Add comment...] [🧠 AI Reply]                              │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │    Next     │  ← Connector button
                    │      ▼      │
                    └─────────────┘
                    ┌─────────────────────────────────────┐
                    │ 💡 This leads to the next concept   │  ← Popover
                    │    by building on...                │
                    └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ▼ Core Implementation                                   💬 1   │
├─────────────────────────────────────────────────────────────────┤
│ ...                                                             │
└─────────────────────────────────────────────────────────────────┘
```

### Connector Button ("Next" Pill)

| Property | Desktop | Mobile |
|----------|---------|--------|
| Max-width | 120px | Full width |
| Height | 40px | 40px |
| Position | Centered, overlaps cards by 12px | In-flow, no overlap |
| Popover | Floating, centered | Inline expand |

### Interactions

| Action | Result |
|--------|--------|
| Click "Next" | Scrolls to + expands + focuses next card; toggles popover |
| Enter/Space on "Next" | Same as click |
| Click outside popover | Closes popover |
| Escape | Closes any open popover |
| Click card header | Toggles card expand/collapse |

### Collapsible Cards

- **Chevron** controls both body AND comments section
- **Collapsed state**: Only header + comment count badge visible
- **Expanded state**: Full body + scrollable comments list

### Comments Section

- Max-height: 200px (desktop), 150px (mobile)
- Scrollable when overflow
- Lazy-loaded on first card expand

---

## Accessibility

### ARIA Attributes

| Element | Attributes |
|---------|------------|
| Card header | `role="button"`, `tabindex="0"`, `aria-expanded`, `aria-label` |
| Connector button | `aria-label="Next: Card N — show connection"`, `aria-expanded` (only if hint) |
| Popover | `role="tooltip"`, `aria-hidden` |
| Comments section | `aria-live="polite"` for new comments |

### Keyboard Navigation

| Key | Action |
|-----|--------|
| Tab | Move between focusable elements |
| Enter/Space | Activate buttons, toggle cards |
| Escape | Close popover |

### Screen Reader Announcements

- Card count: "Card 1 of 5"
- Expand/collapse state changes
- New comment additions
- AI reply generation status

---

## API Reference

### Segmentation Endpoint

```
POST /api/dev/card-segments
Content-Type: application/json
```

**Request:**

```json
{
  "text": "Long AI response text...",
  "use_ai": true,
  "message_id": 123
}
```

**Response:**

```json
{
  "segments": [
    {
      "header": "Introduction",
      "body": "Content here...",
      "type": "text",
      "confidence": 0.85,
      "is_complete": true,
      "card_key": "abc123...",
      "body_hash": "def456..."
    }
  ],
  "guiding_question": "What are the key principles of...?",
  "relationships": [
    "Card 1 introduces the concept that Card 2 then explores..."
  ],
  "is_complete": true,
  "segment_count": 5
}
```

### Comments Endpoints

```
GET    /chat/<chat_id>/cards/<card_key>/comments?after=<cursor>&limit=20
POST   /chat/<chat_id>/cards/<card_key>/comments
DELETE /chat/<chat_id>/cards/<card_key>/comments/<comment_id>
POST   /chat/<chat_id>/cards/<card_key>/comments/ai
GET    /chat/<chat_id>/cards/<card_key>/comments/count
POST   /api/card-comments/bulk-counts
```

### Preview Page

```
GET /api/dev/card-preview
```

Dev-only page for testing segmentation. Guarded by `FLASK_ENV != 'production'`.

---

## Configuration & Limits

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | — | Primary AI provider |
| `OPENAI_API_KEY` | — | Fallback AI provider |
| `FLASK_ENV` | `production` | Must be non-production for dev endpoints |

### Segmentation Limits

| Limit | Value |
|-------|-------|
| Min segments | 3 |
| Max segments | 9 |
| Min segment chars | 100 |
| Max header length | 60 chars |

### AI Limits

| Limit | Value |
|-------|-------|
| Guiding question max tokens | 50 |
| Relationship hint max tokens | 60 |
| AI reply max tokens | 250 |
| AI reply max chars | 1,500 |
| Cache TTL | 5 minutes |

### Rate Limits

| Endpoint | Limit |
|----------|-------|
| Card segments | 10/minute |
| Human comments | 30/minute |
| AI comments | 5/minute |
| Read comments | 60/minute |

---

## Known Limitations

### Caching

- **Per-process only**: Cache not shared between workers or persisted
- **No cache invalidation**: Stale data possible after TTL expires
- Recommended: Add Redis for production

### Card Key Stability

- If segmentation algorithm changes, existing `card_key` values may orphan comments
- Mitigation: `segment_body_hash` detects mismatches, shows warning

### AI Dependencies

- No AI fallback for segmentation itself (only headers)
- Rate limits shared across all users
- No retry logic for transient failures

### Mobile

- Popover becomes inline expand (less elegant)
- No horizontal scroll for code blocks

---

## Future Enhancements

### P0 (High Priority)

- [ ] Redis caching for multi-worker deployments
- [ ] Card key migration tool for algorithm changes
- [ ] Retry logic for AI failures

### P1 (Medium Priority)

- [ ] Threaded comments (parent_id support exists in schema)
- [ ] Comment editing (currently create/delete only)
- [ ] Real-time updates via WebSocket
- [ ] Comment reactions (👍 👎 🤔)

### P2 (Nice to Have)

- [ ] Export cards as PDF/Markdown
- [ ] Custom segmentation rules per room
- [ ] AI-suggested follow-up questions per card
- [ ] Reading progress tracking
- [ ] Bookmark individual cards

---

## Appendix: Test Coverage

```
tests/
├── test_card_view.py          # 45 tests - Segmentation logic
├── test_card_view_api.py      # 12 tests - API endpoints
└── test_card_comments_api.py  # 32 tests - Comments + AI Reply
```

**Total: 89 tests passing**

Key test scenarios:
- Segment count constraints (3–9)
- Code block preservation
- Header generation heuristics
- Tiny card merging
- Truncation detection
- AI fallback behavior
- Comment CRUD operations
- Consecutive AI guard
- Rate limiting
- Access control

---

*Document generated from Card View implementation, December 2024.*


