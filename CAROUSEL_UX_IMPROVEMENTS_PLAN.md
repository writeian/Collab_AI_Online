# Carousel UX Improvements - Complete Implementation Plan

## Overview

Enhance the card overlay carousel with neighbor card peek edges, side navigation buttons, and improved desktop/mobile layouts. This plan incorporates all refinements and risk mitigations.

## Key Refinements Incorporated

1. **Peek elements positioned within card container** (not outside flex)
2. **Comments pane aligned at top** with card
3. **Single-card scenario handling** (hide peeks and side nav)
4. **Narrow desktop overflow prevention** (1024px breakpoint)
5. **Max width on entire carousel** for very large screens
6. **Touch device considerations** (tablets >768px)

## Current Structure

- `.cv-overlay-main`: Flex container (horizontal on desktop)
- `.cv-overlay-card-container`: Flex: 1, centered, width: 60% on desktop
- `.cv-overlay-card`: max-width: 800px, centered
- `.cv-overlay-comments-pane`: width: 40%, hidden on mobile
- `.cv-overlay-nav`: Bottom center buttons

## Implementation Plan

### Phase 1: HTML Structure Changes

**File**: `templates/dev/card_overlay.html`

#### 1.1 Add Peek Card Containers (within card container)

```html
<div class="cv-overlay-card-container">
    <!-- Previous card peek (desktop only) -->
    <div class="cv-overlay-card-peek cv-overlay-card-peek-prev" id="cv-overlay-card-prev">
        <!-- Previous card content rendered here -->
    </div>
    
    <!-- Current card -->
    <div id="cv-overlay-card" class="cv-overlay-card">
        <!-- Card content -->
    </div>
    
    <!-- Next card peek (desktop only) -->
    <div class="cv-overlay-card-peek cv-overlay-card-peek-next" id="cv-overlay-card-next">
        <!-- Next card content rendered here -->
    </div>
</div>
```

**Key Points**:
- Peek elements are **inside** `.cv-overlay-card-container` (not outside flex)
- They will be absolutely positioned within this container
- IDs: `cv-overlay-card-prev` and `cv-overlay-card-next`

#### 1.2 Add Side Navigation Buttons (outside card container, inside overlay content)

```html
<!-- Side navigation (desktop/tablet) - positioned absolutely -->
<button class="cv-overlay-nav-side cv-overlay-nav-side-prev" 
        onclick="CardOverlay.previousCard()"
        aria-label="Previous card"
        id="cv-overlay-nav-side-prev">
    <i data-lucide="chevron-left"></i>
</button>
<button class="cv-overlay-nav-side cv-overlay-nav-side-next"
        onclick="CardOverlay.nextCard()"
        aria-label="Next card"
        id="cv-overlay-nav-side-next">
    <i data-lucide="chevron-right"></i>
</button>

<!-- Bottom navigation (mobile) - keep existing .cv-overlay-nav -->
```

**Key Points**:
- Side nav buttons positioned absolutely on overlay edges
- Bottom nav (`.cv-overlay-nav`) remains for mobile
- Only one nav set visible per breakpoint (CSS handles this)

### Phase 2: CSS Layout Changes

**File**: `src/app/static/css/dev/card-overlay.css`

#### 2.1 Desktop Layout (≥768px)

##### Card Container with Peek Support

```css
@media (min-width: 768px) {
    .cv-overlay-card-container {
        position: relative; /* For absolute positioning of peek cards */
        display: flex;
        align-items: flex-start; /* CRITICAL: Align at top for comments pane alignment */
        justify-content: center;
        gap: 24px; /* Gutter between card and comments */
        padding: 2rem 0; /* Remove horizontal padding for peek */
        overflow: visible; /* CRITICAL: Allow peek cards to extend outside */
        width: auto; /* Remove fixed 60% width */
        flex: 1 1 auto; /* Allow shrinking */
        min-width: 0; /* Prevent flex overflow */
        max-width: calc(100% - 450px - 24px); /* Ensure room for comments + gutter */
    }
}
```

**Key Points**:
- `position: relative` for absolute positioning of peek cards
- `align-items: flex-start` ensures comments pane aligns at top
- `overflow: visible` allows peek cards to extend outside container
- `max-width` calculation ensures room for comments + gutter

