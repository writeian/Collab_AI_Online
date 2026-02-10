# Card View Testing Guide

## Quick Start

### 1. Setup Environment

```bash
cd /Users/iread-mba/Collab_AI_Online

# Activate virtual environment
source .venv/bin/activate

# Set required environment variables
export CARD_VIEW_DEV_ENABLED=true
export FLASK_ENV=development
export DATABASE_URL="sqlite:///$(pwd)/instance/ai_collab.db"

# Optional: For real API testing (requires Anthropic key)
export ANTHROPIC_API_KEY="your-anthropic-key-here"
```

Or add to `.env` file:
```
CARD_VIEW_DEV_ENABLED=true
FLASK_ENV=development
ANTHROPIC_API_KEY=your-key-here
```

### 2. Start the Server

```bash
# Option 1: Flask CLI (port 5001)
flask run --port 5001 --host 127.0.0.1

# Option 2: Python run.py (port 5000)
python run.py

# Option 3: Start script
./START_APP.sh
```

### 3. Create Test User (If Needed)

If you don't have an account yet, create a test user:

```bash
# Create default test user
python scripts/create_test_user.py

# Or create custom user
python scripts/create_test_user.py myusername my@email.com mypassword "My Name"
```

**Default Test Credentials:**
- **Username:** `testuser`
- **Email:** `test@example.com`
- **Password:** `testpass123`

### 4. Sign In

1. Navigate to: `http://127.0.0.1:5001/auth/login` (or `5000` if using run.py)
2. Sign in with your account (required for dev endpoints)
3. Or register a new account at: `http://127.0.0.1:5001/auth/register`

## Testing Modes

### Mode 1: Simulation Mode (No Real API)

**URL:** `http://127.0.0.1:5001/api/dev/card-preview`

**What to Test:**
- ✅ Grid layout renders cards
- ✅ Click card opens overlay
- ✅ Navigation (arrows, keyboard, swipe)
- ✅ Comments simulation (in-memory only)
- ✅ AI reply simulation
- ✅ Deep linking (`#card=<key>`)
- ✅ Mobile gestures

**Limitations:**
- Comments are in-memory only (lost on page refresh)
- AI replies are simulated (not real API calls)

### Mode 2: Real API Mode (With Chat Context)

**URL:** `http://127.0.0.1:5001/api/dev/card-preview?chat_id=123&message_id=456`

**Requirements:**
- Must have a valid `chat_id` from an existing chat
- Must have a valid `message_id` from that chat
- Must be signed in
- `CARD_VIEW_DEV_ENABLED=true` must be set

**What to Test:**
- ✅ Real API calls to `/chat/<chat_id>/cards/<card_key>/comments`
- ✅ Real AI replies via Anthropic API
- ✅ Comments persist to database
- ✅ All simulation features still work

**⚠️ WARNING:** Comments will be saved to the database tied to the specified chat/message, even though preview content may be unrelated. Only use with test chats!

## Step-by-Step Testing Checklist

### Phase 1: Basic Functionality

#### 1.1 Grid Layout
- [ ] Navigate to `/api/dev/card-preview`
- [ ] Paste sample text (or use "Load Sample" button)
- [ ] Click "Segment" button
- [ ] Verify grid shows cards (2-4 per row depending on screen size)
- [ ] Verify each card shows: number, header, snippet
- [ ] Verify cards are clickable

#### 1.2 Overlay Opening
- [ ] Click a card in the grid
- [ ] Verify overlay opens (full-screen dark backdrop)
- [ ] Verify card content displays (header + body)
- [ ] Verify indicator shows "Card X of Y"
- [ ] Verify close button (X) is visible
- [ ] Click close button → overlay closes
- [ ] Press ESC key → overlay closes
- [ ] Click backdrop → overlay closes

#### 1.3 Navigation
- [ ] Open overlay on first card
- [ ] Click "Next" button → navigates to second card
- [ ] Click "Previous" button → navigates back to first card
- [ ] Press Arrow Right → next card
- [ ] Press Arrow Left → previous card
- [ ] Test wrap-around: Last card → Next → First card
- [ ] Test wrap-around: First card → Previous → Last card

### Phase 2: Comments (Simulation Mode)

#### 2.1 Desktop Comments Pane
- [ ] Open overlay (desktop viewport >768px)
- [ ] Verify comments pane visible on right side
- [ ] Verify comments count shows "0"
- [ ] Type comment in textarea
- [ ] Press Enter → comment submits
- [ ] Verify comment appears in list
- [ ] Verify count updates to "1"
- [ ] Verify comment shows: author, content, timestamp
- [ ] Add multiple comments → all persist

