# AI Token & Context Configuration

## Overview
Control AI response length and conversation context via environment variables.

---

## Environment Variables

**Note:** These settings currently apply to the **Anthropic (Claude) path**. The OpenAI path still defaults to 300 tokens and would need the same environment handling if you switch to it in the future.

### `AI_MAX_TOKENS`
**Default:** `400`  
**Range:** `200-2000`  
**Purpose:** Maximum tokens for AI responses

**Impact:**
- **300 tokens** (old): ~225 words, frequent truncation
- **400 tokens** (new): ~300 words, 60% fewer truncations
- **500 tokens**: ~375 words, minimal truncation (higher cost)

**Example:**
```bash
AI_MAX_TOKENS=400  # Balanced (recommended)
AI_MAX_TOKENS=300  # More concise, more truncation
AI_MAX_TOKENS=500  # Longer responses, higher cost
```

**Cost Impact:**
- 300 → 400 tokens = 33% more API cost
- Worth it for better UX (fewer continue clicks)

---

### `AI_MAX_HISTORY`
**Default:** `8`  
**Range:** `4-20`  
**Purpose:** Number of conversation turns to include as context

**What is a "turn"?**
- 1 turn = 1 user message + 1 assistant response (a pair)
- 8 turns = 16 messages (last 8 user+assistant exchanges)

**Note:** History trimming currently applies to the **Anthropic path only** in `get_ai_response()`. The OpenAI helper doesn't trim context yet.

**Impact:**
- **4 turns**: Minimal context, faster responses, might lose continuity
- **8 turns**: Good balance (recommended)
- **12 turns**: More context, slower responses, better for complex topics
- **20 turns**: Maximum context, expensive, rarely needed

**Example:**
```bash
AI_MAX_HISTORY=8   # Balanced (recommended)
AI_MAX_HISTORY=6   # More concise, less context
AI_MAX_HISTORY=12  # More context for complex discussions
```

**Context Calculation:**
```
Conversation has 20 messages
AI_MAX_HISTORY=8
Last 8 turns = last 16 messages sent to AI
Messages 1-4 are not included (saves tokens)
```

---

## How It Works

### **get_ai_response() Function:**

```python
def get_ai_response(chat, max_tokens=None, ...):
    # Read config
    DEFAULT_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "400"))
    MAX_HISTORY_TURNS = int(os.getenv("AI_MAX_HISTORY", "8"))
    
    # Use provided or default
    if max_tokens is None:
        max_tokens = DEFAULT_MAX_TOKENS
    
    # Fetch all messages
    all_messages = Message.query.filter_by(chat_id=chat.id).all()
    
    # Cap to recent history
    if len(all_messages) > MAX_HISTORY_TURNS * 2:
        messages_payload = all_messages[-(MAX_HISTORY_TURNS * 2):]
        # Saves tokens by not sending full 20+ message history
    else:
        messages_payload = all_messages
    
    # Call API with configured max_tokens
    return call_anthropic_api(messages_payload, system, max_tokens)
```

---

## Tuning Guide

### **If Responses Truncate Too Often:**

**Option 1: Increase max_tokens**
```bash
AI_MAX_TOKENS=450  # or 500
```

**Option 2: Reduce context**
```bash
AI_MAX_HISTORY=6  # Saves tokens for response
```

**Option 3: Both**
```bash
AI_MAX_TOKENS=450
AI_MAX_HISTORY=6
```

---

### **If Responses Lose Context:**

**Option 1: Increase history**
```bash
AI_MAX_HISTORY=12  # More conversation context
```

**Option 2: Implement summarization** (future)
- Summarize messages 1-N
- Keep recent messages N+1 to end
- Best of both worlds

---

### **If API Costs Too High:**

**Option 1: Reduce max_tokens**
```bash
AI_MAX_TOKENS=350
```

**Option 2: Reduce history**
```bash
AI_MAX_HISTORY=6
```

**Option 3: Both**
```bash
AI_MAX_TOKENS=350
AI_MAX_HISTORY=6
```

---

## Monitoring

### **Watch For:**

**Truncation Rate:**
- Check logs for: "⚠️ Response truncated at X tokens"
- Target: <10% truncation rate
- If >20%: Increase `AI_MAX_TOKENS`

**Context Trimming:**
- Check logs for: "📊 Context trimmed: 20 messages → 16"
- If frequent: Consider increasing `AI_MAX_HISTORY`
- Or implement summarization

**API Costs:**
- Monitor Anthropic/OpenAI usage
- Compare before/after changing limits
- Adjust based on budget

---

## Examples

### **Scenario 1: Long Academic Discussion**
```bash
# Need more context for thesis development
AI_MAX_TOKENS=500
AI_MAX_HISTORY=12
```

### **Scenario 2: Quick Q&A Chatbot**
```bash
# Keep responses concise and fresh
AI_MAX_TOKENS=300
AI_MAX_HISTORY=4
```

### **Scenario 3: Balanced Learning (Recommended)**
```bash
# Good for most educational use cases
AI_MAX_TOKENS=400
AI_MAX_HISTORY=8
```

---

## Technical Details

### **Token Estimation:**
- 1 token ≈ 0.75 words (English)
- 400 tokens ≈ 300 words ≈ 1-2 paragraphs

### **Context Window:**
- Claude Sonnet: 200K tokens total
- Our limits are well within capacity
- Focus is on cost and response quality

### **Message History:**
- User message: ~50-200 tokens
- Assistant response: ~200-400 tokens
- 8 turns: ~2000-4000 tokens context
- System prompt: ~200-500 tokens
- **Total sent:** ~2500-5000 tokens per request

---

**Date:** November 27, 2025  
**Version:** 3.1.0  
**Status:** Implemented and configurable

