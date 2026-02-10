/**
 * Card Overlay Carousel Module
 * 
 * Handles grid layout, overlay carousel, navigation, and comments for Card View preview.
 * Isolated to dev/preview paths only - does not affect production chat UI.
 */

console.log('[CardOverlay] Script file loading...');

const CardOverlay = (function() {
    'use strict';
    
    console.log('[CardOverlay] IIFE starting...');
    
    // Configuration: Toggle between simulation and real API
    // Set to false to use simulation (in-memory only), true for real API calls
    // 
    // WARNING: When USE_REAL_API=true and chat_id/message_id are provided:
    // - Comments will be saved to the database tied to the real chat/message
    // - Card content from preview may be unrelated to the actual message
    // - This can pollute production data with synthetic content
    // - Only use with test/development chats, never production data
    const USE_REAL_API = true; // Toggle this flag to switch between simulation and real API
    
    // Get chat_id, room_id, and message_id from page data attributes
    const containerEl = document.querySelector('.cv-container');
    const chatId = containerEl?.dataset.chatId ? parseInt(containerEl.dataset.chatId) : null;
    const roomId = containerEl?.dataset.roomId ? parseInt(containerEl.dataset.roomId) : null;
    const initialMessageId = containerEl?.dataset.messageId ? parseInt(containerEl.dataset.messageId) : null;
    
    // Centralized state - URL hash is source of truth
    const state = {
        isOpen: false,
        currentCardIndex: 0,
        currentCardKey: null,
        totalCards: 0,
        cards: [], // Array of card data from segmentation (includes message_id, segment_index, card_key)
        commentsLoaded: new Set(), // Set of card_keys with loaded comments
        comments: {}, // Map of card_key -> array of comments
        gridScrollPosition: 0,
        commentsSheetOpen: false, // Mobile only
        preloadedCards: new Set(),
        guidingQuestion: null,
        relationships: [],
        navigationDirection: null, // 'prev' or 'next' for animation direction
        messageId: null, // Source message ID (for API calls)
        splitRatio: 0.65, // Default: 65% card, 35% comments
        isDragging: false, // Splitter drag state
    };
    
    // DOM elements (cached after init)
    let overlayEl = null;
    let cardContainerEl = null;
    let commentsPaneEl = null;
    let commentsSheetEl = null;
    let indicatorEl = null;
    let prevBtnEl = null;
    let nextBtnEl = null;
    let ariaLiveEl = null; // ARIA live region for screen reader announcements
    let focusTrapElements = []; // Elements that should receive focus within overlay
    
    // Splitter DOM elements
    let splitterEl = null;
    let cardColumnEl = null;
    let shellEl = null;
    
    // Animation timeout tracker (for cleanup)
    let animationTimeoutId = null;
    
    // Navigation debounce tracker
    let navigationDebounceTimeout = null;
    const NAVIGATION_DEBOUNCE_MS = 150; // Prevent rapid-fire navigation
    
    // Swipe gesture tracking
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;
    let isSwipeInProgress = false;
    const SWIPE_THRESHOLD = 50; // Minimum pixels for swipe detection
    const SWIPE_VELOCITY_THRESHOLD = 0.3; // Minimum velocity (pixels/ms)
    
    // Splitter constants
    const SPLITTER_STORAGE_KEY = 'card_overlay_split_ratio';
    const MIN_CARD_WIDTH = 600; // Minimum card column width (px)
    const MIN_COMMENTS_WIDTH = 320; // Minimum comments pane width (px)
    const DEFAULT_SPLIT_RATIO = 0.65; // Default: 65% card, 35% comments
    const SPLITTER_WIDTH = 12; // Fixed splitter width (px)
    const KEYBOARD_NUDGE = 0.02; // 2% ratio change per arrow key press
    
    // Splitter drag state
    let splitterDragStartX = 0;
    let splitterInitialCardWidth = 0;
    let splitterShellWidth = 0;
    let splitterRafId = null; // requestAnimationFrame ID for throttling
    
    /**
     * Initialize overlay module
     */
    function init() {
        overlayEl = document.getElementById('card-overlay');
        if (!overlayEl) {
            console.warn('Card overlay element not found');
            return;
        }
        
        cardContainerEl = document.getElementById('cv-overlay-card');
        commentsPaneEl = document.getElementById('cv-overlay-comments-pane');
        commentsSheetEl = document.getElementById('cv-overlay-comments-sheet');
        indicatorEl = document.getElementById('cv-overlay-indicator-text');
        prevBtnEl = document.getElementById('cv-overlay-nav-prev');
        nextBtnEl = document.getElementById('cv-overlay-nav-next');
        
        // Create ARIA live region for screen reader announcements
        ariaLiveEl = document.createElement('div');
        ariaLiveEl.setAttribute('role', 'status');
        ariaLiveEl.setAttribute('aria-live', 'polite');
        ariaLiveEl.setAttribute('aria-atomic', 'true');
        ariaLiveEl.className = 'sr-only'; // Screen reader only (visually hidden)
        ariaLiveEl.style.cssText = 'position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border-width: 0;';
        if (overlayEl) {
            overlayEl.appendChild(ariaLiveEl);
        }
        
        // Build focus trap elements list
        updateFocusTrapElements();
        
        // Setup keyboard listeners
        document.addEventListener('keydown', handleKeyboard);
        
        // Setup hash change listeners (browser back/forward)
        window.addEventListener('hashchange', syncStateFromHash);
        window.addEventListener('popstate', syncStateFromHash);
        
        // Setup comment composer enhancements (auto-resize, keyboard shortcuts)
        setupCommentComposers();
        
        // Setup swipe gesture handlers
        setupSwipeGestures();
        
        // Initialize splitter
        initSplitter();
        
        // Setup resize handler for peek cards, nav visibility, and splitter
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                if (state.isOpen) {
                    renderPeekCards(); // Hide/show peeks based on new width
                    updateNavButtons(); // Update nav visibility
                    handleSplitterWindowResize(); // Reclamp split ratio
                }
            }, 150); // Debounced
        });
        
        // Parse hash on initial load
        syncStateFromHash();
    }
    
    /**
     * Setup swipe gesture handlers for mobile
     * 
     * NOTE: Must be called after DOM elements are available (in init() after DOM cache).
     * Uses non-passive listeners ({ passive: false }) to allow preventDefault() for swipe detection.
     */
    function setupSwipeGestures() {
        if (!overlayEl) {
            console.warn('setupSwipeGestures: overlay element not found');
            return;
        }
        
        // Card carousel swipe (left/right) - on card container
        // NOTE: We use touch-action: none on container and manually handle vertical scrolling
        // This allows horizontal swipe detection while preserving vertical scroll
        const cardContainer = document.querySelector('.cv-overlay-card-container');
        if (cardContainer) {
            cardContainer.addEventListener('touchstart', handleCardSwipeStart, { passive: false });
            cardContainer.addEventListener('touchmove', handleCardSwipeMove, { passive: false });
            cardContainer.addEventListener('touchend', handleCardSwipeEnd, { passive: false });
        } else {
            console.warn('setupSwipeGestures: card container not found');
        }
        
        // Comments sheet swipe (down to dismiss) - on sheet header/drag handle AND sheet container (upper 20%)
        // NOTE: Swipe down on sheet content upper 20% dismisses to improve UX
        // Swipe down on lower 80% allows scrolling comments without dismissing
        if (commentsSheetEl) {
            const sheetHeader = commentsSheetEl.querySelector('.cv-overlay-comments-sheet-header');
            const dragHandle = commentsSheetEl.querySelector('.cv-overlay-comments-sheet-drag-handle');
            
            // Bind to header
            if (sheetHeader) {
                sheetHeader.addEventListener('touchstart', handleSheetSwipeStart, { passive: false });
                sheetHeader.addEventListener('touchmove', handleSheetSwipeMove, { passive: false });
                sheetHeader.addEventListener('touchend', handleSheetSwipeEnd, { passive: false });
            }
            
            // Bind to drag handle
            if (dragHandle) {
                dragHandle.addEventListener('touchstart', handleSheetSwipeStart, { passive: false });
                dragHandle.addEventListener('touchmove', handleSheetSwipeMove, { passive: false });
                dragHandle.addEventListener('touchend', handleSheetSwipeEnd, { passive: false });
            }
            
            // Also bind to sheet container (but only for vertical swipes starting in upper 20%)
            // This allows dismissing by swiping down on the sheet itself, not just header
            // Upper 20% rule prevents conflicts with scrolling comments in the lower area
            let sheetSwipeStartY = 0;
            
            commentsSheetEl.addEventListener('touchstart', function(e) {
                if (!state.commentsSheetOpen) return;
                
                // Only handle if touch starts in upper 20% of sheet (to avoid conflicts with scrolling)
                const touchY = e.touches[0].clientY;
                const sheetRect = commentsSheetEl.getBoundingClientRect();
                const sheetTop = sheetRect.top;
                const sheetHeight = sheetRect.height;
                const touchRelativeY = touchY - sheetTop;
                
                if (touchRelativeY < sheetHeight * 0.2) {
                    // Touch in upper 20% - allow dismiss gesture
                    sheetSwipeStartY = touchY;
                    handleSheetSwipeStart(e);
                }
            }, { passive: false });
            
            commentsSheetEl.addEventListener('touchmove', function(e) {
                if (!state.commentsSheetOpen || sheetSwipeStartY === 0) return;
                
                // Only handle if started in upper 20%
                handleSheetSwipeMove(e);
            }, { passive: false });
            
            commentsSheetEl.addEventListener('touchend', function(e) {
                if (!state.commentsSheetOpen || sheetSwipeStartY === 0) {
                    sheetSwipeStartY = 0;
                    return;
                }
                
                handleSheetSwipeEnd(e);
                sheetSwipeStartY = 0;
            }, { passive: false });
        } else {
            console.warn('setupSwipeGestures: comments sheet not found');
        }
    }
    
    /**
     * Handle card carousel swipe start
     * 
     * Multi-touch guard: Only handles single-touch gestures (bails if touches.length > 1)
     */
    function handleCardSwipeStart(e) {
        // Multi-touch guard: bail if more than one touch
        if (!state.isOpen || e.touches.length !== 1) {
            touchStartX = 0;
            touchStartY = 0;
            return;
        }
        
        // Check if touch started on side nav button (tablets >768px)
        // Allow button click to proceed normally, don't trigger swipe
        const target = e.target.closest('.cv-overlay-nav-side');
        if (target) {
            // Don't prevent default - let button handle click
            touchStartX = 0;
            touchStartY = 0;
            return;
        }
        
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        isSwipeInProgress = false;
    }
    
    /**
     * Handle card carousel swipe move
     * 
     * Multi-touch guard: Only handles single-touch gestures
     * preventDefault() only called for horizontal swipes to block native horizontal scroll
     * 
     * NOTE: With touch-action: none, we must manually allow vertical scrolling by NOT
     * calling preventDefault() for vertical movements. The browser will handle vertical
     * scrolling naturally when preventDefault() is not called.
     */
    function handleCardSwipeMove(e) {
        // Multi-touch guard: bail if more than one touch
        if (!state.isOpen || e.touches.length !== 1 || !touchStartX || !touchStartY) {
            return;
        }
        
        const deltaX = Math.abs(e.touches[0].clientX - touchStartX);
        const deltaY = Math.abs(e.touches[0].clientY - touchStartY);
        
        // Only prevent default if horizontal swipe is dominant (blocks native horizontal scroll)
        // Vertical scrolling is allowed by NOT calling preventDefault() - browser handles it
        if (deltaX > deltaY && deltaX > 10) {
            e.preventDefault();
            isSwipeInProgress = true;
        }
        // If vertical scroll is dominant, don't preventDefault() - allows native vertical scrolling
    }
    
    /**
     * Handle card carousel swipe end
     * 
     * NOTE: Navigation debounce (150ms) may drop very fast consecutive swipes.
     * This is intentional to prevent animation conflicts.
     */
    function handleCardSwipeEnd(e) {
        if (!state.isOpen || !touchStartX || !touchStartY) {
            // Reset on early return
            touchStartX = 0;
            touchStartY = 0;
            return;
        }
        
        // Multi-touch guard: bail if more than one touch
        if (e.changedTouches.length !== 1) {
            touchStartX = 0;
            touchStartY = 0;
            return;
        }
        
        touchEndX = e.changedTouches[0].clientX;
        touchEndY = e.changedTouches[0].clientY;
        
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;
        const absDeltaX = Math.abs(deltaX);
        const absDeltaY = Math.abs(deltaY);
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        const timeDelta = e.timeStamp - (e.timeStamp - 100); // Approximate duration
        const velocity = distance / Math.max(timeDelta, 1);
        
        // Only handle horizontal swipes (left/right)
        if (absDeltaX > absDeltaY && absDeltaX > SWIPE_THRESHOLD) {
            // Check velocity threshold or allow longer swipes
            if (velocity > SWIPE_VELOCITY_THRESHOLD || absDeltaX > SWIPE_THRESHOLD * 2) {
                if (deltaX > 0) {
                    // Swipe right → previous card
                    previousCard();
                } else {
                    // Swipe left → next card
                    nextCard();
                }
            }
        }
        
        // Reset
        touchStartX = 0;
        touchStartY = 0;
        touchEndX = 0;
        touchEndY = 0;
        isSwipeInProgress = false;
    }
    
    /**
     * Handle comments sheet swipe start
     * 
     * NOTE: Swipe dismiss is ONLY on sheet header/drag handle, NOT on sheet content.
     * This allows users to scroll comments without accidentally dismissing the sheet.
     * 
     * Multi-touch guard: Only handles single-touch gestures
     */
    function handleSheetSwipeStart(e) {
        // Multi-touch guard: bail if more than one touch
        if (!state.commentsSheetOpen || e.touches.length !== 1) {
            touchStartX = 0;
            touchStartY = 0;
            return;
        }
        
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        isSwipeInProgress = false;
    }
    
    /**
     * Handle comments sheet swipe move
     * 
     * preventDefault() only called for vertical swipes to block native vertical scroll on header
     */
    function handleSheetSwipeMove(e) {
        // Multi-touch guard: bail if more than one touch
        if (!state.commentsSheetOpen || e.touches.length !== 1 || !touchStartY) {
            return;
        }
        
        const deltaY = Math.abs(e.touches[0].clientY - touchStartY);
        const deltaX = Math.abs(e.touches[0].clientX - touchStartX);
        
        // Only prevent default if vertical swipe is dominant (blocks native vertical scroll on header)
        // Horizontal swipes are allowed (for potential future features)
        if (deltaY > deltaX && deltaY > 10) {
            e.preventDefault();
            isSwipeInProgress = true;
        }
    }
    
    /**
     * Handle comments sheet swipe end
     * 
     * Swipe down on header/drag handle dismisses the sheet.
     * Swipe down on sheet content does NOT dismiss (allows scrolling comments).
     */
    function handleSheetSwipeEnd(e) {
        if (!state.commentsSheetOpen || !touchStartY) {
            touchStartX = 0;
            touchStartY = 0;
            return;
        }
        
        // Multi-touch guard: bail if more than one touch
        if (e.changedTouches.length !== 1) {
            touchStartX = 0;
            touchStartY = 0;
            return;
        }
        
        touchEndY = e.changedTouches[0].clientY;
        const deltaY = touchEndY - touchStartY;
        const absDeltaY = Math.abs(deltaY);
        
        // Swipe down to dismiss sheet (only works on header/drag handle)
        if (deltaY > 0 && absDeltaY > SWIPE_THRESHOLD) {
            toggleCommentsSheet();
        }
        
        // Reset
        touchStartX = 0;
        touchStartY = 0;
        touchEndY = 0;
        isSwipeInProgress = false;
    }
    
    /**
     * Setup comment composer enhancements (auto-resize, keyboard shortcuts)
     */
    function setupCommentComposers() {
        // Setup for both desktop and mobile inputs
        const inputIds = ['cv-overlay-comment-input', 'cv-overlay-comment-input-mobile'];
        
        inputIds.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (!input) return;
            
            // Auto-resize textarea
            input.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 200) + 'px'; // Max 200px height
            });
            
            // Keyboard shortcuts: Enter to submit, Shift+Enter for new line
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const isMobile = inputId.includes('mobile');
                    addComment(isMobile);
                }
            });
            
            // Prevent form submission on Enter
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                }
            });
        });
    }
    
    /**
     * Extract first phrase/sentence from body for bold title
     * Returns object with {title, snippet} where title is first phrase (bolded)
     * and snippet is remaining text (2-3 lines, avoiding duplication)
     */
    function extractTitleAndSnippet(body, header = null, maxChars = 180) {
        if (!body) return { title: '', snippet: '' };
        
        // Strip markdown code blocks
        let text = body.replace(/```[\s\S]*?```/g, '[code]');
        
        // Strip markdown formatting (but preserve structure)
        text = text.replace(/#{1,6}\s+/g, ''); // Headings
        text = text.replace(/\*\*(.*?)\*\*/g, '$1'); // Bold
        text = text.replace(/\*(.*?)\*/g, '$1'); // Italic
        text = text.replace(/`(.*?)`/g, '$1'); // Inline code
        
        // Split into lines
        const lines = text.split('\n').filter(line => line.trim());
        if (lines.length === 0) return { title: '', snippet: '' };
        
        // Use header if available (relaxed check - accept any header length)
        // Prefer API/AI-supplied header over body-derived title
        if (header && header.trim().length > 0) {
            const headerWords = header.trim().split(/\s+/).length;
            // Accept headers from 2 words up (very permissive)
            if (headerWords >= 2) {
                // Use header as title, skip first line if it matches header
                const firstLine = lines[0].trim();
                const headerLower = header.toLowerCase();
                const firstLineLower = firstLine.toLowerCase();
                
                // If first line is similar to header, skip it
                let snippetStart = 0;
                if (firstLineLower.includes(headerLower) || headerLower.includes(firstLineLower.substring(0, 30))) {
                    snippetStart = 1;
                }
                
                // Build snippet from remaining lines
                let snippet = '';
                for (let i = snippetStart; i < Math.min(snippetStart + 3, lines.length) && snippet.length < maxChars; i++) {
                    const line = lines[i].trim();
                    if (snippet) snippet += ' ';
                    snippet += line;
                    if (snippet.length >= maxChars) break;
                }
                
                if (snippet.length > maxChars) {
                    snippet = snippet.substring(0, maxChars - 3).trim() + '...';
                }
                
                return { title: header, snippet: snippet || lines[snippetStart]?.trim() || '' };
            }
        }
        
        // Fallback: Bold first phrase/sentence as title
        const firstLine = lines[0].trim();
        // Extract first phrase (up to first period, comma, or ~40 chars)
        let titleEnd = firstLine.length;
        const periodIdx = firstLine.indexOf('.');
        const commaIdx = firstLine.indexOf(',');
        if (periodIdx > 0 && periodIdx < 40) titleEnd = Math.min(titleEnd, periodIdx + 1);
        if (commaIdx > 0 && commaIdx < 40) titleEnd = Math.min(titleEnd, commaIdx + 1);
        if (titleEnd > 50) titleEnd = 50; // Cap at 50 chars
        
        const title = firstLine.substring(0, titleEnd).trim();
        
        // Build snippet starting from after title (avoid duplication)
        let snippet = '';
        let startIdx = 0;
        if (firstLine.length > titleEnd) {
            // Use rest of first line if there's more
            snippet = firstLine.substring(titleEnd).trim();
            startIdx = 1;
        } else {
            startIdx = 1; // Skip first line entirely
        }
        
        // Add 2-3 more lines
        for (let i = startIdx; i < Math.min(startIdx + 3, lines.length) && snippet.length < maxChars; i++) {
            const line = lines[i].trim();
            if (snippet) snippet += ' ';
            snippet += line;
            if (snippet.length >= maxChars) break;
        }
        
        if (snippet.length > maxChars) {
            snippet = snippet.substring(0, maxChars - 3).trim() + '...';
        }
        
        return { title, snippet: snippet || title };
    }
    
    /**
     * Render grid of cards
     */
    function renderGrid(cards, containerId = 'cards-container') {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn(`Grid container ${containerId} not found`);
            return;
        }
        
        if (!cards || cards.length === 0) {
            container.innerHTML = `
                <div class="cv-empty">
                    <i data-lucide="inbox"></i>
                    <p>No cards to display</p>
                </div>
            `;
            // Clear card count badge
            const cardCountBadge = document.getElementById('card-count');
            if (cardCountBadge) {
                cardCountBadge.textContent = '';
            }
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
            return;
        }
        
        // Store cards in state
        state.cards = cards;
        state.totalCards = cards.length;
        
        // Update card count badge
        const cardCountBadge = document.getElementById('card-count');
        if (cardCountBadge) {
            cardCountBadge.textContent = cards.length;
        }
        
        let html = '<div class="cv-grid">';
        
        cards.forEach((card, index) => {
            const cardKey = card.card_key || '';
            const { title, snippet } = extractTitleAndSnippet(card.body, card.header);
            
            // Create unique handler function name to avoid closure issues
            const cardHandler = `handleGridCard${index}`;
            
            // Store handler globally for inline event handlers
            window[cardHandler] = function(e) {
                if (e.type === 'keydown') {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        CardOverlay.openCard(index);
                    }
                } else {
                    CardOverlay.openCard(index);
                }
            };
            
            // Build metadata for large screens (segment index, confidence, AI tag)
            const metaParts = [];
            if (card.segment_index !== undefined) {
                metaParts.push(`Segment ${card.segment_index + 1} of ${cards.length}`);
            }
            if (card.confidence !== undefined && card.confidence < 1.0) {
                metaParts.push(`${Math.round(card.confidence * 100)}% confidence`);
            }
            if (card.segment_type === 'code') {
                metaParts.push('Code');
            }
            const metadata = metaParts.length > 0 ? metaParts.join(' • ') : '';
            
            // Build snippet HTML with bold first phrase
            let snippetHtml = '';
            if (title && snippet) {
                // If snippet starts with title, bold it and show rest
                if (snippet.toLowerCase().startsWith(title.toLowerCase())) {
                    const rest = snippet.substring(title.length).trim();
                    snippetHtml = `<span class="cv-grid-card-snippet-bold-start">${escapeHtml(title)}</span>${rest ? ' ' + escapeHtml(rest) : ''}`;
                } else {
                    // Title and snippet are different - show both
                    snippetHtml = `<span class="cv-grid-card-snippet-bold-start">${escapeHtml(title)}</span> ${escapeHtml(snippet)}`;
                }
            } else if (title) {
                snippetHtml = `<span class="cv-grid-card-snippet-bold-start">${escapeHtml(title)}</span>`;
            } else if (snippet) {
                snippetHtml = escapeHtml(snippet);
            }
            
            html += `
                <div 
                    class="cv-grid-card" 
                    data-card-index="${index}"
                    data-card-key="${cardKey}"
                    onclick="window.${cardHandler}(event)"
                    onkeydown="window.${cardHandler}(event)"
                    role="button"
                    tabindex="0"
                    aria-label="Card ${index + 1}: ${escapeHtml(title || card.header || 'Card')}"
                >
                    <div class="cv-grid-card-number">${index + 1}</div>
                    <div class="cv-grid-card-body">
                        <div class="cv-grid-card-snippet">${snippetHtml}</div>
                        ${metadata ? `<div class="cv-grid-card-meta">${escapeHtml(metadata)}</div>` : ''}
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Get CSRF token from cookie
     */
    function getCsrfToken() {
        const name = 'csrf_token=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const cookieArray = decodedCookie.split(';');
        
        for (let cookie of cookieArray) {
            cookie = cookie.trim();
            if (cookie.indexOf(name) === 0) {
                return cookie.substring(name.length);
            }
        }
        return null;
    }
    
    /**
     * Get API base URL for comments endpoints
     */
    function getCommentsApiUrl(cardKey) {
        if (!chatId || !cardKey) {
            return null;
        }
        return `/chat/${chatId}/cards/${cardKey}/comments`;
    }
    
    /**
     * Check if real API should be used
     * 
     * Requires: chatId, roomId, AND messageId (all must be present)
     * 
     * WARNING: Using real API with preview/synthetic content will create
     * real database records tied to the specified chat/message, even though
     * the card content may be unrelated. This can pollute production data.
     * 
     * Only use real API when:
     * 1. All required context is present (chatId, roomId, messageId)
     * 2. You're in a test/development chat with known message_id matching the content
     * 3. Never use with production data
     */
    function shouldUseRealApi() {
        // Require explicit messageId - don't auto-detect from latest message
        // This prevents writing comments to unrelated messages
        return USE_REAL_API && chatId && roomId && state.messageId && state.messageId > 0;
    }
    
    /**
     * Sync state from URL hash (source of truth)
     */
    function syncStateFromHash() {
        const hash = window.location.hash;
        // Regex matches #card= followed by 8+ hex chars (handles SHA1 40-char keys)
        // NOTE: Currently optimized for SHA1 format. If card_key format changes,
        // update regex accordingly. Current format: 40 hex chars (SHA1)
        const match = hash.match(/#card=([a-f0-9]{8,})/i);
        
        if (match && state.cards.length > 0) {
            const cardKey = match[1];
            const cardIndex = state.cards.findIndex(card => card.card_key === cardKey);
            
            if (cardIndex !== -1) {
                if (!state.isOpen) {
                    // Opening overlay from hash - no direction animation
                    openCard(cardIndex);
                } else if (state.currentCardIndex !== cardIndex) {
                    // Navigating to different card - determine direction
                    const direction = cardIndex > state.currentCardIndex ? 'next' : 'prev';
                    navigateToCard(cardIndex, direction);
                }
            } else {
                // Card key not found - might be from different segmentation
                console.warn(`Card key ${cardKey} not found in current cards`);
                // Fallback: if overlay is open, keep it open but don't navigate
                // If overlay is closed, do nothing (invalid hash)
            }
        } else if (!match && state.isOpen) {
            // Hash cleared but overlay still open - close it
            close();
        }
    }
    
    /**
     * Update URL hash (source of truth)
     */
    function updateURLHash(cardKey) {
        if (cardKey) {
            window.history.pushState(null, '', `#card=${cardKey}`);
        } else {
            window.history.pushState(null, '', window.location.pathname);
        }
    }
    
    /**
     * Open overlay at specific card index
     */
    function openCard(cardIndex) {
        if (cardIndex < 0 || cardIndex >= state.cards.length) {
            console.warn(`Invalid card index: ${cardIndex}`);
            return;
        }
        
        state.isOpen = true;
        state.gridScrollPosition = window.scrollY;
        state.currentCardIndex = cardIndex;
        state.currentCardKey = state.cards[cardIndex].card_key;
        
        // Update hash (source of truth)
        updateURLHash(state.currentCardKey);
        
        // Show overlay
        overlayEl.classList.add('cv-overlay-open');
        overlayEl.setAttribute('aria-hidden', 'false');
        
        // Setup comment composers (in case they weren't initialized yet)
        setupCommentComposers();
        
        // Update focus trap elements
        updateFocusTrapElements();
        
        // Announce to screen readers
        announceToScreenReader(`Opened card ${cardIndex + 1} of ${state.totalCards}: ${state.cards[cardIndex].header}`);
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Setup focus trap
        setupFocusTrap();
        
        // Render card (no direction animation on initial open)
        renderCard(cardIndex, null);
        
        // Apply split ratio (after shell is visible)
        if (shellEl) {
            // Use setTimeout to ensure shell is rendered
            setTimeout(() => {
                applySplitRatio(state.splitRatio);
            }, 0);
        }
        
        // Render peek cards
        renderPeekCards();
        
        // Update navigation buttons
        updateNavButtons();
        
        // Load comments if needed
        loadCommentsIfNeeded(cardIndex);
        
        // Focus close button for accessibility
        const closeBtn = overlayEl.querySelector('.cv-overlay-close');
        if (closeBtn) closeBtn.focus();
    }
    
    /**
     * Close overlay
     */
    function close() {
        state.isOpen = false;
        state.commentsSheetOpen = false;
        
        // Hide overlay
        overlayEl.classList.remove('cv-overlay-open');
        overlayEl.setAttribute('aria-hidden', 'true');
        
        // Announce to screen readers
        announceToScreenReader('Card overlay closed');
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Remove focus trap
        removeFocusTrap();
        
        // Restore grid scroll position
        window.scrollTo(0, state.gridScrollPosition);
        
        // Clear hash
        updateURLHash(null);
        
        // Close comments sheet if open
        if (commentsSheetEl) {
            commentsSheetEl.classList.remove('cv-overlay-comments-sheet-open');
        }
    }
    
    /**
     * Navigate to card (without opening overlay if closed)
     */
    function navigateToCard(cardIndex, direction = null) {
        if (cardIndex < 0 || cardIndex >= state.cards.length) {
            console.warn(`Invalid card index for navigation: ${cardIndex}`);
            return;
        }
        
        const card = state.cards[cardIndex];
        if (!card) {
            console.warn(`Card at index ${cardIndex} not found`);
            return;
        }
        
        // Determine direction if not provided
        if (direction === null) {
            if (cardIndex > state.currentCardIndex) {
                direction = 'next';
            } else if (cardIndex < state.currentCardIndex) {
                direction = 'prev';
            }
        }
        
        state.navigationDirection = direction;
        state.currentCardIndex = cardIndex;
        state.currentCardKey = card.card_key;
        
        // Update hash (source of truth)
        try {
            updateURLHash(state.currentCardKey);
        } catch (e) {
            console.warn('Failed to update URL hash:', e);
            // Continue navigation even if hash update fails
        }
        
        // Render card with animation
        try {
            renderCard(cardIndex, direction);
        } catch (e) {
            console.error('Failed to render card:', e);
            // Try to recover by rendering without animation
            renderCard(cardIndex, null);
        }
        
        // Render peek cards
        renderPeekCards();
        
        // Update navigation buttons
        updateNavButtons();
        
        // Preload adjacent cards for smooth navigation
        preloadAdjacentCards(cardIndex);
        
        // Load comments if needed
        loadCommentsIfNeeded(cardIndex);
    }
    
    /**
     * Preload adjacent cards (±1) for smooth navigation
     * 
     * Pre-fetches comments for adjacent cards to reduce loading time when navigating.
     * Uses silent loading (no skeleton loaders) to avoid UI flicker.
     */
    async function preloadAdjacentCards(currentIndex) {
        // Ensure comments state is initialized
        if (!state.comments) {
            state.comments = {};
        }
        
        // Preload previous card comments
        if (currentIndex > 0 && !state.preloadedCards.has(currentIndex - 1)) {
            const prevCard = state.cards[currentIndex - 1];
            if (prevCard && prevCard.card_key) {
                state.preloadedCards.add(currentIndex - 1);
                // Silently preload comments (no UI updates)
                await preloadCommentsSilently(prevCard.card_key);
            }
        }
        
        // Preload next card comments
        if (currentIndex < state.cards.length - 1 && !state.preloadedCards.has(currentIndex + 1)) {
            const nextCard = state.cards[currentIndex + 1];
            if (nextCard && nextCard.card_key) {
                state.preloadedCards.add(currentIndex + 1);
                // Silently preload comments (no UI updates)
                await preloadCommentsSilently(nextCard.card_key);
            }
        }
    }
    
    /**
     * Preload comments silently (no UI updates, no skeleton loaders)
     * 
     * NOTE: Marks as loaded even on benign errors (404, network issues) to avoid
     * repeated failed attempts. Only skips marking on critical errors (auth failures).
     */
    async function preloadCommentsSilently(cardKey) {
        // Skip if already loaded
        if (state.commentsLoaded.has(cardKey)) {
            return;
        }
        
        // Use real API if enabled
        if (shouldUseRealApi()) {
            try {
                const apiUrl = getCommentsApiUrl(cardKey);
                if (!apiUrl) {
                    // Missing context - mark as loaded to avoid repeated attempts
                    state.comments[cardKey] = [];
                    state.commentsLoaded.add(cardKey);
                    return;
                }
                
                const response = await fetch(apiUrl, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken() || '',
                    },
                    credentials: 'same-origin',
                });
                
                if (response.ok) {
                    // Check if response is JSON before parsing
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        const data = await response.json();
                        if (data.success && Array.isArray(data.comments)) {
                            state.comments[cardKey] = data.comments;
                            state.commentsLoaded.add(cardKey);
                            return;
                        }
                    }
                } else if (response.status === 404) {
                    // Card has no comments - mark as loaded (empty array)
                    state.comments[cardKey] = [];
                    state.commentsLoaded.add(cardKey);
                    return;
                } else if (response.status === 401 || response.status === 403) {
                    // Auth failure - don't mark as loaded, will retry with proper auth
                    console.debug('Preload comments auth failure (will retry):', response.status);
                    return;
                }
                
                // Other errors - mark as loaded to avoid repeated failed attempts
                state.comments[cardKey] = [];
                state.commentsLoaded.add(cardKey);
            } catch (error) {
                // Network/other errors - mark as loaded to avoid repeated attempts
                // Preloading is best-effort, don't spam failed requests
                console.debug('Preload comments failed (non-critical):', error);
                state.comments[cardKey] = [];
                state.commentsLoaded.add(cardKey);
            }
        } else {
            // Simulation mode - just mark as loaded
            state.comments[cardKey] = state.comments[cardKey] || [];
            state.commentsLoaded.add(cardKey);
        }
    }
    
    /**
     * Navigate to previous card (with debounce and wrap-around)
     * 
     * NOTE: Navigation is debounced (150ms) to prevent rapid-fire navigation
     * when arrow keys are held down. Rapid key repeats are ignored until debounce
     * timeout completes. This is intentional to prevent animation conflicts.
     * 
     * Carousel wraps: Previous on first card goes to last card.
     */
    function previousCard() {
        if (navigationDebounceTimeout) {
            return; // Navigation in progress
        }
        
        if (state.cards.length === 0) return;
        
        let nextIndex;
        if (state.currentCardIndex > 0) {
            nextIndex = state.currentCardIndex - 1;
        } else {
            // Wrap around: first card → last card
            nextIndex = state.cards.length - 1;
        }
        
        navigateToCard(nextIndex, 'prev');
        
        // Debounce navigation
        navigationDebounceTimeout = setTimeout(() => {
            navigationDebounceTimeout = null;
        }, NAVIGATION_DEBOUNCE_MS);
    }
    
    /**
     * Navigate to next card (with debounce and wrap-around)
     * 
     * NOTE: Navigation is debounced (150ms) to prevent rapid-fire navigation
     * when arrow keys are held down. Rapid key repeats are ignored until debounce
     * timeout completes. This is intentional to prevent animation conflicts.
     * 
     * Carousel wraps: Next on last card goes to first card.
     */
    function nextCard() {
        if (navigationDebounceTimeout) {
            return; // Navigation in progress
        }
        
        if (state.cards.length === 0) return;
        
        let nextIndex;
        if (state.currentCardIndex < state.cards.length - 1) {
            nextIndex = state.currentCardIndex + 1;
        } else {
            // Wrap around: last card → first card
            nextIndex = 0;
        }
        
        navigateToCard(nextIndex, 'next');
        
        // Debounce navigation
        navigationDebounceTimeout = setTimeout(() => {
            navigationDebounceTimeout = null;
        }, NAVIGATION_DEBOUNCE_MS);
    }
    
    /**
     * Render card content in overlay
     */
    /**
     * Hide a peek card and clear its content
     */
    function hidePeek(dir) {
        const el = document.getElementById(`cv-overlay-card-${dir}`);
        if (el) {
            // Use CSS class instead of inline style to avoid overriding !important rules
            el.classList.add('cv-peek-hidden');
            // CRITICAL: Remove any inline display styles that might override CSS
            el.style.removeProperty('display');
            el.style.removeProperty('visibility');
            el.innerHTML = '';
        }
    }
    
    /**
     * Render peek cards (previous/next) for desktop
     * Hides peeks on mobile, when only 1 card, or below 768px
     * NO WRAP-AROUND: hide prev peek on first card, next peek on last card
     */
    function renderPeekCards() {
        console.log('[renderPeekCards] Called - width:', window.innerWidth, 'cards:', state.cards.length, 'index:', state.currentCardIndex);
        
        // Hide peeks on mobile, when only 1 card, or viewport < 768px
        if (window.innerWidth < 768 || state.cards.length <= 1) {
            console.log('[renderPeekCards] Hiding peeks - mobile or single card');
            hidePeek('prev');
            hidePeek('next');
            return;
        }
        
        // Desktop: render peek cards (NO WRAP-AROUND)
        const first = state.currentCardIndex === 0;
        const last = state.currentCardIndex === state.cards.length - 1;
        
        console.log('[renderPeekCards] Desktop - first:', first, 'last:', last);
        
        // Hide/show peeks based on position
        if (first) {
            console.log('[renderPeekCards] Hiding prev peek (first card)');
            hidePeek('prev');
        } else {
            console.log('[renderPeekCards] Rendering prev peek for index:', state.currentCardIndex - 1);
            renderPeekCard('prev', state.currentCardIndex - 1);
        }
        
        if (last) {
            console.log('[renderPeekCards] Hiding next peek (last card)');
            hidePeek('next');
        } else {
            console.log('[renderPeekCards] Rendering next peek for index:', state.currentCardIndex + 1);
            renderPeekCard('next', state.currentCardIndex + 1);
        }
    }
    
    /**
     * Render a single peek card
     */
    function renderPeekCard(direction, cardIndex) {
        const peekEl = document.getElementById(`cv-overlay-card-${direction}`);
        console.log('[renderPeekCard]', direction, 'index:', cardIndex, 'element:', peekEl);
        
        if (!peekEl) {
            console.error('[renderPeekCard] Element not found:', `cv-overlay-card-${direction}`);
            return;
        }
        
        if (cardIndex < 0 || cardIndex >= state.cards.length) {
            console.error('[renderPeekCard] Invalid cardIndex:', cardIndex, 'cards.length:', state.cards.length);
            return;
        }
        
        const card = state.cards[cardIndex];
        console.log('[renderPeekCard] Card data:', { header: card.header, bodyLength: card.body?.length });
        
        // Only update innerHTML if content changed (avoid unnecessary Lucide init)
        const newContent = `
            <div class="cv-overlay-card-peek-content">
                <div class="cv-overlay-card-peek-header">${escapeHtml(card.header || 'No header')}</div>
                <div class="cv-overlay-card-peek-body">${escapeHtml((card.body || '').substring(0, 100))}...</div>
            </div>
        `;
        
        // Check if content actually changed
        if (peekEl.innerHTML !== newContent) {
            peekEl.innerHTML = newContent;
            console.log('[renderPeekCard] Content updated for', direction);
            
            // Initialize Lucide icons only if content changed
            if (typeof lucide !== 'undefined') {
                lucide.createIcons(peekEl);
            }
        }
        
        // Remove hidden class and ensure visible (CSS handles display via media query)
        peekEl.classList.remove('cv-peek-hidden');
        // CRITICAL: Remove inline styles that override CSS !important rules
        peekEl.style.removeProperty('display'); // Remove inline display style completely
        peekEl.style.removeProperty('visibility'); // Remove inline visibility style completely
        
        // Debug: Log computed styles
        const computed = window.getComputedStyle(peekEl);
        console.log('[renderPeekCard]', direction, 'computed styles:', {
            display: computed.display,
            visibility: computed.visibility,
            left: computed.left,
            right: computed.right,
            width: computed.width,
            opacity: computed.opacity,
            zIndex: computed.zIndex
        });
    }
    
    function renderCard(cardIndex, direction = null) {
        const card = state.cards[cardIndex];
        if (!card || !cardContainerEl) return;
        
        // Update indicator
        if (indicatorEl) {
            indicatorEl.textContent = `Card ${cardIndex + 1} of ${state.totalCards}`;
        }
        
        // Announce to screen readers
        announceToScreenReader(`Card ${cardIndex + 1} of ${state.totalCards}: ${card.header}`);
        
        // Add direction class for animation
        if (direction) {
            // Cancel any pending animation cleanup
            if (animationTimeoutId) {
                clearTimeout(animationTimeoutId);
                animationTimeoutId = null;
            }
            
            // Remove existing animation classes
            cardContainerEl.classList.remove('cv-card-slide-prev', 'cv-card-slide-next');
            
            // Force reflow to ensure class removal is applied
            cardContainerEl.offsetHeight;
            
            // Add new direction class
            cardContainerEl.classList.add(`cv-card-slide-${direction}`);
            
            // Remove class after animation completes (use animationend event if available)
            const handleAnimationEnd = () => {
                cardContainerEl.classList.remove('cv-card-slide-prev', 'cv-card-slide-next');
                cardContainerEl.removeEventListener('animationend', handleAnimationEnd);
                animationTimeoutId = null;
            };
            
            // Use animationend event for precise cleanup, fallback to timeout
            cardContainerEl.addEventListener('animationend', handleAnimationEnd, { once: true });
            animationTimeoutId = setTimeout(() => {
                cardContainerEl.classList.remove('cv-card-slide-prev', 'cv-card-slide-next');
                animationTimeoutId = null;
            }, 250); // Slightly longer than animation duration as fallback
        }
        
        // Format card body (preserve markdown code blocks)
        let body = escapeHtml(card.body);
        body = body.replace(/```(\w*)\n([\s\S]*?)```/g, (m, lang, code) => 
            `<pre><code class="language-${lang || 'text'}">${escapeHtml(code)}</code></pre>`
        );
        
        // Get current comment count for this card
        const comments = state.comments && state.comments[card.card_key] ? state.comments[card.card_key] : [];
        const commentCount = comments.length;
        
        // Render card HTML with mobile comments toggle button
        // NOTE: The toggle button (#cv-overlay-comments-toggle-btn) is rendered dynamically here,
        // not in the static template. It's only visible on mobile (hidden on desktop via CSS).
        // The count element (#cv-overlay-comments-toggle-count) is updated by renderComments().
        cardContainerEl.innerHTML = `
            <div class="cv-overlay-card-header">${escapeHtml(card.header)}</div>
            <div class="cv-overlay-card-body">${body}</div>
            <div class="cv-overlay-card-footer">
                <button 
                    class="cv-overlay-comments-toggle-btn" 
                    id="cv-overlay-comments-toggle-btn"
                    onclick="CardOverlay.toggleCommentsSheet()"
                    aria-label="Toggle comments"
                    aria-expanded="${state.commentsSheetOpen}"
                >
                    <i data-lucide="message-circle"></i>
                    <span>Comments</span>
                    <span class="cv-overlay-comments-toggle-count" id="cv-overlay-comments-toggle-count">${commentCount}</span>
                </button>
            </div>
        `;
        
        // Initialize lucide icons (for message-circle icon in toggle button)
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Highlight syntax if Prism.js is available
        if (typeof Prism !== 'undefined') {
            Prism.highlightAllUnder(cardContainerEl);
        }
        
        // Scroll card container to top when navigating
        const cardContainer = document.querySelector('.cv-overlay-card-container');
        if (cardContainer) {
            cardContainer.scrollTop = 0;
        }
        
        // Update focus trap elements after card content changes
        updateFocusTrapElements();
        
        // Apply split ratio to persist across card navigation
        if (shellEl) {
            applySplitRatio(state.splitRatio);
        }
        
        // Render peek cards after main card (re-render to ensure they're visible if needed)
        renderPeekCards();
    }
    
    /**
     * Update navigation button states
     * 
     * Handles both side nav (desktop) and bottom nav (mobile).
     * NO WRAP-AROUND on desktop: disable/hide prev nav on first card, next nav on last card
     * Wrap-around still enabled on mobile bottom nav
     */
    function updateNavButtons() {
        const isMobile = window.innerWidth < 768;
        const isSingleCard = state.cards.length <= 1;
        const isFirstCard = state.currentCardIndex === 0;
        const isLastCard = state.currentCardIndex === state.cards.length - 1;
        
        // Side nav buttons (desktop) - NO WRAP-AROUND
        const sidePrev = document.getElementById('cv-overlay-nav-side-prev');
        const sideNext = document.getElementById('cv-overlay-nav-side-next');
        
        if (!isMobile && !isSingleCard && sidePrev && sideNext) {
            // Desktop: disable/hide prev nav on first card, next nav on last card
            if (isFirstCard) {
                sidePrev.disabled = true;
                sidePrev.style.display = 'none';
                sidePrev.setAttribute('aria-disabled', 'true');
            } else {
                sidePrev.disabled = false;
                sidePrev.style.display = 'flex';
                sidePrev.setAttribute('aria-disabled', 'false');
                sidePrev.setAttribute('aria-label', 'Previous card');
            }
            
            if (isLastCard) {
                sideNext.disabled = true;
                sideNext.style.display = 'none';
                sideNext.setAttribute('aria-disabled', 'true');
            } else {
                sideNext.disabled = false;
                sideNext.style.display = 'flex';
                sideNext.setAttribute('aria-disabled', 'false');
                sideNext.setAttribute('aria-label', 'Next card');
            }
        } else {
            // Hide on mobile or single card
            if (sidePrev) sidePrev.style.display = 'none';
            if (sideNext) sideNext.style.display = 'none';
        }
        
        // Bottom nav buttons (mobile) - WRAP-AROUND enabled
        if (prevBtnEl) {
            if (isMobile && !isSingleCard) {
                // Wrap-around: always enabled on mobile
                prevBtnEl.disabled = false;
                prevBtnEl.setAttribute('aria-disabled', 'false');
                prevBtnEl.setAttribute('aria-label', 'Previous card (wraps to last)');
                prevBtnEl.style.display = 'flex';
            } else {
                // Hide on desktop or single card
                prevBtnEl.style.display = 'none';
            }
        }
        if (nextBtnEl) {
            if (isMobile && !isSingleCard) {
                // Wrap-around: always enabled on mobile
                nextBtnEl.disabled = false;
                nextBtnEl.setAttribute('aria-disabled', 'false');
                nextBtnEl.setAttribute('aria-label', 'Next card (wraps to first)');
                nextBtnEl.style.display = 'flex';
            } else {
                // Hide on desktop or single card
                nextBtnEl.style.display = 'none';
            }
        }
    }
    
    /**
     * Load comments if needed (real API or simulation)
     * 
     * NOTE: Real API requires messageId. If missing, falls back to simulation.
     */
    async function loadCommentsIfNeeded(cardIndex) {
        const card = state.cards[cardIndex];
        if (!card || !card.card_key) return;
        
        // Ensure comments state is initialized
        if (!state.comments) {
            state.comments = {};
        }
        
        // Check if already loaded
        if (state.commentsLoaded.has(card.card_key)) {
            renderComments(cardIndex);
            return;
        }
        
        // Mark as loading
        state.commentsLoaded.add(card.card_key);
        
        // Show skeleton loader
        renderCommentsLoading(cardIndex);
        
        // Use real API if enabled and all required context available
        if (shouldUseRealApi()) {
            try {
                const apiUrl = getCommentsApiUrl(card.card_key);
                if (!apiUrl) {
                    throw new Error('Missing chat_id or card_key');
                }
                
                // Log warning about potential data mismatch
                console.warn(
                    `[Card Preview] Using real API with chat_id=${chatId}, message_id=${state.messageId}. ` +
                    `Comments will be saved to database even though card content may be unrelated to the message.`
                );
                
                const response = await fetch(apiUrl, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken() || '',
                    },
                    credentials: 'same-origin',
                });
                
                if (!response.ok) {
                    throw new Error(`API error: ${response.status} ${response.statusText}`);
                }
                
                // Check if response is JSON before parsing
                const contentType = response.headers.get('content-type');
                let data;
                if (contentType && contentType.includes('application/json')) {
                    data = await response.json();
                } else {
                    throw new Error(`Unexpected response format: ${contentType || 'unknown'}`);
                }
                
                if (data.success && Array.isArray(data.comments)) {
                    // Store comments in state
                    state.comments[card.card_key] = data.comments;
                    renderComments(cardIndex);
                } else {
                    throw new Error(data.error || 'Failed to load comments');
                }
            } catch (error) {
                console.error('Failed to load comments:', error);
                // Enhanced error handling
                const errorMessage = error.message || 'Unknown error';
                let announcement = 'Error loading comments';
                
                if (errorMessage.includes('network') || errorMessage.includes('fetch') || errorMessage.includes('Failed to fetch')) {
                    announcement = 'Network error: Unable to load comments. Please check your connection.';
                } else if (errorMessage.includes('401') || errorMessage.includes('403')) {
                    announcement = 'Permission denied: Unable to load comments.';
                } else if (errorMessage.includes('JSON') || errorMessage.includes('Unexpected response')) {
                    announcement = 'Server error: Invalid response format.';
                } else {
                    announcement = `Error loading comments: ${errorMessage}`;
                }
                
                announceToScreenReader(announcement);
                // Fallback to empty comments on error
                state.comments[card.card_key] = [];
                renderComments(cardIndex);
            }
        } else {
            // Simulation mode (in-memory only)
            setTimeout(() => {
                state.comments[card.card_key] = state.comments[card.card_key] || [];
                renderComments(cardIndex);
            }, 300);
        }
    }
    
    /**
     * Render skeleton loader for comments
     */
    function renderCommentsLoading(cardIndex) {
        const skeletonHtml = `
            <div class="cv-overlay-comments-loading">
                <div class="cv-comment-skeleton">
                    <div class="cv-skeleton-avatar"></div>
                    <div class="cv-skeleton-content">
                        <div class="cv-skeleton-line cv-skeleton-line-short"></div>
                        <div class="cv-skeleton-line"></div>
                    </div>
                </div>
                <div class="cv-comment-skeleton">
                    <div class="cv-skeleton-avatar"></div>
                    <div class="cv-skeleton-content">
                        <div class="cv-skeleton-line"></div>
                        <div class="cv-skeleton-line cv-skeleton-line-short"></div>
                    </div>
                </div>
            </div>
        `;
        
        // Render in desktop pane
        const listEl = document.getElementById('cv-overlay-comments-list');
        if (listEl) {
            listEl.innerHTML = skeletonHtml;
        }
        
        // Render in mobile sheet
        const sheetListEl = document.getElementById('cv-overlay-comments-sheet-list');
        if (sheetListEl) {
            sheetListEl.innerHTML = skeletonHtml;
        }
    }
    
    /**
     * Render comments for current card
     * 
     * NOTE: Comments are simulated in preview mode (in-memory state only).
     * Comments persist per-session but are not saved to database.
     * In production, this would fetch from /chat/<chat_id>/cards/<card_key>/comments API.
     */
    function renderComments(cardIndex) {
        const card = state.cards[cardIndex];
        if (!card) return;
        
        // Ensure comments state is initialized
        if (!state.comments) {
            state.comments = {};
        }
        
        // Get comments from state (simulation for preview)
        // In real implementation: fetch from API
        const comments = state.comments[card.card_key] || [];
        const commentCount = comments.length;
        
        // Update count (desktop pane header)
        const countEl = document.getElementById('cv-overlay-comments-count');
        if (countEl) {
            countEl.textContent = commentCount;
        }
        
        // Update count (mobile toggle button in card footer - dynamically rendered)
        // Note: This element only exists after renderCard() has been called
        const toggleCountEl = document.getElementById('cv-overlay-comments-toggle-count');
        if (toggleCountEl) {
            toggleCountEl.textContent = commentCount;
        }
        
        // Update count (mobile sheet header)
        const sheetCountEl = document.getElementById('cv-overlay-comments-sheet-count');
        if (sheetCountEl) {
            sheetCountEl.textContent = commentCount;
        }
        
        // Render comments list (desktop)
        const listEl = document.getElementById('cv-overlay-comments-list');
        if (listEl) {
            if (comments.length === 0) {
                listEl.innerHTML = `
                    <div class="cv-overlay-comments-empty">
                        <i data-lucide="message-circle"></i>
                        <p>No comments yet. Be the first!</p>
                    </div>
                `;
            } else {
                // Render comments with visual distinction for AI vs user
                listEl.innerHTML = comments.map((comment, idx) => {
                    const isAi = comment.content_type === 'ai';
                    const commentClass = isAi ? 'cv-overlay-comment cv-overlay-comment-ai' : 'cv-overlay-comment cv-overlay-comment-user';
                    const isNew = idx === comments.length - 1; // Mark last comment as new for auto-scroll
                    return `
                    <div class="${commentClass}" data-comment-id="${comment.id}" ${isNew ? 'data-new-comment="true"' : ''}>
                        <div class="cv-overlay-comment-author">
                            ${isAi ? '<i data-lucide="sparkles" class="cv-comment-ai-icon"></i>' : ''}
                            ${escapeHtml(comment.user?.display_name || 'User')}
                        </div>
                        <div class="cv-overlay-comment-text">${escapeHtml(comment.content)}</div>
                        <div class="cv-overlay-comment-time">${formatTime(comment.created_at)}</div>
                    </div>
                `;
                }).join('');
                
                // Auto-scroll to newest comment
                const newCommentEl = listEl.querySelector('[data-new-comment="true"]');
                if (newCommentEl) {
                    setTimeout(() => {
                        newCommentEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                        // Remove marker after scroll
                        newCommentEl.removeAttribute('data-new-comment');
                    }, 100);
                }
            }
        }
        
        // Render comments sheet (mobile)
        const sheetListEl = document.getElementById('cv-overlay-comments-sheet-list');
        if (sheetListEl) {
            sheetListEl.innerHTML = listEl ? listEl.innerHTML : '';
            
            // Auto-scroll to newest comment in mobile sheet too
            const newCommentEl = sheetListEl.querySelector('[data-new-comment="true"]');
            if (newCommentEl) {
                setTimeout(() => {
                    newCommentEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    newCommentEl.removeAttribute('data-new-comment');
                }, 100);
            }
        }
        
        // Initialize icons (for AI sparkles icons)
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Update focus trap elements after comments render (new focusable elements may be added)
        updateFocusTrapElements();
    }
    
    /**
     * Add comment (real API or simulation)
     */
    async function addComment(isMobile = false) {
        const inputId = isMobile ? 'cv-overlay-comment-input-mobile' : 'cv-overlay-comment-input';
        const input = document.getElementById(inputId);
        if (!input) return;
        
        const content = input.value.trim();
        if (!content) return;
        
        const card = state.cards[state.currentCardIndex];
        if (!card || !card.card_key) return;
        
        // Ensure comments state is initialized
        if (!state.comments) {
            state.comments = {};
        }
        
        // Disable input during submission
        input.disabled = true;
        
        try {
            if (shouldUseRealApi()) {
                // Real API call
                const apiUrl = getCommentsApiUrl(card.card_key);
                if (!apiUrl) {
                    throw new Error('Missing chat_id or card_key');
                }
                
                // Double-check required fields (shouldUseRealApi already checks, but be defensive)
                if (!state.messageId || card.segment_index === undefined) {
                    console.warn('Missing message_id or segment_index, falling back to simulation');
                    // Fall back to simulation
                    if (!state.comments[card.card_key]) {
                        state.comments[card.card_key] = [];
                    }
                    const newComment = {
                        id: `sim-${Date.now()}`,
                        content: content,
                        content_type: 'user',
                        user: { display_name: 'You (Preview)' },
                        created_at: new Date().toISOString()
                    };
                    state.comments[card.card_key].push(newComment);
                    input.value = '';
                    input.style.height = 'auto';
                    renderComments(state.currentCardIndex);
                    setTimeout(() => input.focus(), 50);
                    return;
                }
                
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken() || '',
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({
                        content: content,
                        message_id: state.messageId,
                        segment_index: card.segment_index,
                        segment_body: card.body ? card.body.substring(0, 200) : undefined,
                    }),
                });
                
                if (!response.ok) {
                    // Check if response is JSON before parsing
                    const contentType = response.headers.get('content-type');
                    let errorData = {};
                    if (contentType && contentType.includes('application/json')) {
                        try {
                            errorData = await response.json();
                        } catch (e) {
                            // Non-JSON error response
                            errorData = { error: `HTTP ${response.status}: ${response.statusText}` };
                        }
                    } else {
                        errorData = { error: `HTTP ${response.status}: ${response.statusText}` };
                    }
                    throw new Error(errorData.error || `API error: ${response.status}`);
                }
                
                // Check if response is JSON before parsing
                const contentType = response.headers.get('content-type');
                let data;
                if (contentType && contentType.includes('application/json')) {
                    data = await response.json();
                } else {
                    throw new Error(`Unexpected response format: ${contentType || 'unknown'}`);
                }
                if (data.success && data.comment) {
                    // Add comment to state
                    if (!state.comments[card.card_key]) {
                        state.comments[card.card_key] = [];
                    }
                    state.comments[card.card_key].push(data.comment);
                    
                    // Clear input and reset height
                    input.value = '';
                    input.style.height = 'auto';
                    
                    // Re-render comments
                    renderComments(state.currentCardIndex);
                    
                    // Focus input again
                    setTimeout(() => {
                        input.focus();
                    }, 50);
                } else {
                    throw new Error(data.error || 'Failed to add comment');
                }
            } else {
                // Simulation mode
                if (!state.comments[card.card_key]) {
                    state.comments[card.card_key] = [];
                }
                
                const newComment = {
                    id: `sim-${Date.now()}`,
                    content: content,
                    content_type: 'user',
                    user: { display_name: 'You (Preview)' },
                    created_at: new Date().toISOString()
                };
                
                state.comments[card.card_key].push(newComment);
                
                // Clear input and reset height
                input.value = '';
                input.style.height = 'auto';
                
                // Re-render comments
                renderComments(state.currentCardIndex);
                
                // Focus input again
                setTimeout(() => {
                    input.focus();
                }, 50);
            }
        } catch (error) {
            console.error('Failed to add comment:', error);
            const errorMessage = error.message || 'Unknown error';
            
            // Enhanced error handling with user-friendly messages
            let userMessage = 'Failed to add comment';
            if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
                userMessage = 'Network error: Unable to post comment. Please check your connection.';
            } else if (errorMessage.includes('401') || errorMessage.includes('403')) {
                userMessage = 'Permission denied: Unable to post comment.';
            } else if (errorMessage.includes('400')) {
                userMessage = 'Invalid request: ' + errorMessage;
            } else {
                userMessage = `Error: ${errorMessage}`;
            }
            
            alert(userMessage);
            announceToScreenReader(userMessage);
        } finally {
            input.disabled = false;
        }
    }
    
    /**
     * Request AI reply (real API or simulation)
     */
    async function requestAiReply(isMobile = false) {
        const card = state.cards[state.currentCardIndex];
        if (!card || !card.card_key) return;
        
        // Ensure comments state is initialized
        if (!state.comments) {
            state.comments = {};
        }
        
        // Check consecutive AI replies guard (max 2) - only in simulation
        if (!shouldUseRealApi()) {
            const comments = state.comments[card.card_key] || [];
            const recentAiCount = comments.slice(-2).filter(c => c.content_type === 'ai').length;
            
            if (recentAiCount >= 2) {
                alert('You\'ve used 2 AI replies in a row. What do you think?');
                return;
            }
        }
        
        // Show loading state
        const listEl = document.getElementById(isMobile ? 'cv-overlay-comments-sheet-list' : 'cv-overlay-comments-list');
        if (listEl) {
            const loadingHtml = listEl.innerHTML + `
                <div class="cv-overlay-comment cv-overlay-comment-loading">
                    <div class="cv-overlay-comment-author">AI</div>
                    <div class="cv-overlay-comment-text">
                        <div class="cv-comment-skeleton-inline">
                            <div class="cv-skeleton-line"></div>
                            <div class="cv-skeleton-line cv-skeleton-line-short"></div>
                        </div>
                    </div>
                </div>
            `;
            listEl.innerHTML = loadingHtml;
        }
        
        try {
            if (shouldUseRealApi()) {
                // Real API call
                const apiUrl = getCommentsApiUrl(card.card_key) + '/ai';
                if (!apiUrl || !apiUrl.includes('/ai')) {
                    throw new Error('Missing chat_id or card_key');
                }
                
                // Double-check required fields (shouldUseRealApi already checks, but be defensive)
                if (!state.messageId || card.segment_index === undefined || !card.body) {
                    console.warn('Missing message_id, segment_index, or card_body, falling back to simulation');
                    // Fall back to simulation
                    setTimeout(() => {
                        if (!state.comments[card.card_key]) {
                            state.comments[card.card_key] = [];
                        }
                        const aiComment = {
                            id: `sim-ai-${Date.now()}`,
                            content: 'This is a simulated AI reply. Real API requires message_id, segment_index, and card_body.',
                            content_type: 'ai',
                            user: { display_name: 'AI Assistant' },
                            created_at: new Date().toISOString()
                        };
                        state.comments[card.card_key].push(aiComment);
                        renderComments(state.currentCardIndex);
                    }, 1500);
                    return;
                }
                
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken() || '',
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({
                        message_id: state.messageId,
                        segment_index: card.segment_index,
                        card_header: card.header || '',
                        card_body: card.body,
                        segment_body: card.body ? card.body.substring(0, 200) : undefined,
                        guiding_question: state.guidingQuestion || '',
                    }),
                });
                
                if (!response.ok) {
                    // Check if response is JSON before parsing
                    const contentType = response.headers.get('content-type');
                    let errorData = {};
                    if (contentType && contentType.includes('application/json')) {
                        try {
                            errorData = await response.json();
                        } catch (e) {
                            // Non-JSON error response
                            errorData = { error: `HTTP ${response.status}: ${response.statusText}` };
                        }
                    } else {
                        errorData = { error: `HTTP ${response.status}: ${response.statusText}` };
                    }
                    
                    // Handle "what_do_you_think" error (429)
                    if (response.status === 429 && errorData.error === 'what_do_you_think') {
                        const message = errorData.message || 'You\'ve used 2 AI replies in a row. What do you think?';
                        alert(message);
                        announceToScreenReader(message);
                        // Reload comments to get updated state
                        state.commentsLoaded.delete(card.card_key);
                        loadCommentsIfNeeded(state.currentCardIndex);
                        return;
                    }
                    throw new Error(errorData.error || `API error: ${response.status}`);
                }
                
                // Check if response is JSON before parsing
                const contentType = response.headers.get('content-type');
                let data;
                if (contentType && contentType.includes('application/json')) {
                    data = await response.json();
                } else {
                    throw new Error(`Unexpected response format: ${contentType || 'unknown'}`);
                }
                if (data.success && data.comment) {
                    // Add comment to state
                    if (!state.comments[card.card_key]) {
                        state.comments[card.card_key] = [];
                    }
                    state.comments[card.card_key].push(data.comment);
                    
                    // Re-render comments
                    renderComments(state.currentCardIndex);
                } else {
                    throw new Error(data.error || 'Failed to generate AI reply');
                }
            } else {
                // Simulation mode
                setTimeout(() => {
                    if (!state.comments[card.card_key]) {
                        state.comments[card.card_key] = [];
                    }
                    
                    const aiComment = {
                        id: `sim-ai-${Date.now()}`,
                        content: 'This is a simulated AI reply. In production, this would be generated by the AI service.',
                        content_type: 'ai',
                        user: { display_name: 'AI Assistant' },
                        created_at: new Date().toISOString()
                    };
                    
                    state.comments[card.card_key].push(aiComment);
                    
                    // Re-render comments
                    renderComments(state.currentCardIndex);
                }, 1500);
            }
        } catch (error) {
            console.error('Failed to generate AI reply:', error);
            const errorMessage = error.message || 'Unknown error';
            
            // Enhanced error handling with user-friendly messages
            let userMessage = 'Failed to generate AI reply';
            if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
                userMessage = 'Network error: Unable to generate AI reply. Please check your connection.';
            } else if (errorMessage.includes('429')) {
                userMessage = 'Rate limit exceeded: Please wait a moment before requesting another AI reply.';
            } else if (errorMessage.includes('503') || errorMessage.includes('unavailable')) {
                userMessage = 'AI service unavailable: Please try again later.';
            } else {
                userMessage = `Error: ${errorMessage}`;
            }
            
            alert(userMessage);
            announceToScreenReader(userMessage);
            
            // Reload comments to refresh state
            state.commentsLoaded.delete(card.card_key);
            loadCommentsIfNeeded(state.currentCardIndex);
        }
    }
    
    /**
     * Toggle comments sheet (mobile)
     */
    function toggleCommentsSheet() {
        state.commentsSheetOpen = !state.commentsSheetOpen;
        
        if (commentsSheetEl) {
            if (state.commentsSheetOpen) {
                commentsSheetEl.classList.add('cv-overlay-comments-sheet-open');
                // Setup composer when opening
                setupCommentComposers();
                // Update focus trap elements (sheet is now visible)
                updateFocusTrapElements();
                // Announce to screen readers
                announceToScreenReader('Comments sheet opened');
            } else {
                commentsSheetEl.classList.remove('cv-overlay-comments-sheet-open');
                // Update focus trap elements
                updateFocusTrapElements();
                // Announce to screen readers
                announceToScreenReader('Comments sheet closed');
            }
        }
        
        // Update ARIA expanded attribute on toggle button
        const toggleBtn = document.querySelector('.cv-overlay-comments-toggle-btn');
        if (toggleBtn) {
            toggleBtn.setAttribute('aria-expanded', state.commentsSheetOpen);
        }
        
        // Load comments if opening sheet and not already loaded
        if (state.commentsSheetOpen) {
            loadCommentsIfNeeded(state.currentCardIndex);
        }
    }
    
    /**
     * Handle keyboard events
     */
    function handleKeyboard(e) {
        if (!state.isOpen) return;
        
        switch(e.key) {
            case 'Escape':
                e.preventDefault();
                close();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                previousCard();
                break;
            case 'ArrowRight':
                e.preventDefault();
                nextCard();
                break;
            case 'Tab':
                // Handle focus trap - keep focus within overlay
                handleFocusTrap(e);
                break;
        }
    }
    
    /**
     * Update focus trap elements list
     */
    function updateFocusTrapElements() {
        if (!overlayEl) return;
        
        focusTrapElements = Array.from(overlayEl.querySelectorAll(
            'button, [href], input, textarea, select, [tabindex]:not([tabindex="-1"])'
        )).filter(el => {
            // Only include visible, focusable elements
            const style = window.getComputedStyle(el);
            return style.display !== 'none' && 
                   style.visibility !== 'hidden' && 
                   !el.disabled &&
                   el.tabIndex !== -1;
        });
    }
    
    /**
     * Setup focus trap to keep focus within overlay
     */
    function setupFocusTrap() {
        if (!overlayEl) return;
        
        // Focus first focusable element
        if (focusTrapElements.length > 0) {
            focusTrapElements[0].focus();
        }
    }
    
    /**
     * Handle focus trap on Tab key
     */
    function handleFocusTrap(e) {
        if (!overlayEl || focusTrapElements.length === 0) return;
        
        const firstElement = focusTrapElements[0];
        const lastElement = focusTrapElements[focusTrapElements.length - 1];
        const activeElement = document.activeElement;
        
        // If Shift+Tab on first element, wrap to last
        if (e.shiftKey && activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
        }
        // If Tab on last element, wrap to first
        else if (!e.shiftKey && activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
        }
    }
    
    /**
     * Remove focus trap
     */
    function removeFocusTrap() {
        // Focus is restored to grid when overlay closes
        // No cleanup needed
    }
    
    /**
     * Announce to screen readers via ARIA live region
     */
    function announceToScreenReader(message) {
        if (ariaLiveEl) {
            ariaLiveEl.textContent = message;
            // Clear after announcement to allow re-announcement of same message
            setTimeout(() => {
                if (ariaLiveEl) {
                    ariaLiveEl.textContent = '';
                }
            }, 1000);
        }
    }
    
    /**
     * Format time for display
     */
    function formatTime(isoString) {
        if (!isoString) return '';
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
        return date.toLocaleDateString();
    }
    
    /**
     * Load split ratio from localStorage
     */
    function loadSplitRatio() {
        try {
            const stored = localStorage.getItem(SPLITTER_STORAGE_KEY);
            if (stored) {
                const ratio = parseFloat(stored);
                // Validate range (0.3 to 0.8)
                if (!isNaN(ratio) && ratio >= 0.3 && ratio <= 0.8) {
                    return ratio;
                }
            }
        } catch (e) {
            console.warn('Failed to load split ratio from localStorage:', e);
        }
        return DEFAULT_SPLIT_RATIO;
    }
    
    /**
     * Save split ratio to localStorage (save unclamped ratio, clamping happens on apply)
     */
    function saveSplitRatio(ratio) {
        try {
            // Save unclamped ratio - clamping will happen on apply based on current shell width
            localStorage.setItem(SPLITTER_STORAGE_KEY, ratio.toString());
            state.splitRatio = ratio;
        } catch (e) {
            console.warn('Failed to save split ratio to localStorage:', e);
        }
    }
    
    /**
     * Clamp split ratio based on shell width and min widths
     */
    function clampSplitRatio(ratio, shellWidth) {
        // Min ratio: cardWidth >= MIN_CARD_WIDTH
        const minRatio = MIN_CARD_WIDTH / shellWidth;
        // Max ratio: commentsWidth >= MIN_COMMENTS_WIDTH
        // commentsWidth = shellWidth * (1 - ratio) - SPLITTER_WIDTH >= MIN_COMMENTS_WIDTH
        // => shellWidth * (1 - ratio) >= MIN_COMMENTS_WIDTH + SPLITTER_WIDTH
        // => 1 - ratio >= (MIN_COMMENTS_WIDTH + SPLITTER_WIDTH) / shellWidth
        // => ratio <= 1 - (MIN_COMMENTS_WIDTH + SPLITTER_WIDTH) / shellWidth
        const maxRatio = 1 - (MIN_COMMENTS_WIDTH + SPLITTER_WIDTH) / shellWidth;
        return Math.max(minRatio, Math.min(maxRatio, ratio));
    }
    
    /**
     * Get shell padding (computed, not hardcoded)
     */
    function getShellPadding() {
        if (!shellEl) return 0;
        const computedStyle = window.getComputedStyle(shellEl);
        const paddingLeft = parseFloat(computedStyle.paddingLeft) || 0;
        const paddingRight = parseFloat(computedStyle.paddingRight) || 0;
        return paddingLeft + paddingRight;
    }
    
    /**
     * Apply split ratio to card column and comments pane
     */
    function applySplitRatio(ratio) {
        if (!shellEl || !cardColumnEl || !commentsPaneEl || !splitterEl) {
            return;
        }
        
        // Get shell width (accounting for computed padding)
        const shellRect = shellEl.getBoundingClientRect();
        const shellPadding = getShellPadding();
        const shellWidth = shellRect.width - shellPadding;
        
        // Clamp ratio first
        const clampedRatio = clampSplitRatio(ratio, shellWidth);
        
        // Calculate widths
        const cardWidth = shellWidth * clampedRatio;
        const commentsWidth = shellWidth * (1 - clampedRatio) - SPLITTER_WIDTH;
        
        // Calculate min/max ratios for ARIA
        const minRatio = MIN_CARD_WIDTH / shellWidth;
        const maxRatio = 1 - (MIN_COMMENTS_WIDTH + SPLITTER_WIDTH) / shellWidth;
        
        // Apply via inline styles (flex-basis)
        cardColumnEl.style.flex = `0 0 ${cardWidth}px`;
        commentsPaneEl.style.flex = `0 0 ${commentsWidth}px`;
        
        // Update ARIA attributes for screen readers
        splitterEl.setAttribute('aria-valuenow', Math.round(clampedRatio * 100));
        splitterEl.setAttribute('aria-valuemin', Math.round(minRatio * 100));
        splitterEl.setAttribute('aria-valuemax', Math.round(maxRatio * 100));
        
        // Update state
        state.splitRatio = clampedRatio;
    }
    
    /**
     * Start drag (shared by mouse and touch)
     */
    function startSplitterDrag(clientX) {
        if (!shellEl || !cardColumnEl) {
            return;
        }
        
        state.isDragging = true;
        splitterEl.classList.add('dragging');
        
        // Capture initial values
        splitterDragStartX = clientX;
        const cardRect = cardColumnEl.getBoundingClientRect();
        splitterInitialCardWidth = cardRect.width;
        const shellRect = shellEl.getBoundingClientRect();
        const shellPadding = getShellPadding();
        splitterShellWidth = shellRect.width - shellPadding;
        
        // Prevent text selection during drag
        document.body.style.userSelect = 'none';
    }
    
    /**
     * Handle splitter mouse down (start drag)
     */
    function handleSplitterMouseDown(e) {
        e.preventDefault();
        e.stopPropagation();
        startSplitterDrag(e.clientX);
        
        // Attach listeners to document (not splitter) to track mouse outside
        document.addEventListener('mousemove', handleSplitterMouseMove);
        document.addEventListener('mouseup', handleSplitterMouseUp);
    }
    
    /**
     * Handle splitter touch start (start drag)
     */
    function handleSplitterTouchStart(e) {
        if (e.touches.length !== 1) return; // Ignore multi-touch
        e.preventDefault();
        e.stopPropagation();
        startSplitterDrag(e.touches[0].clientX);
        
        // Attach listeners to document (not splitter) to track touch outside
        document.addEventListener('touchmove', handleSplitterTouchMove, { passive: false });
        document.addEventListener('touchend', handleSplitterTouchEnd);
        document.addEventListener('touchcancel', handleSplitterTouchEnd);
    }
    
    /**
     * Handle drag move (shared by mouse and touch)
     */
    function handleSplitterDragMove(clientX) {
        if (!state.isDragging) {
            return;
        }
        
        // Calculate delta
        const deltaX = clientX - splitterDragStartX;
        const newCardWidth = splitterInitialCardWidth + deltaX;
        const newRatio = newCardWidth / splitterShellWidth;
        
        // Clamp ratio
        const clampedRatio = clampSplitRatio(newRatio, splitterShellWidth);
        
        // Schedule update via requestAnimationFrame (throttle)
        if (splitterRafId === null) {
            splitterRafId = requestAnimationFrame(() => {
                applySplitRatio(clampedRatio);
                splitterRafId = null;
            });
        }
    }
    
    /**
     * Handle splitter mouse move (during drag)
     */
    function handleSplitterMouseMove(e) {
        e.preventDefault();
        handleSplitterDragMove(e.clientX);
    }
    
    /**
     * Handle splitter touch move (during drag)
     */
    function handleSplitterTouchMove(e) {
        if (e.touches.length !== 1) return; // Ignore multi-touch
        e.preventDefault();
        handleSplitterDragMove(e.touches[0].clientX);
    }
    
    /**
     * End drag (shared by mouse and touch)
     */
    function endSplitterDrag() {
        if (!state.isDragging) {
            return;
        }
        
        // Remove dragging class
        splitterEl.classList.remove('dragging');
        
        // Remove mouse listeners
        document.removeEventListener('mousemove', handleSplitterMouseMove);
        document.removeEventListener('mouseup', handleSplitterMouseUp);
        
        // Remove touch listeners
        document.removeEventListener('touchmove', handleSplitterTouchMove);
        document.removeEventListener('touchend', handleSplitterTouchEnd);
        document.removeEventListener('touchcancel', handleSplitterTouchEnd);
        
        // Cancel pending rAF
        if (splitterRafId !== null) {
            cancelAnimationFrame(splitterRafId);
            splitterRafId = null;
        }
        
        // Save ratio to localStorage
        saveSplitRatio(state.splitRatio);
        
        // Reset drag state
        state.isDragging = false;
        
        // Restore user-select
        document.body.style.userSelect = '';
    }
    
    /**
     * Handle splitter mouse up (end drag)
     */
    function handleSplitterMouseUp(e) {
        endSplitterDrag();
    }
    
    /**
     * Handle splitter touch end (end drag)
     */
    function handleSplitterTouchEnd(e) {
        endSplitterDrag();
    }
    
    /**
     * Handle splitter keyboard events
     */
    function handleSplitterKeyboard(e) {
        if (!splitterEl || !shellEl) {
            return;
        }
        
        let newRatio = state.splitRatio;
        let announceChange = false;
        
        switch (e.key) {
            case 'ArrowLeft':
                e.preventDefault();
                newRatio = state.splitRatio - KEYBOARD_NUDGE;
                announceChange = true;
                break;
            case 'ArrowRight':
                e.preventDefault();
                newRatio = state.splitRatio + KEYBOARD_NUDGE;
                announceChange = true;
                break;
            case 'Escape':
                e.preventDefault();
                resetSplitRatio();
                return;
            case 'Enter':
            case ' ':
                // No-op, splitter already focused
                return;
            default:
                return; // Ignore other keys
        }
        
        // Clamp and apply
        const shellRect = shellEl.getBoundingClientRect();
        const shellPadding = getShellPadding();
        const shellWidth = shellRect.width - shellPadding;
        const clampedRatio = clampSplitRatio(newRatio, shellWidth);
        applySplitRatio(clampedRatio);
        saveSplitRatio(clampedRatio);
        
        // Announce change to screen readers
        if (announceChange && ariaLiveEl) {
            ariaLiveEl.textContent = `Splitter ratio: ${Math.round(clampedRatio * 100)}%`;
        }
    }
    
    /**
     * Reset split ratio to default
     */
    function resetSplitRatio() {
        applySplitRatio(DEFAULT_SPLIT_RATIO);
        saveSplitRatio(DEFAULT_SPLIT_RATIO);
        
        // Announce reset to screen readers
        if (ariaLiveEl) {
            ariaLiveEl.textContent = `Splitter reset to default ratio`;
        }
    }
    
    /**
     * Handle window resize - reclamp split ratio
     */
    function handleSplitterWindowResize() {
        if (!state.isOpen || !shellEl) {
            return;
        }
        
        const shellRect = shellEl.getBoundingClientRect();
        const shellPadding = getShellPadding();
        const shellWidth = shellRect.width - shellPadding;
        const clampedRatio = clampSplitRatio(state.splitRatio, shellWidth);
        
        // Only update if ratio changed due to clamping
        if (clampedRatio !== state.splitRatio) {
            applySplitRatio(clampedRatio);
            saveSplitRatio(clampedRatio);
        } else {
            // Reapply to ensure min widths respected
            applySplitRatio(state.splitRatio);
        }
    }
    
    /**
     * Initialize splitter
     */
    function initSplitter() {
        splitterEl = document.getElementById('cv-overlay-splitter');
        cardColumnEl = document.querySelector('.cv-overlay-card-column');
        shellEl = document.querySelector('.cv-overlay-shell');
        
        if (!splitterEl || !cardColumnEl || !shellEl) {
            return; // Elements not found (mobile or not loaded yet)
        }
        
        // Load ratio from localStorage
        state.splitRatio = loadSplitRatio();
        
        // Attach event listeners
        splitterEl.addEventListener('mousedown', handleSplitterMouseDown);
        splitterEl.addEventListener('touchstart', handleSplitterTouchStart, { passive: false });
        splitterEl.addEventListener('keydown', handleSplitterKeyboard);
        
        // Optional: Double-click to reset
        splitterEl.addEventListener('dblclick', (e) => {
            e.preventDefault();
            resetSplitRatio();
        });
        
        // Initialize ARIA attributes
        const shellRect = shellEl.getBoundingClientRect();
        const shellPadding = getShellPadding();
        const shellWidth = shellRect.width - shellPadding;
        const minRatio = MIN_CARD_WIDTH / shellWidth;
        const maxRatio = 1 - (MIN_COMMENTS_WIDTH + SPLITTER_WIDTH) / shellWidth;
        splitterEl.setAttribute('aria-valuemin', Math.round(minRatio * 100));
        splitterEl.setAttribute('aria-valuemax', Math.round(maxRatio * 100));
    }
    
    /**
     * Set cards data (called from preview page)
     */
    function setCardsData(cards, guidingQuestion = null, relationships = [], messageId = null) {
        // Ensure cards preserve card_key and segment_index from segmentation
        state.cards = cards.map((card, index) => ({
            ...card,
            card_key: card.card_key || card.cardKey, // Support both formats
            segment_index: card.segment_index !== undefined ? card.segment_index : index,
        }));
        state.totalCards = state.cards.length;
        state.guidingQuestion = guidingQuestion;
        state.relationships = relationships;
        // Use provided messageId or fall back to initial messageId from page
        state.messageId = messageId || initialMessageId;
    }
    
    // Public API
    return {
        init,
        renderGrid,
        setCardsData,
        openCard,
        close,
        previousCard,
        nextCard,
        addComment,
        requestAiReply,
        toggleCommentsSheet,
        getState: () => ({ ...state }), // Read-only access to state
        get state() { return state; }, // Direct access to state for debugging (getter)
        renderPeekCards: renderPeekCards // Expose for debugging
    };
})();