#### 2.2 Mobile Comments Sheet
- [ ] Open overlay (mobile viewport <768px)
- [ ] Verify comments toggle button in card footer
- [ ] Click "Comments" button → sheet slides up
- [ ] Verify comments list visible
- [ ] Add comment via mobile composer
- [ ] Verify comment appears
- [ ] Swipe down on sheet header → sheet dismisses
- [ ] Verify count updates on toggle button

#### 2.3 AI Reply (Simulation)
- [ ] Add a comment
- [ ] Click "AI" button
- [ ] Verify loading skeleton appears
- [ ] Verify simulated AI reply appears after ~1.5s
- [ ] Verify AI comment has purple styling
- [ ] Verify sparkles icon on AI comments
- [ ] Try 3 AI replies in a row → should show guard message

### Phase 3: Real API Mode

#### 3.1 Setup Real API Context
```bash
# Get a chat_id and message_id from your database or UI
# Example: Navigate to a chat, note the chat_id from URL
# Example: Note a message_id from the chat
```

#### 3.2 Test Real API Calls
- [ ] Navigate to: `/api/dev/card-preview?chat_id=123&message_id=456`
- [ ] Verify warning banner shows (yellow)
- [ ] Paste text and segment
- [ ] Open overlay
- [ ] Check browser Network tab → should see GET `/chat/123/cards/<key>/comments`
- [ ] Verify comments load from API (if any exist)
- [ ] Add a comment → check Network tab → should see POST request
- [ ] Verify comment persists (refresh page, reopen card)
- [ ] Request AI reply → check Network tab → should see POST to `/comments/ai`
- [ ] Verify real AI reply appears (from Anthropic)

#### 3.3 Test Without message_id
- [ ] Navigate to: `/api/dev/card-preview?chat_id=123` (no message_id)
- [ ] Verify warning shows "no message_id - will use simulation"
- [ ] Add comment → should use simulation (no API call)
- [ ] Request AI reply → should use simulation

### Phase 4: Mobile Gestures

