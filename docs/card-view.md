# Card View Feature Documentation

## Overview

Card View transforms long AI responses into structured, digestible learning units. Instead of presenting a multi-paragraph response as one scroll block, Card View:

- Breaks messages into 3–9 coherent segments (cards)
- Provides headers for each card for progressive disclosure
- Optionally adds AI-generated guiding questions and relationship hints
- Supports collaborative exploration of complex AI responses

## Architecture

```
src/utils/card_view/
├── __init__.py          # Exports: segment_message, Segment, enhance_segments_with_ai
├── schemas.py           # Segment dataclass with serialization
├── detector.py          # Structure detection (bullets, prose, code)
├── headers.py           # Header generation and normalization
├── segmenter.py         # Core segmentation logic
├── prompts.py           # AI prompt templates
└── ai_helpers.py        # AI-powered enhancements (guiding question, hints)

src/app/api/
└── card_view.py         # Dev API blueprint (/api/dev/card-segments)

templates/dev/
└── card_preview.html    # Interactive preview UI
```

## Environment Variables

### API Access Control

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Set to `development` to enable dev API |
| `CARD_VIEW_DEV_ENABLED` | `false` | Explicitly enable dev API in production |
| `ADMIN_EMAILS` | (empty) | Comma-separated admin emails for prod access |

### Caching

| Variable | Default | Description |
|----------|---------|-------------|
| `CARD_VIEW_CACHE_ENABLED` | `true` | Enable/disable in-memory cache |
| `CARD_VIEW_CACHE_TTL` | `300` | Cache TTL in seconds (5 minutes) |

**⚠️ Cache Warning**: The cache is **in-memory and per-process only**.

In multi-worker deployments (e.g., gunicorn with >1 worker):
- Each worker has its own isolated cache
- Cache hits are inconsistent across requests
- `_ai_meta.latency_ms` will vary unpredictably
- Stale results possible if one worker caches, another doesn't

**Recommendations:**
- **Dev/single-worker**: Cache is fine (default: enabled)
- **Multi-worker prod**: Either disable (`CARD_VIEW_CACHE_ENABLED=false`) or implement Redis
- **Testing**: Clear cache between tests to ensure consistency

### AI Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | Anthropic API key for AI features |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-6` | Model for main app (card view helpers temporarily use `claude-haiku-4-5`) |

## API Endpoints

### POST `/api/dev/card-segments`

Segment text into cards with optional AI enhancements.

**Request:**
```json
{
  "text": "Long message to segment...",
  "enhance": true
}
```

**Response:**
```json
{
  "success": true,
  "segment_count": 5,
  "text_length": 1234,
  "segments": [
    {
      "id": "abc123",
      "header": "Introduction to Machine Learning",
      "body": "...",
      "segment_type": "paragraph",
      "is_complete": true,
      "is_truncated": false
    }
  ],
  "guiding_question": "What are the key types of machine learning?",
  "relationships": [
    "Card 2 builds on the introduction by...",
    "Card 3 extends the concept with..."
  ],
  "ai_enhanced": true,
  "_ai_meta": {
    "cache_enabled": true,
    "latency_ms": 450,
    "guiding_question_source": "ai",
    "hints_fallback_count": 0,
    "errors": []
  }
}
```

**Rate Limits:**
- Segmentation only: 30 requests/minute
- With AI enhancement: 10 requests/minute

### GET `/api/dev/card-segments/health`

Health check with cache status.

### POST `/api/dev/card-segments/cache/clear`

Clear the AI response cache (dev only).

### GET `/api/dev/card-preview`

Interactive preview UI for testing segmentation.

## Cost Considerations

### AI Token Usage

Card View AI features use Claude 3 Haiku for cost efficiency:

| Feature | Estimated Tokens | Cost (approx) |
|---------|-----------------|---------------|
| Guiding Question | ~100-200 input, ~50 output | ~$0.0001/call |
| Relationship Hints (per pair) | ~200-400 input, ~30 output | ~$0.0001/call |

For a typical 5-card message:
- 1 guiding question + 4 relationship hints
- ~1,500 input tokens, ~200 output tokens
- **~$0.0005 per message** with AI enhancement

### Optimization Strategies

1. **Caching**: Enabled by default, 5-minute TTL
2. **Batching**: Relationship hints batched in chunks of 8 pairs
3. **Body truncation**: Only first 400 chars of each card sent to AI
4. **Message truncation**: Max 8,000 chars for guiding question

## Testing

```bash
# Run all card view tests
python -m pytest tests/test_card_view.py tests/test_card_view_api.py -v

# Test segmentation only
python -m pytest tests/test_card_view.py -v

# Test API and caching
python -m pytest tests/test_card_view_api.py -v
```

## Usage Examples

### Python (Direct)

```python
from src.utils.card_view import segment_message, enhance_segments_with_ai

# Segment only (fast, no AI)
segments = segment_message(long_message)

# With AI enhancements
segments = segment_message(long_message)
ai_data = enhance_segments_with_ai(long_message, segments)
print(f"Guiding Question: {ai_data['guiding_question']}")
```

### API (curl)

```bash
curl -X POST http://localhost:5001/api/dev/card-segments \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{"text": "Your long message...", "enhance": true}'
```

### Preview UI

Visit `http://localhost:5001/api/dev/card-preview` while logged in.

## Fallback Behavior

When AI is unavailable:

| Feature | Fallback |
|---------|----------|
| Guiding Question | "What is the main point of this message?" |
| Relationship Hints | "These sections are connected thematically." |

The UI shows status messages indicating whether AI responses or fallbacks were used.

## Future Considerations

- **Redis caching**: For production multi-worker deployments
- **AI header generation**: When heuristic headers are weak
- **Comment threading**: Attach comments to individual cards
- **Card reordering**: AI-suggested optimal reading order
- **Summary cards**: AI-generated mini-summaries for long cards