// Debug: Log if CardOverlay was created successfully
try {
    console.log('[CardOverlay] Module IIFE completed, CardOverlay type:', typeof CardOverlay);
    
    // Expose CardOverlay to window for debugging
    window.CardOverlay = CardOverlay;
    
    // Debug: Verify exposure
    console.log('[CardOverlay] Exposed to window:', typeof window.CardOverlay !== 'undefined' ? 'SUCCESS' : 'FAILED');
    
    // Debug: Expose state accessor (since getter might not work in all browsers)
    // Access state via CardOverlay.getState() or CardOverlay.state
    if (typeof CardOverlay !== 'undefined' && CardOverlay && typeof CardOverlay.getState === 'function') {
        // Add state property for easier debugging
        Object.defineProperty(CardOverlay, 'state', {
            get: function() {
                return CardOverlay.getState();
            },
            enumerable: true,
            configurable: true
        });
        console.log('[CardOverlay] state accessor added, test:', typeof CardOverlay.state);
    } else {
        console.error('[CardOverlay] Failed to add state accessor - CardOverlay:', CardOverlay, 'getState:', typeof CardOverlay?.getState);
    }
} catch (e) {
    console.error('[CardOverlay] Error during module exposure:', e);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', CardOverlay.init);
} else {
    CardOverlay.init();
}

