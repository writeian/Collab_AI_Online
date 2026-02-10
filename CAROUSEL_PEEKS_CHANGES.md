# Carousel Peeks Implementation - Specific Code Changes

## Summary
Re-enabled peek cards with proper positioning, added max-width constraints, and ensured peeks are hidden at first/last cards.

---

## File 1: `src/app/static/css/dev/card-overlay.css`

### Change 1: Shell Max-Width and Centering (Lines ~1287-1334)

**Location**: Inside `@media (min-width: 768px)` block for `.cv-overlay-shell`

**Added**:
```css
.cv-overlay-shell {
    /* ... existing styles ... */
    max-width: 1600px;  /* NEW: Cap width on large screens */
    margin: 0 auto;      /* NEW: Center on wide viewports */
}
```

**Changed**:
```css
.cv-overlay-card-column {
    /* ... existing styles ... */
    padding: 0 40px; /* NEW: Space for peeks */
}

.cv-overlay-card-column .cv-overlay-card {
    max-width: 1100px; /* CHANGED: Was 1200px, tightened for XL screens */
    /* ... rest unchanged ... */
}
```

---

### Change 2: Re-enabled Peek Cards (Lines ~595-628)

**Location**: `.cv-overlay-card-peek` block

**Changed from**:
```css
/* Temporarily hide peeks to verify layout */
.cv-overlay-card-peek {
    display: none !important;
    /* ... */
}
```

**Changed to**:
```css
/* Peek Cards - Re-enabled with contained positioning */
.cv-overlay-card-peek {
    display: none !important; /* Hidden on mobile */
    position: absolute;
    width: 80px;
    max-width: 80px;  /* NEW: Explicit max-width */
    height: 80%;
    opacity: 0.35;    /* CHANGED: Was 0.4, now 0.35 */
    pointer-events: none;
    z-index: 1;       /* Under card/comments */
}

@media (min-width: 768px) {
    .cv-overlay-card-peek {
        display: block !important; /* CHANGED: Re-enabled on desktop */
    }
    
    .cv-overlay-card-peek-prev {
        left: -40px;      /* CHANGED: Was left: 0; transform: translateX(-40px) */
        transform: none; /* NEW: Removed transform */
    }
    
    .cv-overlay-card-peek-next {
        right: -40px;     /* CHANGED: Was right: 24px; transform: translateX(40px) */
        transform: none; /* NEW: Removed transform */
    }
}

@media (max-width: 767px) {
    .cv-overlay-card-peek {
        display: none !important; /* Explicit mobile hide */
    }
}
```

---

### Change 3: Card Column Padding (Line ~1304)

**Location**: Inside `@media (min-width: 768px)` for `.cv-overlay-card-column`

**Added**:
```css
.cv-overlay-card-column {
    /* ... existing styles ... */
    padding: 0 40px; /* NEW: Space for peeks */
}
```

---

### Change 4: Card Max-Width Tightened (Line ~1316)

**Location**: Inside `@media (min-width: 768px)` for `.cv-overlay-card-column .cv-overlay-card`

**Changed**:
```css
.cv-overlay-card-column .cv-overlay-card {
    max-width: 1100px; /* CHANGED: Was 1200px, tightened for XL screens */
    /* ... rest unchanged ... */
}
```

---

## File 2: `src/app/static/js/dev/card-overlay.js`

### Change 1: hidePeek Function (Lines ~1074-1080)

**Location**: Before `renderPeekCards()` function

**Code**:
```javascript
/**
 * Hide a peek card and clear its content
 */
function hidePeek(dir) {
    const el = document.getElementById(`cv-overlay-card-${dir}`);
    if (el) {
        el.style.display = 'none';
        el.innerHTML = '';  // NEW: Clear content when hiding
    }
}
```

**Note**: This function already existed but now explicitly clears `innerHTML`.

---

### Change 2: renderPeekCards Function (Lines ~1087-1115)

**Location**: After `hidePeek()` function

**Code**:
```javascript
function renderPeekCards() {
    const prevPeek = document.getElementById('cv-overlay-card-prev');
    const nextPeek = document.getElementById('cv-overlay-card-next');
    
    // Hide peeks on mobile, when only 1 card, or viewport < 768px
    if (window.innerWidth < 768 || state.cards.length <= 1) {
        hidePeek('prev');
        hidePeek('next');
        return;
    }
    
    // Desktop: render peek cards (NO WRAP-AROUND)
    const isFirst = state.currentCardIndex === 0;
    const isLast = state.currentCardIndex === state.cards.length - 1;
    
    // Hide prev peek on first card, show on others
    if (isFirst) {
        hidePeek('prev');
    } else {
        renderPeekCard('prev', state.currentCardIndex - 1);
    }
    
    // Hide next peek on last card, show on others
    if (isLast) {
        hidePeek('next');
    } else {
        renderPeekCard('next', state.currentCardIndex + 1);
    }
}
```