##### Current Card with Max-Width (Can Shrink)

```css
@media (min-width: 768px) {
    .cv-overlay-card {
        max-width: 1200px; /* Cap width */
        width: 100%;
        flex-shrink: 1; /* CRITICAL: Allow shrinking if needed */
        position: relative;
        z-index: 2; /* Above peek cards */
    }
}
```

**Key Points**:
- `flex-shrink: 1` allows card to shrink if container is narrow
- `max-width: 1200px` caps width but doesn't force it
- `z-index: 2` ensures card is above peek cards

##### Peek Cards (Positioned Within Container)

```css
.cv-overlay-card-peek {
    display: none; /* Hidden on mobile */
    position: absolute;
    width: 10%; /* 5-10% of container width */
    max-width: 150px; /* Cap peek width */
    height: 80%; /* Match card height proportionally */
    opacity: 0.4; /* Dimmed */
    pointer-events: none; /* CRITICAL: Not clickable, avoid hit-target issues */
    z-index: 1; /* Behind current card */
    transition: opacity 200ms ease-out;
}

@media (min-width: 768px) {
    .cv-overlay-card-peek {
        display: block;
    }
    
    .cv-overlay-card-peek-prev {
        left: 0;
        transform: translateX(-20%); /* Slight offset */
    }
    
    .cv-overlay-card-peek-next {
        right: 0;
        transform: translateX(20%); /* Slight offset */
    }
}

/* Hide peek cards when only one card exists */
.cv-overlay-card-container:has(.cv-overlay-card:only-child) .cv-overlay-card-peek {
    display: none;
}
```

**Key Points**:
- `pointer-events: none` prevents hit-target issues
- Absolutely positioned within container (not affecting flex)
- CSS `:has()` selector hides peeks when only one card
- Fallback: JavaScript will also handle single-card scenario

##### Comments Pane Fixed Width (Aligned at Top)

```css
@media (min-width: 768px) {
    .cv-overlay-comments-pane {
        width: 450px; /* Fixed width */
        flex-shrink: 0; /* Don't shrink */
        min-width: 450px; /* Enforce minimum */
        align-self: flex-start; /* CRITICAL: Align at top with card */
    }
}
```

**Key Points**:
- Fixed width: `450px` (not percentage)
- `align-self: flex-start` ensures top alignment with card
- `flex-shrink: 0` prevents unwanted shrinking

##### Narrow Desktop Overflow Prevention (768-1024px)

```css
/* Ensure main container doesn't overflow on narrow desktops */
@media (min-width: 768px) and (max-width: 1024px) {
    .cv-overlay-main {
        overflow-x: hidden; /* Prevent horizontal scroll */
    }
    
    .cv-overlay-card-container {
        max-width: calc(100% - 450px - 24px); /* Comments + gutter */
    }
    
    .cv-overlay-card {
        max-width: calc(100vw - 450px - 24px - 4rem); /* Account for padding */
    }
}
```

**Key Points**:
- Prevents horizontal scroll on narrow desktops (~1024px)
- Ensures card + comments + gutter fit within viewport
- Accounts for padding in calculations

##### Max Width on Entire Carousel (Very Large Screens)

```css
@media (min-width: 1600px) {
    .cv-overlay-main {
        max-width: 1800px; /* Cap entire carousel width */
        margin: 0 auto; /* Center on very large screens */
    }
}
```

**Key Points**:
- Prevents side buttons from being too far away
- Centers carousel on very large screens
- Maintains reasonable proportions

##### Side Navigation Buttons

```css
.cv-overlay-nav-side {
    display: none; /* Hidden on mobile */
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    z-index: 10; /* Above cards */
    width: 56px;
    height: 56px;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    color: white;
    cursor: pointer;
    transition: all 200ms ease-out;
}

@media (min-width: 768px) {
    .cv-overlay-nav-side {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .cv-overlay-nav-side-prev {
        left: 1rem;
    }
    
    .cv-overlay-nav-side-next {
        right: 1rem;
    }
}

.cv-overlay-nav-side:hover:not(:disabled),
.cv-overlay-nav-side:focus {
    background: rgba(255, 255, 255, 0.25);
    transform: translateY(-50%) scale(1.1);
    outline: 2px solid rgba(255, 255, 255, 0.5);
    outline-offset: 2px;
}

/* Hide side nav when only one card */
.cv-overlay:has(.cv-overlay-card-container:has(.cv-overlay-card:only-child)) .cv-overlay-nav-side {
    display: none;
}
```

