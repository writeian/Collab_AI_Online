# iPhone Scroll Diagnostic Plan - October 28, 2025

## 🎯 The Problem
User cannot scroll up on iPhone - gets pushed back to bottom
Only by scrolling to bottom first can they scroll up normally

## 📋 THEORIES TO TEST (In Order of Likelihood)

================================================================================
## Theory #1: Padding Updates Still Nudge Scroll ⭐⭐⭐ HIGH
================================================================================

HYPOTHESIS:
applyBottomPadding fires constantly via ResizeObserver/visualViewport
Even though we guard nudgeScroll, some path might still set scrollTop

TEST ON IPHONE:
```javascript
// Add logging to every applyBottomPadding call
const originalApplyBottomPadding = applyBottomPadding;
window.applyBottomPadding = function(nudge) {
    const msgs = document.getElementById('chat-messages');
    console.log('🔧 applyBottomPadding called:', {
        nudge: nudge,
        scrollTop: msgs?.scrollTop,
        scrollHeight: msgs?.scrollHeight,
        clientHeight: msgs?.clientHeight,
        isNearBottom: (msgs.scrollHeight - msgs.scrollTop - msgs.clientHeight) < 20
    });
    return originalApplyBottomPadding?.call(this, nudge);
};

// Then scroll up and watch console
// Does it fire? Does scrollTop change?
```

LOOK FOR:
- Frequent calls (every 100ms or less)
- scrollTop jumping back up
- Correlation with your scroll attempts

IF CONFIRMED:
Disable applyBottomPadding on mobile entirely or
Remove ResizeObserver on mobile

================================================================================
## Theory #2: Polling Auto-Scroll on Mobile ⭐⭐ MEDIUM-HIGH  
================================================================================

HYPOTHESIS:
pollNewMessages thinks you're "near bottom" and auto-scrolls
sticky layout makes wasNearBottom === true too often

TEST ON IPHONE:
```javascript
// Temporarily disable polling
clearInterval(window.pollTimer);
console.log('✅ Polling disabled - try scrolling now');

// Or add logging to polling
const originalPoll = pollNewMessages;
window.pollNewMessages = async function() {
    const msgs = document.getElementById('chat-messages');
    const nearBottom = (msgs.scrollHeight - msgs.scrollTop - msgs.clientHeight) < 120;
    console.log('📊 Before poll:', {
        scrollTop: msgs.scrollTop,
        nearBottom: nearBottom
    });
    const result = await originalPoll.call(this);
    console.log('📊 After poll:', {
        scrollTop: msgs.scrollTop
    });
    return result;
};
```

LOOK FOR:
- Does disabling polling fix the scroll?
- Is nearBottom reporting true when you're scrolled up?

IF CONFIRMED:
Tighten threshold on mobile (120 → 200)
Or disable auto-scroll in polling for mobile

================================================================================
## Theory #3: Mobile "Near Bottom" Threshold Too Loose ⭐⭐ MEDIUM
================================================================================

HYPOTHESIS:
20px threshold too small for sticky layout
iOS reports near-bottom even when user is scrolled up

TEST ON IPHONE:
```javascript
// Monitor threshold while scrolling
const msgs = document.getElementById('chat-messages');
setInterval(() => {
    const distance = msgs.scrollHeight - msgs.scrollTop - msgs.clientHeight;
    console.log('Distance from bottom:', distance, 
                'NearBottom(20)?:', distance < 20,
                'NearBottom(100)?:', distance < 100);
}, 1000);

// Scroll up and watch the numbers
```

LOOK FOR:
- Distance reports negative or near-zero when you're scrolled up
- "NearBottom" flipping true unexpectedly

IF CONFIRMED:
Increase mobile threshold to 200 or higher
Or use different calculation for sticky layouts

================================================================================
## Theory #4: Pull-to-Refresh State Interference ⭐ LOW-MEDIUM
================================================================================

HYPOTHESIS:
isPulling flag affects scroll even without preventDefault
Indicator manipulation might cause layout shifts

