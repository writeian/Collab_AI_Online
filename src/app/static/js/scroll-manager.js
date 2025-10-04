/**
 * ChatScrollManager - Unified scroll management for chat interface
 * Version: 1.0
 * Phase: 1 - Scroll Consolidation
 * 
 * Replaces 7+ scattered scroll handlers with single, testable class
 * Feature flag: CHAT_NEW_SCROLL_MANAGER
 */

class ChatScrollManager {
    constructor(options = {}) {
        // Configuration
        this.enabled = options.enabled !== false;
        this.debug = options.debug || false;
        
        // DOM elements
        this.chatMessages = document.getElementById('chat-messages');
        this.scrollButton = document.getElementById('scroll-to-bottom');
        this.inputContainer = document.querySelector('.chat-input-container');
        
        // State tracking
        this.lastScrollTop = 0;
        this.lastScrollTime = 0;
        this.isUserScrolling = false;
        this.scrollTimeout = null;
        this.autoScrollEnabled = true;
        
        // Device detection
        this.isMobile = this._detectMobile();
        
        // Thresholds
        this.nearBottomThreshold = this.isMobile ? 50 : 100;
        this.userScrollIdleTime = 1000; // 1 second
        
        if (!this.chatMessages) {
            console.warn('ChatScrollManager: #chat-messages not found');
            return;
        }
        
        this.log('Initializing ScrollManager', {
            isMobile: this.isMobile,
            threshold: this.nearBottomThreshold
        });
        
        this.init();
    }
    
    /**
     * Initialize scroll manager
     */
    init() {
        // Setup event listeners
        this.setupScrollListener();
        this.setupScrollButton();
        this.setupResizeHandler();
        
        // Initial scroll to bottom on page load
        this.scrollToBottomOnLoad();
        
        // Track metrics
        if (typeof window.CHAT_METRICS === 'undefined') {
            window.CHAT_METRICS = {};
        }
        window.CHAT_METRICS.scrollManagerActive = true;
        window.CHAT_METRICS.scrollManagerErrors = 0;
        
        this.log('ScrollManager initialized successfully');
    }
    
    /**
     * Setup scroll event listener with user intent tracking
     */
    setupScrollListener() {
        if (!this.chatMessages) return;
        
        this.chatMessages.addEventListener('scroll', () => {
            this.handleScroll();
        }, { passive: true });
    }
    
    /**
     * Handle scroll event
     */
    handleScroll() {
        const now = Date.now();
        const currentScrollTop = this.chatMessages.scrollTop;
        
        // Track user scroll intent
        if (Math.abs(currentScrollTop - this.lastScrollTop) > 5) {
            this.markUserScroll();
        }
        
        this.lastScrollTop = currentScrollTop;
        this.lastScrollTime = now;
        
        // Update scroll button visibility
        this.updateScrollButton();
    }
    
    /**
     * Mark that user is actively scrolling
     */
    markUserScroll() {
        this.isUserScrolling = true;
        clearTimeout(this.scrollTimeout);
        
        // Clear scrolling flag after idle period
        this.scrollTimeout = setTimeout(() => {
            this.isUserScrolling = false;
            this.log('User scroll idle');
        }, this.userScrollIdleTime);
    }
    
    /**
     * Setup scroll-to-bottom button
     */
    setupScrollButton() {
        if (!this.scrollButton) return;
        
        this.scrollButton.addEventListener('click', () => {
            this.scrollToBottom(true);
        });
    }
    