**Key Points**:
- Absolutely positioned on overlay edges
- Vertically centered (`top: 50%`, `translateY(-50%)`)
- High z-index (`z-index: 10`) above cards
- Hidden on mobile and single-card scenarios

##### Hide Bottom Nav on Desktop

```css
@media (min-width: 768px) {
    .cv-overlay-nav {
        display: none !important; /* CRITICAL: Hide bottom nav on desktop */
    }
}
```

**Key Points**:
- `!important` ensures it overrides any other rules
- Only one nav set visible per breakpoint

#### 2.2 Mobile Layout (<768px)

```css
@media (max-width: 767px) {
    .cv-overlay-card-container {
        width: 100%;
        padding: 1rem;
        overflow-y: auto;
        overflow-x: hidden; /* Prevent horizontal scroll */
    }
    
    .cv-overlay-card {
        max-width: 100%;
        width: 100%;
    }
    
    .cv-overlay-card-peek {
        display: none !important; /* No peek on mobile */
    }
    
    .cv-overlay-nav-side {
        display: none !important; /* Hide side nav on mobile */
    }
    
    .cv-overlay-nav {
        display: flex; /* Show bottom nav on mobile */
    }
}
```

**Key Points**:
- Full-width card on mobile
- No peek cards
- Side nav hidden
- Bottom nav visible

#### 2.3 Peek Card Content Styles

```css
.cv-overlay-card-peek-content {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(4px);
    border-radius: 12px;
    padding: 1rem;
    height: 100%;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.cv-overlay-card-peek-header {
    font-size: 0.875rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 0.5rem;
    line-height: 1.3;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.cv-overlay-card-peek-body {
    font-size: 0.75rem;
    color: #6b7280;
    line-height: 1.5;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}
```

### Phase 3: JavaScript Changes

**File**: `src/app/static/js/dev/card-overlay.js`

#### 3.1 Render Peek Cards Function

```javascript
/**
 * Render peek cards (previous/next) for desktop
 * Hides peeks on mobile, when only 1 card, or below 768px
 */
function renderPeekCards() {
    const prevPeek = document.getElementById('cv-overlay-card-prev');
    const nextPeek = document.getElementById('cv-overlay-card-next');
    
    // Hide peeks on mobile, when only 1 card, or viewport < 768px
    if (window.innerWidth < 768 || state.cards.length <= 1) {
        if (prevPeek) prevPeek.style.display = 'none';
        if (nextPeek) nextPeek.style.display = 'none';
        return;
    }
    
    // Desktop: render peek cards
    const prevIndex = state.currentCardIndex > 0 
        ? state.currentCardIndex - 1 
        : state.cards.length - 1; // Wrap-around
    const nextIndex = state.currentCardIndex < state.cards.length - 1 
        ? state.currentCardIndex + 1 
        : 0; // Wrap-around
    
    renderPeekCard('prev', prevIndex);
    renderPeekCard('next', nextIndex);
}

/**
 * Render a single peek card
 */
function renderPeekCard(direction, cardIndex) {
    const peekEl = document.getElementById(`cv-overlay-card-${direction}`);
    if (!peekEl || cardIndex < 0 || cardIndex >= state.cards.length) {
        return;
    }
    
    const card = state.cards[cardIndex];
    
    // Only update innerHTML if content changed (avoid unnecessary Lucide init)
    const newContent = `
        <div class="cv-overlay-card-peek-content">
            <div class="cv-overlay-card-peek-header">${escapeHtml(card.header)}</div>
            <div class="cv-overlay-card-peek-body">${escapeHtml(card.body.substring(0, 100))}...</div>
        </div>
    `;
    
    // Check if content actually changed
    if (peekEl.innerHTML !== newContent) {
        peekEl.innerHTML = newContent;
        
        // Initialize Lucide icons only if content changed
        if (typeof lucide !== 'undefined') {
            lucide.createIcons(peekEl);
        }
    }
    
    peekEl.style.display = 'block';
}
```

