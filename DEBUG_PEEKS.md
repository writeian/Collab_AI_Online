# DevTools Checklist for Peek Cards

## 1. Check if Elements Exist in DOM
- Open DevTools → Elements tab
- Search for `cv-overlay-card-prev` and `cv-overlay-card-next`
- Verify they exist as children of `.cv-overlay-main` (not inside `.cv-overlay-shell`)

## 2. Check Computed Styles (Desktop ≥768px)

### For `#cv-overlay-card-prev`:
- **Display**: Should be `block` (not `none`)
- **Visibility**: Should be `visible` (not `hidden`)
- **Position**: Should be `absolute`
- **Left**: Should be `-80px` (not `-100px` or `0px`)
- **Width**: Should be `80px`
- **Z-index**: Should be `3`
- **Opacity**: Should be `0.35`

### For `#cv-overlay-card-next`:
- **Display**: Should be `block` (not `none`)
- **Visibility**: Should be `visible` (not `hidden`)
- **Position**: Should be `absolute`
- **Right**: Should be `-80px` (not `-100px` or `0px`)
- **Width**: Should be `80px`
- **Z-index**: Should be `3`
- **Opacity**: Should be `0.35`

## 3. Check Parent Container Styles

### `.cv-overlay-main`:
- **Overflow**: Should be `visible` (not `hidden`)
- **Padding**: Should be `32px 100px` (2rem = 32px)
- **Position**: Should be `relative`

### `.cv-overlay-content`:
- **Overflow**: Should be `visible` (not `hidden`)

## 4. Check for Conflicting Rules
- In Computed styles, look for "strikethrough" rules (overridden)
- Check if any `display: none !important` is overriding
- Check if inline styles are set (look for `style="display: none"` attribute)

## 5. Check JavaScript State
- Open Console
- Type: `CardOverlay.state`
- Check:
  - `currentCardIndex`: Should NOT be `0` (first card) or `length - 1` (last card) to see both peeks
  - `cards.length`: Should be > 1
- Type: `window.innerWidth` - Should be ≥ 768

## 6. Check Element Content
- Inspect `#cv-overlay-card-prev` and `#cv-overlay-card-next`
- Check if `innerHTML` has content (should have `.cv-overlay-card-peek-content` div)
- If empty, `renderPeekCard()` might not be running

## 7. Check Media Query
- In DevTools, toggle device toolbar (Cmd+Shift+M / Ctrl+Shift+M)
- Set width to ≥ 768px
- Verify desktop media query is active

## 8. Visual Inspection
- Use "Select element" tool (Cmd+Shift+C / Ctrl+Shift+C)
- Hover over left/right edges of screen
- Check if peeks are there but invisible (opacity 0, or behind something)

## 9. Console Commands to Test
```javascript
// Check if elements exist
document.getElementById('cv-overlay-card-prev')
document.getElementById('cv-overlay-card-next')

// Force show peeks
document.getElementById('cv-overlay-card-prev').style.display = 'block';
document.getElementById('cv-overlay-card-prev').style.visibility = 'visible';
document.getElementById('cv-overlay-card-prev').style.left = '-80px';
document.getElementById('cv-overlay-card-prev').style.zIndex = '999';

// Manually trigger render
CardOverlay.renderPeekCards();

// Check current card index
CardOverlay.state.currentCardIndex
CardOverlay.state.cards.length
```

## 10. Common Issues
- **Inline styles**: JavaScript `hidePeek()` sets `display: none` inline, overriding CSS
- **First/Last card**: Peeks hidden on first (no prev) or last (no next) card
- **Mobile viewport**: Width < 768px hides peeks
- **Empty content**: `innerHTML` is empty, so nothing to show
- **Z-index stacking**: Peeks behind shell or other elements
- **Overflow clipping**: Parent has `overflow: hidden`