TEST ON IPHONE:
```javascript
// Disable ChatTouchOptimizer entirely
// In console before page loads (or edit code):
// Comment out: new ChatTouchOptimizer();

// Or disable just on mobile:
const isMobile = /iP(ad|hone|od)/i.test(navigator.userAgent);
if (!isMobile) {
    new ChatTouchOptimizer();
}
console.log('ChatTouchOptimizer:', isMobile ? 'disabled' : 'enabled');
```

LOOK FOR:
- Does scroll work perfectly without ChatTouchOptimizer?

IF CONFIRMED:
Disable ChatTouchOptimizer on iOS
Or rewrite to not track state

================================================================================
## Theory #5: VisualViewport Handlers Over-Firing ⭐⭐ MEDIUM
================================================================================

HYPOTHESIS:
iOS toolbar show/hide triggers visualViewport events constantly
Each calls applyBottomPadding → potential scroll interference

TEST ON IPHONE:
```javascript
// Log visualViewport events
let vvCount = 0;
if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', () => {
        console.log('VV resize #' + (++vvCount));
    });
    window.visualViewport.addEventListener('scroll', () => {
        console.log('VV scroll event');
    });
}

// Scroll up and watch how many fire
```

LOOK FOR:
- Dozens of events while scrolling
- Correlation with snap-back behavior

IF CONFIRMED:
Debounce visualViewport handlers
Or disable on mobile

================================================================================
## Theory #6: scroll-behavior CSS Conflict ⭐ LOW
================================================================================

HYPOTHESIS:
Some CSS rule still has scroll-behavior: smooth on mobile
Smooth + sticky = unexpected repositioning

TEST ON IPHONE:
```javascript
// Check computed scroll-behavior
const msgs = document.getElementById('chat-messages');
console.log('scroll-behavior:', getComputedStyle(msgs).scrollBehavior);
// Expected: "auto"

// Force to auto and test
msgs.style.scrollBehavior = 'auto';
console.log('Forced to auto - try scrolling');
```

LOOK FOR:
- Returns "smooth" when should be "auto"

IF CONFIRMED:
Update components.css to ensure auto on mobile

================================================================================

## 🎯 RECOMMENDED DIAGNOSTIC ORDER

1. TEST THEORY #1 FIRST (Pull-to-Refresh Reload)
   - Disable ChatTouchOptimizer: comment out line 300
   - Test scroll on iPhone
   - If fixed → we know the culprit

2. IF NOT FIXED, TEST THEORY #2 (Polling)
   - Disable polling: clearInterval(pollTimer)
   - Test scroll
   - If fixed → tighten threshold

3. IF NOT FIXED, TEST THEORY #3 (Threshold)
   - Log distance while scrolling
   - Check if reporting near-bottom incorrectly

4. IF NOT FIXED, TEST THEORY #5 (VisualViewport)
   - Disable visualViewport handlers
   - Test scroll

5. THEORY #4 & #6 are less likely but easy to test

================================================================================

## 🔧 QUICK TEST CODE (Copy to iPhone Safari Console)

```javascript
// COMPREHENSIVE DIAGNOSTIC
console.log('=== SCROLL DIAGNOSTIC ===');

const msgs = document.getElementById('chat-messages');

// 1. Check what's active
console.log('ChatTouchOptimizer:', typeof ChatTouchOptimizer);
console.log('Polling:', typeof pollNewMessages);

// 2. Current state
console.log('scrollTop:', msgs.scrollTop);
console.log('scrollHeight:', msgs.scrollHeight);
console.log('clientHeight:', msgs.clientHeight);
console.log('Distance from bottom:', msgs.scrollHeight - msgs.scrollTop - msgs.clientHeight);

// 3. Monitor for auto-scrolling
let lastScrollTop = msgs.scrollTop;
setInterval(() => {
    if (msgs.scrollTop !== lastScrollTop) {
        console.log('📍 SCROLL CHANGED:', {
            from: lastScrollTop,
            to: msgs.scrollTop,
            diff: msgs.scrollTop - lastScrollTop
        });
    }
    lastScrollTop = msgs.scrollTop;
}, 100);

// 4. Disable ChatTouchOptimizer test
// Just reload page with this in console to disable it:
// (put in console before page loads)
```

================================================================================