**Key Points**:
- Checks for single card (`state.cards.length <= 1`)
- Checks viewport width (`window.innerWidth < 768`)
- Only initializes Lucide if content changed (performance)
- Uses `lucide.createIcons(peekEl)` to scope to element

#### 3.2 Update renderCard Function

```javascript
function renderCard(cardIndex, direction) {
    // ... existing renderCard logic ...
    
    // Render peek cards after main card
    renderPeekCards();
    
    // Update navigation button visibility (handles single-card scenario)
    updateNavButtons();
    
    // ... rest of function ...
}
```

#### 3.3 Handle Window Resize

```javascript
// In init() function
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        if (state.isOpen) {
            renderPeekCards(); // Hide/show peeks based on new width
            updateNavButtons(); // Update nav visibility
        }
    }, 150); // Debounced
});
```

**Key Points**:
- Debounced resize handler (150ms)
- Hides peeks when viewport dips below 768px
- Updates nav button visibility

#### 3.4 Update Navigation Button Visibility

```javascript
function updateNavButtons() {
    const isMobile = window.innerWidth < 768;
    const isSingleCard = state.cards.length <= 1;
    
    // Side nav buttons (desktop)
    const sidePrev = document.getElementById('cv-overlay-nav-side-prev');
    const sideNext = document.getElementById('cv-overlay-nav-side-next');
    
    if (!isMobile && !isSingleCard && sidePrev && sideNext) {
        // Wrap-around: always enabled
        sidePrev.disabled = false;
        sideNext.disabled = false;
        sidePrev.style.display = 'flex';
        sideNext.style.display = 'flex';
    } else {
        // Hide on mobile or single card
        if (sidePrev) sidePrev.style.display = 'none';
        if (sideNext) sideNext.style.display = 'none';
    }
    
    // Bottom nav buttons (mobile)
    const bottomPrev = document.getElementById('cv-overlay-nav-prev');
    const bottomNext = document.getElementById('cv-overlay-nav-next');
    
    if (isMobile && !isSingleCard && bottomPrev && bottomNext) {
        // Wrap-around: always enabled
        bottomPrev.disabled = false;
        bottomNext.disabled = false;
        bottomPrev.style.display = 'flex';
        bottomNext.style.display = 'flex';
    } else {
        // Hide on desktop or single card
        if (bottomPrev) bottomPrev.style.display = 'none';
        if (bottomNext) bottomNext.style.display = 'none';
    }
}
```

**Key Points**:
- Checks for single card scenario
- Hides side nav on mobile or single card
- Hides bottom nav on desktop or single card
- Only one nav set visible per breakpoint

#### 3.5 Touch Device Considerations (Tablets >768px)

```javascript
// In init() function - ensure swipe doesn't conflict with side buttons
function setupSwipeGestures() {
    // ... existing swipe setup ...
    
    // On tablets (>768px), side buttons are visible
    // Ensure swipe handlers don't interfere
    overlayEl.addEventListener('touchstart', (e) => {
        // Check if touch started on side nav button
        const target = e.target.closest('.cv-overlay-nav-side');
        if (target) {
            // Don't prevent default - let button handle click
            return;
        }
        
        // ... existing swipe logic ...
    });
}
```

**Key Points**:
- Checks if touch started on side nav button
- Allows button click to proceed normally
- Prevents swipe handler from interfering

## Critical Challenges & Solutions

### Challenge 1: Peek Cards Without Breaking Layout

**Problem**: Showing neighbor cards can cause overflow or layout shifts.