#### 4.1 Card Carousel Swipe
- [ ] Open overlay on mobile device (or browser mobile emulation)
- [ ] Swipe left on card → navigates to next card
- [ ] Swipe right on card → navigates to previous card
- [ ] Verify vertical scrolling still works (doesn't trigger swipe)
- [ ] Test rapid swipes → should respect debounce

#### 4.2 Comments Sheet Swipe
- [ ] Open comments sheet on mobile
- [ ] Swipe down on header → sheet dismisses
- [ ] Swipe down on drag handle → sheet dismisses
- [ ] Swipe down on upper 20% of sheet → sheet dismisses
- [ ] Swipe down on lower 80% of sheet → scrolls comments (doesn't dismiss)
- [ ] Verify scrolling works normally in comments list

### Phase 5: Deep Linking

#### 5.1 Hash Navigation
- [ ] Segment text to create cards
- [ ] Open overlay on card 3
- [ ] Verify URL hash: `#card=<40-char-key>`
- [ ] Copy URL with hash
- [ ] Close overlay
- [ ] Paste URL in new tab → overlay opens to correct card
- [ ] Use browser back button → overlay closes
- [ ] Use browser forward button → overlay reopens

#### 5.2 Hash Updates
- [ ] Navigate to card 1
- [ ] Note hash in URL
- [ ] Navigate to card 2 → hash updates
- [ ] Navigate to card 3 → hash updates
- [ ] Verify hash always matches current card

### Phase 6: Accessibility

#### 6.1 Keyboard Navigation
- [ ] Tab through overlay → focus stays within overlay
- [ ] Tab on last element → wraps to first element
- [ ] Shift+Tab on first element → wraps to last element
- [ ] Arrow keys navigate cards
- [ ] ESC closes overlay
- [ ] Enter/Space on grid cards opens overlay

#### 6.2 Screen Reader
- [ ] Enable screen reader (VoiceOver, NVDA, etc.)
- [ ] Open overlay → should announce "Opened card X of Y: [header]"
- [ ] Navigate cards → should announce each card
- [ ] Add comment → should announce success/error
- [ ] Close overlay → should announce "Card overlay closed"

### Phase 7: Error Handling

#### 7.1 Network Errors
- [ ] Disconnect network (or block requests in DevTools)
- [ ] Try to load comments → should show friendly error
- [ ] Try to add comment → should show error message
- [ ] Try AI reply → should show error message
- [ ] Verify screen reader announces errors

#### 7.2 Invalid Context
- [ ] Navigate with invalid `chat_id`: `/api/dev/card-preview?chat_id=99999`
- [ ] Should fall back to simulation mode
- [ ] Navigate without `message_id`: `/api/dev/card-preview?chat_id=123`
- [ ] Should show warning and use simulation

## Sample Test Data

### Short Text (2-3 cards)
```
Introduction to Machine Learning

Machine learning is a subset of artificial intelligence. It enables computers to learn from data without explicit programming.

Key Concepts:
- Supervised learning uses labeled data
- Unsupervised learning finds patterns
- Reinforcement learning learns from rewards
```

### Long Text (5-7 cards)
```
Understanding Neural Networks

Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) organized in layers.

Architecture:
- Input layer receives data
- Hidden layers process information
- Output layer produces results

Training Process:
1. Forward propagation passes data through network
2. Loss calculation measures prediction error
3. Backpropagation adjusts weights
4. Iteration repeats until convergence

Applications:
- Image recognition
- Natural language processing
- Speech recognition
- Autonomous vehicles

Challenges:
- Requires large datasets
- Computationally expensive
- Black box problem (interpretability)
- Overfitting risks
```

## Browser DevTools Testing

### Network Tab
- [ ] Check API calls when using real API mode
- [ ] Verify CSRF token in headers
- [ ] Verify JSON request/response format
- [ ] Check for failed requests (should show friendly errors)

### Console Tab
- [ ] Check for JavaScript errors
- [ ] Verify warnings about data mismatch (real API mode)
- [ ] Check preload debug messages
- [ ] Verify focus trap updates

### Mobile Emulation
- [ ] Chrome DevTools → Toggle device toolbar
- [ ] Test iPhone/Android viewports
- [ ] Test swipe gestures
- [ ] Test touch interactions

## Common Issues & Solutions

### Issue: Preview page shows 403 Forbidden
**Solution:**
- Verify `CARD_VIEW_DEV_ENABLED=true` in environment
- Verify you're signed in
- Check `FLASK_ENV=development` is set

### Issue: Comments don't load
**Solution:**
- Check Network tab for API errors
- Verify `chat_id` and `message_id` are valid
- Check browser console for errors
- Verify CSRF token is present

### Issue: Swipe gestures don't work
**Solution:**
- Verify mobile viewport (<768px)
- Check browser console for errors
- Verify `touch-action: none` is applied
- Test on actual mobile device (not just emulation)

### Issue: Focus trap doesn't work
**Solution:**
- Check browser console for errors
- Verify `updateFocusTrapElements()` is called
- Check that focusable elements exist in overlay
- Test with keyboard (Tab key)

### Issue: AI replies don't work
**Solution:**
- Verify `ANTHROPIC_API_KEY` is set
- Check Network tab for API errors
- Verify real API mode is enabled (`message_id` present)
- Check rate limits (max 5 per minute)

## Performance Testing

### Test Preloading
- [ ] Open overlay on card 2
- [ ] Check Network tab → should see preload requests for cards 1 and 3
- [ ] Navigate to card 3 → should load instantly (no skeleton)
- [ ] Navigate to card 1 → should load instantly

### Test Debouncing
- [ ] Rapidly press Arrow Right key
- [ ] Verify only one navigation per 150ms
- [ ] Verify animations don't conflict
- [ ] Verify no errors in console

### Test Large Card Sets
- [ ] Paste very long text (50+ cards)
- [ ] Verify grid renders efficiently
- [ ] Verify navigation is smooth
- [ ] Check memory usage (should be reasonable)

## Checklist Summary

### Core Features
- [ ] Grid layout (2-4 cards per row)
- [ ] Overlay opens/closes
- [ ] Card navigation (buttons, keyboard, swipe)
- [ ] Wrap-around navigation
- [ ] Deep linking (`#card=<key>`)
- [ ] Browser back/forward support

### Comments
- [ ] Desktop comments pane
- [ ] Mobile comments sheet
- [ ] Add comment (simulation & real API)
- [ ] AI reply (simulation & real API)
- [ ] Comment persistence
- [ ] Comment counts update

### Mobile
- [ ] Swipe left/right for cards
- [ ] Swipe down to dismiss sheet
- [ ] Touch interactions work
- [ ] Vertical scrolling preserved

### Accessibility
- [ ] Keyboard navigation
- [ ] Focus trap
- [ ] Screen reader announcements
- [ ] ARIA attributes

### Error Handling
- [ ] Network errors handled gracefully
- [ ] Invalid context falls back to simulation
- [ ] User-friendly error messages
- [ ] Screen reader error announcements

## Next Steps

After testing:
1. Review any console errors
2. Test on actual mobile device
3. Verify real API mode with test chat
4. Check performance with large card sets
5. Test edge cases (empty text, single card, etc.)