    /**
     * Setup window resize handler
     */
    setupResizeHandler() {
        let resizeTimeout;
        
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                // On mobile, iOS address bar hide/show causes resize
                // Don't auto-scroll on resize to avoid interrupting user
                this.log('Window resized, updating button');
                this.updateScrollButton();
            }, 150);
        }, { passive: true });
    }
    
    /**
     * Scroll to bottom on page load
     */
    scrollToBottomOnLoad() {
        if (!this.chatMessages) return;
        
        const performScroll = () => {
            // Try anchor-based scroll first
            const lastIdAttr = this.chatMessages.getAttribute('data-last-id');
            if (lastIdAttr) {
                const anchor = this.chatMessages.querySelector(`[data-message-id="${lastIdAttr}"]`);
                if (anchor && typeof anchor.scrollIntoView === 'function') {
                    anchor.scrollIntoView({ block: 'end', behavior: 'auto' });
                }
            }
            
            // Ensure absolute bottom
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        };
        
        // Progressive scroll timing for different render phases
        requestAnimationFrame(() => {
            performScroll();
            
            // Additional attempts after content settles
            setTimeout(performScroll, 120);
            setTimeout(performScroll, 400);
            
            this.log('Initial scroll to bottom completed');
        });
    }
    
    /**
     * Scroll to bottom (manual or auto)
     * @param {boolean} smooth - Use smooth scrolling
     */
    scrollToBottom(smooth = false) {
        if (!this.chatMessages) return;
        
        if (smooth && !this.isMobile) {
            this.chatMessages.scrollTo({
                top: this.chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        } else {
            // Instant scroll (better for mobile)
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
        
        this.log('Scrolled to bottom', { smooth });
    }
    
    /**
     * Handle new message arrival
     * Decides whether to auto-scroll based on user state
     */
    handleNewMessage() {
        if (!this.shouldAutoScroll()) {
            this.log('New message: not auto-scrolling (user is reading)');
            this.updateScrollButton(); // Show button instead
            return;
        }
        
        this.log('New message: auto-scrolling');
        this.scrollToBottom(false);
    }
    
    /**
     * Determine if we should auto-scroll
     * @returns {boolean}
     */
    shouldAutoScroll() {
        if (!this.autoScrollEnabled) return false;
        if (!this.chatMessages) return false;
        
        // Don't auto-scroll if user is actively scrolling
        if (this.isUserScrolling) {
            this.log('Not auto-scrolling: user is actively scrolling');
            return false;
        }
        
        // Only auto-scroll if near bottom
        const isNearBottom = this.isNearBottom();
        if (!isNearBottom) {
            this.log('Not auto-scrolling: not near bottom');
            return false;
        }
        
        return true;
    }
    
    /**
     * Check if scrolled near bottom
     * @returns {boolean}
     */
    isNearBottom() {
        if (!this.chatMessages) return false;
        
        const { scrollHeight, scrollTop, clientHeight } = this.chatMessages;
        const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
        
        return distanceFromBottom < this.nearBottomThreshold;
    }
    
    /**
     * Check if scrolled near top
     * @returns {boolean}
     */
    isNearTop() {
        if (!this.chatMessages) return false;
        return this.chatMessages.scrollTop < 40;
    }
    
    /**
     * Update scroll button visibility
     */
    updateScrollButton() {
        if (!this.scrollButton) return;
        
        const isNearBottom = this.isNearBottom();
        
        if (isNearBottom) {
            this.scrollButton.classList.remove('visible');
        } else {
            this.scrollButton.classList.add('visible');
        }
    }
    
    /**
     * Disable auto-scroll (for manual control)
     */
    disableAutoScroll() {
        this.autoScrollEnabled = false;
        this.log('Auto-scroll disabled');
    }
    
    /**
     * Enable auto-scroll
     */
    enableAutoScroll() {
        this.autoScrollEnabled = true;
        this.log('Auto-scroll enabled');
    }
    
    /**
     * Detect mobile device
     * @returns {boolean}
     */
    _detectMobile() {
        return window.innerWidth <= 768 || 
               /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    /**
     * Debug logging
     */
    log(...args) {
        if (this.debug) {
            console.log('[ScrollManager]', ...args);
        }
    }
    
    /**
     * Cleanup
     */
    destroy() {
        clearTimeout(this.scrollTimeout);
        this.log('ScrollManager destroyed');
    }
}

// ============================================
// INITIALIZATION WITH FEATURE FLAG CHECK
// ============================================

(function() {
    // Check if feature is enabled
    if (!window.CHAT_FEATURES || !window.CHAT_FEATURES.newScrollManager) {
        console.log('📜 ScrollManager: Using legacy scroll system (flag disabled)');
        return;
    }
    
    // Wait for DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initScrollManager);
    } else {
        initScrollManager();
    }
    
    function initScrollManager() {
        try {
            console.log('✨ ScrollManager: Initializing new scroll system');
            
            // Create scroll manager instance
            window.chatScroll = new ChatScrollManager({
                enabled: true,
                debug: window.location.search.includes('debug=scroll')
            });
            
            // Signal to other scripts to skip legacy scroll
            window.__SKIP_LEGACY_SCROLL__ = true;
            
            console.log('✅ ScrollManager: Successfully initialized');
            
        } catch (error) {
            console.error('❌ ScrollManager: Initialization failed', error);
            
            // Track error
            if (window.CHAT_METRICS) {
                window.CHAT_METRICS.scrollManagerErrors++;
            }
            
            // Don't block legacy scroll
            window.__SKIP_LEGACY_SCROLL__ = false;
        }
    }
})();

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatScrollManager;
}