**Solution**:
- Peek cards use `position: absolute` (don't affect flex layout)
- Container has `overflow: visible` (allows peek to extend)
- `z-index` layers cards correctly
- `pointer-events: none` prevents hit-target issues
- Narrow desktop breakpoint prevents horizontal scroll

### Challenge 2: Single-Card Scenario

**Problem**: Peeks and side nav should hide when only one card exists.

**Solution**:
- CSS `:has()` selector hides peeks
- JavaScript checks `state.cards.length <= 1`
- Both CSS and JS handle this (defensive)
- Nav buttons also hidden in single-card scenario

### Challenge 3: Narrow Desktop Overflow

**Problem**: Comments pane + gutter + card max-width might overflow on ~1024px screens.

**Solution**:
- Specific breakpoint: `@media (min-width: 768px) and (max-width: 1024px)`
- `overflow-x: hidden` on main container
- Calculated `max-width` accounts for comments + gutter + padding
- Card can shrink (`flex-shrink: 1`)

### Challenge 4: Touch Device Conflicts

**Problem**: Side buttons on tablets (>768px) might conflict with swipe gestures.

**Solution**:
- Swipe handler checks if touch started on side nav button
- Allows button click to proceed normally
- Bottom nav hidden on desktop (no conflict)
- Side nav hidden on mobile (no conflict)

### Challenge 5: Lucide Icon Re-initialization

**Problem**: Re-running `lucide.createIcons()` unnecessarily on every render.

**Solution**:
- Check if content actually changed before updating
- Use `lucide.createIcons(peekEl)` to scope to element
- Only initialize if innerHTML changed

## Testing Checklist

### Desktop (≥768px)
- [ ] Peek cards visible (5-10% of neighbors)
- [ ] Side nav buttons visible and functional
- [ ] Bottom nav hidden
- [ ] Card max-width capped at 1200px
- [ ] Card can shrink if needed
- [ ] Comments pane fixed at 450px
- [ ] Comments pane aligned at top with card
- [ ] 24px gutter between card and comments
- [ ] No horizontal scroll on narrow desktops (~1024px)
- [ ] Peek cards hidden when only 1 card
- [ ] Side nav hidden when only 1 card

### Mobile (<768px)
- [ ] No peek cards visible
- [ ] Side nav hidden
- [ ] Bottom nav visible and functional
- [ ] Full-width card
- [ ] Swipe gestures work correctly
- [ ] No conflicts between swipe and nav buttons

### Resize Behavior
- [ ] Layout switches correctly at 768px breakpoint
- [ ] Peeks hide when viewport dips below 768px
- [ ] Nav switches between side/bottom at breakpoint
- [ ] No layout shifts or overflow issues

### Navigation
- [ ] Wrap-around works (last → first, first → last)
- [ ] Peek cards update on navigation
- [ ] Peek cards dimmed opacity (0.4)
- [ ] Side nav hover/focus states work
- [ ] Side nav z-index above cards

### Comments Pane
- [ ] Independent scroll
- [ ] Aligned at top with card
- [ ] Fixed width maintained

### Very Large Screens (≥1600px)
- [ ] Carousel max-width capped at 1800px
- [ ] Carousel centered
- [ ] Side buttons not too far away

### Single Card Scenario
- [ ] Peeks hidden
- [ ] Side nav hidden
- [ ] Bottom nav hidden (or disabled)
- [ ] No odd slivers or visual artifacts

## Files to Modify

1. **`templates/dev/card_overlay.html`**
   - Add peek containers within card container
   - Add side nav buttons

2. **`src/app/static/css/dev/card-overlay.css`**
   - Desktop layout changes
   - Peek card styles
   - Side nav styles
   - Narrow desktop breakpoint
   - Very large screen breakpoint
   - Single-card CSS rules

3. **`src/app/static/js/dev/card-overlay.js`**
   - `renderPeekCards()` function
   - `renderPeekCard()` function
   - Update `renderCard()` to call peek rendering
   - Update `updateNavButtons()` for single-card scenario
   - Resize handler improvements
   - Touch device considerations

## Estimated Complexity

- **HTML Changes**: Low (add containers, add buttons)
- **CSS Changes**: Medium-High (layout restructuring, multiple breakpoints, peek positioning)
- **JavaScript Changes**: Medium (render peek cards, single-card handling, resize improvements)

**Total Estimate**: 6-8 hours

## Risk Mitigation Summary

| Risk | Mitigation |
|------|------------|
| Peek cards break layout | Absolute positioning, overflow: visible, z-index layering |
| Single-card slivers | CSS :has() + JS check, hide peeks and nav |
| Narrow desktop overflow | Specific breakpoint, calculated max-widths, overflow-x: hidden |
| Touch device conflicts | Check touch target, allow button clicks, hide conflicting nav |
| Lucide re-init overhead | Check content change, scope to element |
| Comments pane alignment | align-items: flex-start, align-self: flex-start |
| Max width too restrictive | Allow card to shrink, cap entire carousel on very large screens |