**Note**: Function already existed with this logic. No changes needed - it already calls `hidePeek()` which clears content.

---

### Change 3: renderPeekCards() Calls

**Location**: Multiple locations

**Verified calls exist at**:
- Line ~797: In `openCard()` function - after `renderCard()`
- Line ~888: In `navigateToCard()` function - after `renderCard()`
- Line ~1245: In `renderCard()` function - at end
- Line ~122: In resize handler - debounced

**No changes needed** - all calls already in place.

---

## File 3: `templates/dev/card_preview.html`

### Change: Cache-Busting Version Update (Lines ~114-117)

**Changed from**:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/dev/card-overlay.css') }}?v=9">
<script src="{{ url_for('static', filename='js/dev/card-overlay.js') }}?v=5"></script>
```

**Changed to**:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/dev/card-overlay.css') }}?v=10">
<script src="{{ url_for('static', filename='js/dev/card-overlay.js') }}?v=6"></script>
```

---

## Summary of Specific Changes

### CSS Changes (`card-overlay.css`):

1. **Line ~1289**: Added `max-width: 1600px;` to `.cv-overlay-shell`
2. **Line ~1290**: Added `margin: 0 auto;` to `.cv-overlay-shell`
3. **Line ~1304**: Added `padding: 0 40px;` to `.cv-overlay-card-column`
4. **Line ~1316**: Changed `max-width: 1200px` to `max-width: 1100px` for `.cv-overlay-card-column .cv-overlay-card`
5. **Line ~599**: Changed `display: none !important` to `display: block !important` for `.cv-overlay-card-peek` on desktop
6. **Line ~600**: Added `max-width: 80px;` to `.cv-overlay-card-peek`
7. **Line ~603**: Changed `opacity: 0.4` to `opacity: 0.35` for `.cv-overlay-card-peek`
8. **Line ~614**: Changed `left: 0; transform: translateX(-40px)` to `left: -40px; transform: none` for `.cv-overlay-card-peek-prev`
9. **Line ~619**: Changed `right: 24px; transform: translateX(40px)` to `right: -40px; transform: none` for `.cv-overlay-card-peek-next`

### JavaScript Changes (`card-overlay.js`):

1. **Line ~1078**: `hidePeek()` function already clears `innerHTML` - no change needed
2. **Lines ~1087-1115**: `renderPeekCards()` function already has correct logic - no change needed
3. **All renderPeekCards() calls**: Already in place - no changes needed

### HTML Changes (`card_preview.html`):

1. **Line ~114**: Changed CSS version from `?v=9` to `?v=10`
2. **Line ~117**: Changed JS version from `?v=5` to `?v=6`

---

## Key Behavioral Changes

1. **Shell max-width**: Carousel now caps at 1600px and centers on very wide screens
2. **Card max-width**: Reduced from 1200px to 1100px for tighter layout on XL screens
3. **Peeks re-enabled**: Changed from `display: none !important` to `display: block !important` on desktop
4. **Peeks positioning**: Now use `left: -40px` and `right: -40px` with `transform: none` (simpler positioning)
5. **Card column padding**: Added `padding: 0 40px` to make room for peeks
6. **Peeks opacity**: Reduced from 0.4 to 0.35 for more subtle appearance
7. **Peeks max-width**: Explicitly set to 80px (was implicit 100px)

---

## Verification Checklist

- [x] Shell has `max-width: 1600px` and `margin: 0 auto`
- [x] Card column has `padding: 0 40px`
- [x] Card has `max-width: 1100px`
- [x] Peeks have `display: block !important` on desktop (≥768px)
- [x] Peeks positioned at `left: -40px` and `right: -40px`
- [x] Peeks have `max-width: 80px` and `opacity: 0.35`
- [x] Peeks hidden on mobile (`display: none !important` at ≤767px)
- [x] `hidePeek()` clears `innerHTML`
- [x] `renderPeekCards()` hides peeks on first/last cards
- [x] Cache-busting versions updated


