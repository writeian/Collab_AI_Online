# Peek Cards Visibility Issue - Troubleshooting Guide

## Problem Summary

Peek cards (preview of previous/next cards) were not visible in the card overlay carousel despite correct HTML structure, CSS rules, and JavaScript rendering logic. The cards were being rendered but appeared off-canvas or were completely invisible.

## Initial Symptoms

- Peek cards were being rendered in the DOM (verified via `console.log` and DOM inspection)
- JavaScript `renderPeekCards()` function was executing correctly
- CSS rules were present and appeared correct
- Cards were positioned but not visible on screen
- No console errors related to rendering

## Root Cause

**The core issue was incorrect CSS positioning context.** Peek cards were using `position: absolute` relative to a parent container (`.cv-overlay-main`) that had padding (`padding: 2rem 100px`). This caused the peeks to be positioned relative to the content area, not the viewport edges, making them appear off-canvas or invisible.

## Attempted Fixes (Chronological)

### Attempt 1: HTML Structure Changes
**What we tried:**
- Moved peek elements to be siblings of `.cv-overlay-shell` inside `.cv-overlay-main`
- Ensured peeks were outside the shell wrapper

**Result:** No change - peeks still invisible

**Why it didn't work:** The positioning context issue persisted regardless of HTML structure.

---

### Attempt 2: CSS Positioning Adjustments (Absolute)
**What we tried:**
```css
.cv-overlay-card-peek {
    position: absolute;
    left: 0;
    right: 0;
    width: 80px;
    z-index: 3;
}
```

**Result:** Peeks positioned relative to parent container, not viewport

**Why it didn't work:** `position: absolute` positions relative to the nearest positioned ancestor (`.cv-overlay-main`), which had padding, causing misalignment.

---

### Attempt 3: Transform-Based Positioning
**What we tried:**
```css
.cv-overlay-card-peek-prev {
    left: -100px;
    transform: translateX(-100px);
}
.cv-overlay-card-peek-next {
    right: -100px;
    transform: translateX(100px);
}
```

**Result:** Peeks still off-canvas or invisible

**Why it didn't work:** Still using `absolute` positioning relative to padded parent, transforms didn't solve the fundamental positioning context issue.

---

### Attempt 4: JavaScript Inline Style Management
**What we tried:**
- Changed `hidePeek()` to use `removeProperty('display')` instead of `style.display = ''`
- Added `cv-peek-hidden` class for toggling visibility
- Ensured inline styles were properly cleared

**Result:** Improved state management but peeks still not visible

**Why it didn't work:** The positioning issue was CSS-level, not JavaScript-level.

---

### Attempt 5: Z-Index and Overflow Adjustments
**What we tried:**
```css
.cv-overlay-main {
    overflow: visible !important;
    position: relative;
    padding: 2rem 100px;
}
.cv-overlay-content {
    overflow: visible;
}
.cv-overlay-card-peek {
    z-index: 10 !important;
}
```

**Result:** No change - peeks still invisible

**Why it didn't work:** Overflow and z-index don't fix positioning context issues.

---

### Attempt 6: Debug Styling (Temporary)
**What we tried:**
```css
.cv-overlay-card-peek {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    opacity: 0.7 !important;
}
```

**Result:** Made peeks visible during debugging, confirming they existed but were mispositioned

**Why it didn't work:** This was diagnostic, not a fix.

---

## The Fix: Switch to `position: fixed`

### Final Solution

**Changed from:**
```css
.cv-overlay-card-peek {
    position: absolute;
    left: 0;
    right: 0;
}
```

**Changed to:**
```css
.cv-overlay-card-peek {
    position: fixed;
    left: 0;
    right: 0;
}
```

### Why This Works

1. **Viewport-Relative Positioning**: `position: fixed` positions elements relative to the browser viewport, not the parent container
2. **Independent of Parent Padding**: Parent container padding (`padding: 2rem 100px`) no longer affects peek positioning
3. **Screen Edge Alignment**: `left: 0` and `right: 0` now correctly align with screen edges
4. **Predictable Behavior**: Fixed positioning is more predictable and easier to debug

### Complete CSS Solution

```css
.cv-overlay-card-peek {
    display: none; /* Hidden by default, shown on desktop */
    position: fixed; /* KEY: Fixed to viewport, not parent */
    width: 80px;
    max-width: 80px;
    height: 80%;
    opacity: 0.7;
    pointer-events: none;
    z-index: 3;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 0, 0, 0.1);
}

@media (min-width: 768px) {
    .cv-overlay-card-peek {
        display: block !important;
        visibility: visible !important;
    }
    
    .cv-overlay-main .cv-overlay-card-peek-prev {
        left: 0 !important; /* Screen edge */
        transform: none;
        z-index: 10 !important;
    }
    
    .cv-overlay-main .cv-overlay-card-peek-next {
        right: 0 !important; /* Screen edge */
        transform: none;
        z-index: 10 !important;
    }
}

@media (max-width: 767px) {
    .cv-overlay-card-peek {
        display: none !important;
    }
}
```

## Key Lessons Learned

### 1. Positioning Context Matters
- `position: absolute` positions relative to the nearest positioned ancestor
- Parent padding/margins affect absolute positioning calculations
- `position: fixed` positions relative to the viewport, independent of parent

### 2. Debugging Strategy
- Use temporary high-contrast styling (`background`, `border`, `opacity`) to verify elements exist
- Check computed styles in browser DevTools, not just source CSS
- Verify positioning context by inspecting parent containers

### 3. CSS Specificity and Inheritance
- `!important` flags helped during debugging but weren't the solution
- Media queries need to be explicit about display/visibility
- Z-index only matters if elements are visible and positioned

### 4. JavaScript vs CSS Issues
- If JavaScript is rendering correctly (verified via DOM inspection), the issue is likely CSS
- Inline style management (`removeProperty` vs `= ''`) matters for state management but won't fix positioning

### 5. Testing Approach
- Test with different viewport sizes to catch responsive issues
- Use browser DevTools to inspect computed styles and positioning
- Temporarily increase opacity/visibility to verify element existence

## Prevention Checklist

When implementing similar peek/preview features:

- [ ] **Choose positioning carefully**: Use `fixed` for viewport-relative elements, `absolute` for container-relative
- [ ] **Account for parent padding**: If using `absolute`, calculate positions including parent padding
- [ ] **Test with debug styling**: Add temporary high-contrast styles during development
- [ ] **Verify in DevTools**: Check computed styles, not just source CSS
- [ ] **Test responsive breakpoints**: Ensure visibility rules work at all screen sizes
- [ ] **Document positioning strategy**: Note why `fixed` vs `absolute` was chosen

## Related Files

- `src/app/static/css/dev/card-overlay.css` - CSS rules for peek cards
- `src/app/static/js/dev/card-overlay.js` - JavaScript rendering logic
- `templates/dev/card_overlay.html` - HTML structure

## Time Investment

- **Total debugging time**: ~4-6 hours
- **Attempts made**: 6+ different approaches
- **Root cause identified**: After 5th attempt (positioning context)
- **Final fix**: Simple CSS change (`absolute` → `fixed`)

## Conclusion

The issue was a fundamental misunderstanding of CSS positioning contexts. Switching from `position: absolute` to `position: fixed` resolved the problem immediately. This document should prevent similar issues in the future by documenting the positioning context considerations and debugging strategies.

---

**Last Updated**: December 2025  
**Status**: Resolved  
**Impact**: High (feature was completely broken)  
**Complexity**: Medium (simple fix, complex debugging process)


