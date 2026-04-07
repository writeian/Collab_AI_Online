    function toggleCommentForm(dialogueNumber) {
        const form = document.getElementById('comment-form-' + dialogueNumber);
        if (!form) return;
        const current = form.style.display || 'none';
        form.style.display = (current === 'none') ? 'block' : 'none';
    }

    // DEPLOYMENT TEST: This should appear in browser console
    console.log('🚨 MOBILE SCROLL FIX v3.0 LOADED - If you see this, our code is deployed!');
    
    // Smart auto-scroll function with mobile optimization
    function smartScrollToBottom(chatMessages) {
        if (!chatMessages) return;
        
        const isMobile = window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        // STRICT "near bottom" threshold for mobile to prevent scroll traps
        const threshold = isMobile ? 20 : 100;  // Much stricter on mobile
        const isNearBottom = (chatMessages.scrollHeight - chatMessages.scrollTop - chatMessages.clientHeight) < threshold;
        
        if (isNearBottom) {
            if (isMobile) {
                // Mobile: Gentle scroll with slight delay to avoid conflicts
                setTimeout(() => {
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }, 50);
            } else {
                // Desktop: Immediate scroll
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
        // If user is scrolled up, don't auto-scroll - let them read in peace
    }

    // Scroll to bottom function
    function scrollToBottom() {
        const chatMessagesEl = document.getElementById('chat-messages');
        if (chatMessagesEl) {
            chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
        }
    }

    // Anchor-aware auto-scroll on load
    function autoScrollOnLoad() {
        const chatMessagesEl = document.getElementById('chat-messages');
        if (!chatMessagesEl) return;

        const lastIdAttr = chatMessagesEl.getAttribute('data-last-id');
        const performScroll = () => {
            // Prefer precise anchor scroll when available
            if (lastIdAttr) {
                const anchor = chatMessagesEl.querySelector(`[data-message-id="${lastIdAttr}"]`);
                if (anchor && typeof anchor.scrollIntoView === 'function') {
                    anchor.scrollIntoView({ block: 'end' });
                }
            }
            // Ensure we land at absolute bottom regardless of content shifts
            chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
        };

        // Run after paint and again after layout settles (desktop/mobile/focus)
        requestAnimationFrame(() => {
            performScroll();
            setTimeout(performScroll, 120);
            setTimeout(performScroll, 400);
            setTimeout(performScroll, 800);
            // IMPORTANT: Do not auto-scroll on resize. On iOS, address bar hide/show
            // triggers resize while the user is scrolling up, which would yank them
            // back to the bottom. We keep resize handlers only for padding updates below.
        });
    }

    // Show/hide scroll to bottom button based on scroll position
    function updateScrollButton() {
        const chatMessagesEl = document.getElementById('chat-messages');
        const scrollButton = document.getElementById('scroll-to-bottom');
        
        if (chatMessagesEl && scrollButton) {
            const isNearBottom = (chatMessagesEl.scrollHeight - chatMessagesEl.scrollTop - chatMessagesEl.clientHeight) < 100;
            
            if (isNearBottom) {
                // Hide button when near bottom
                scrollButton.classList.remove('visible');
            } else {
                // Show button when scrolled up
                scrollButton.classList.add('visible');
            }
        }
    }

    // Touch-Optimized Scrolling and Pull-to-Refresh
    class ChatTouchOptimizer {
        constructor() {
            this.chatMessages = document.getElementById('chat-messages');
            this.isPulling = false;
            this.startY = 0;
            this.currentY = 0;
            this.pullDistance = 0;
            this.isScrolling = false;
            this.scrollVelocity = 0;
            this.lastScrollTop = 0;
            this.lastScrollTime = 0;
            
            this.init();
        }
        
        init() {
            if (!this.chatMessages) return;
            
            // Add pull-to-refresh indicator
            this.createPullIndicator();
            
            // Add touch event listeners
            this.chatMessages.addEventListener('touchstart', this.handleTouchStart.bind(this));
            this.chatMessages.addEventListener('touchmove', this.handleTouchMove.bind(this));
            this.chatMessages.addEventListener('touchend', this.handleTouchEnd.bind(this));
            
            // Add momentum scrolling
            this.addMomentumScrolling();
            
            // Add scroll event listener for velocity calculation
            this.chatMessages.addEventListener('scroll', this.handleScroll.bind(this));
        }
        
        createPullIndicator() {
            // Create pull indicator element
            const indicator = document.createElement('div');
            indicator.className = 'pull-indicator';
            indicator.innerHTML = `
                <div class="pull-content">
                    <i data-lucide="refresh-cw" class="w-5 h-5 animate-spin"></i>
                    <span>Pull to refresh messages</span>
                </div>
            `;
            
            // Insert at the top of chat messages
            this.chatMessages.insertBefore(indicator, this.chatMessages.firstChild);
            this.pullIndicator = indicator;
            
            // Initialize Lucide icons for the new element
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
        
        handleTouchStart(e) {
            this.startY = e.touches[0].clientY;
            this.isPulling = false;
            this.isScrolling = true;
            this.lastScrollTop = this.chatMessages.scrollTop;
            this.lastScrollTime = Date.now();
        }
        
        handleTouchMove(e) {
            this.currentY = e.touches[0].clientY;
            const deltaY = this.currentY - this.startY;
            
            // Check if we're at the top and pulling down
            if (this.chatMessages.scrollTop === 0 && deltaY > 0) {
                this.isPulling = true;
                this.pullDistance = Math.min(deltaY * 0.5, 80); // Limit pull distance
                
                // Show pull indicator
                this.showPullIndicator();
                // e.preventDefault() REMOVED - was blocking native iOS scroll
                // Let native scroll work naturally (matches October 6 fix)
            } else if (this.isPulling) {
                // Continue pull gesture
                this.pullDistance = Math.min(deltaY * 0.5, 80);
                this.updatePullIndicator();
                // e.preventDefault() REMOVED - was blocking native iOS scroll
            }
        }
        
        handleTouchEnd(e) {
            if (this.isPulling && this.pullDistance > 50) {
                // Trigger refresh
                this.refreshMessages();
            }
            
            // Hide pull indicator
            this.hidePullIndicator();
            this.isPulling = false;
            this.isScrolling = false;
        }
        
        handleScroll() {
            if (!this.isScrolling) return;
            
            // Calculate scroll velocity for momentum
            const currentTime = Date.now();
            const timeDelta = currentTime - this.lastScrollTime;
            const scrollDelta = this.chatMessages.scrollTop - this.lastScrollTop;
            
            if (timeDelta > 0) {
                this.scrollVelocity = scrollDelta / timeDelta;
            }
            
            this.lastScrollTop = this.chatMessages.scrollTop;
            this.lastScrollTime = currentTime;
            
            // Update scroll button visibility
            updateScrollButton();
        }
        
        showPullIndicator() {
            if (this.pullIndicator) {
                this.pullIndicator.style.transform = `translateY(${this.pullDistance}px)`;
                this.pullIndicator.style.opacity = '1';
            }
        }
        
        updatePullIndicator() {
            if (this.pullIndicator) {
                this.pullIndicator.style.transform = `translateY(${this.pullDistance}px)`;
            }
        }
        
        hidePullIndicator() {
            if (this.pullIndicator) {
                this.pullIndicator.style.transform = 'translateY(-100%)';
                this.pullIndicator.style.opacity = '0';
            }
        }
        
        refreshMessages() {
            // Show loading state
            if (this.pullIndicator) {
                this.pullIndicator.innerHTML = `
                    <div class="pull-content">
                        <i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i>
                        <span>Refreshing messages...</span>
                    </div>
                `;
                lucide.createIcons();
            }
            
            // Fetch new messages
            fetch(window.location.href)
                .then(response => response.text())
                .then(html => {
                    // Parse the HTML and extract new messages
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newMessages = doc.getElementById('chat-messages');
                    
                    if (newMessages) {
                        // Update messages (this is a simplified version)
                        // In a real implementation, you'd want to compare message IDs
                        window.location.reload();
                    }
                })
                .catch(error => {
                    console.error('Failed to refresh messages:', error);
                    // Restore original pull indicator
                    this.pullIndicator.innerHTML = `
                        <div class="pull-content">
                            <i data-lucide="refresh-cw" class="w-5 h-5 animate-spin"></i>
                            <span>Pull to refresh messages</span>
                        </div>
                    `;
                    lucide.createIcons();
                });
        }
        
        addMomentumScrolling() {
            // CSS now applied via stylesheet (safer than cssText manipulation)
            // See template: #chat-messages gets these properties from CSS
            // No inline style manipulation to avoid destroying other styles
        }
    }

    // Initialize touch optimization when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        let queueStatusIntervalId = null;
        /** 1 after SSE ``start`` so /queue-status excludes our job from "others". */
        let queuePollSubtractSelf = 0;
        /** Hide queue only after N consecutive polls with nothing to show (brief blips / latency). */
        let queueNoticeMissStreak = 0;
        const QUEUE_NOTICE_MISS_BEFORE_HIDE = 3;
        let activeEventSource = null;
        let activeStreamFetchController = null;
        /** User Message.id we are waiting to pair with an assistant (token stream). */
        let streamingForUserMessageId = null;

        function clearStreamingTarget() {
            streamingForUserMessageId = null;
        }

        function setStreamingTarget(id) {
            if (id == null || id === '') {
                streamingForUserMessageId = null;
                return;
            }
            const n = Number(id);
            streamingForUserMessageId = isNaN(n) ? null : n;
        }

        function releaseActiveEventSource(es) {
            if (activeEventSource === es) activeEventSource = null;
        }

        function releaseActiveFetchController(controller) {
            if (activeStreamFetchController === controller) activeStreamFetchController = null;
        }

        function closeActiveEventSource(reason) {
            if (!activeEventSource) return;
            try {
                activeEventSource.close();
            } catch (_) {}
            if (aiStreamDebugVerbose()) {
                aiStreamLogVerbose('closed existing EventSource', reason || 'cleanup');
            }
            activeEventSource = null;
        }

        function abortActiveFetchStream(reason) {
            if (!activeStreamFetchController) return;
            try {
                activeStreamFetchController.abort();
            } catch (_) {}
            if (aiStreamDebugVerbose()) {
                aiStreamLogVerbose('aborted existing fetch stream', reason || 'cleanup');
            }
            activeStreamFetchController = null;
        }

        function logTransportProtocolHint() {
            try {
                const nav = performance.getEntriesByType('navigation');
                const proto = nav && nav[0] ? nav[0].nextHopProtocol : '';
                if (proto && !/^h2|h3|http\/2$/i.test(proto)) {
                    console.warn(
                        '[AI stream] Connection protocol appears to be',
                        proto,
                        '- HTTP/2 or HTTP/3 is recommended for many concurrent browser streams.'
                    );
                }
            } catch (_) {}
        }
        logTransportProtocolHint();

        window.addEventListener('beforeunload', function() {
            closeActiveEventSource('page-unload');
            abortActiveFetchStream('page-unload');
            clearStreamingTarget();
        });

        // Delegate clicks for Add Comment toggles (avoids inline handlers in HTML lints)
        document.body.addEventListener('click', function(ev) {
            const btn = ev.target.closest('[data-toggle-comment]');
            if (btn) {
                const d = btn.getAttribute('data-dialogue');
                if (d) { try { toggleCommentForm(d); } catch(_){} }
            }
        });
        // Format all message timestamps to the viewer's local timezone
        function formatAllMessageTimes(root) {
            try {
                const scope = root || document;
                const nodes = scope.querySelectorAll('time.msg-time');
                const formatter = new Intl.DateTimeFormat([], { hour: '2-digit', minute: '2-digit' });
                nodes.forEach(node => {
                    const ts = parseInt(node.getAttribute('data-ts') || '0', 10);
                    if (!ts) return;
                    const d = new Date(ts * 1000);
                    node.textContent = formatter.format(d);
                    node.setAttribute('title', d.toLocaleString());
                });
            } catch (e) { /* no-op */ }
        }
        formatAllMessageTimes();
        
        function getUserInitials(displayName) {
            if (!displayName) return '';
            const parts = displayName.trim().split(/\s+/);
            if (parts.length >= 2) {
                return (parts[0][0] + parts[1][0]).toUpperCase();
            }
            return displayName.substring(0, 2).toUpperCase();
        }

        function getUserAvatarHtml(user) {
            if (!user) return '';
            const id = typeof user.id === 'number' ? user.id : 0;
            const colorClass = 'avatar-color-' + ((id % 6) + 1);
            const initials = getUserInitials(user.display_name || '');
            return `
                <div class="user-avatar ${colorClass}">
                    <span class="avatar-text">${initials}</span>
                </div>
            `;
        }

        // Initialize touch-optimized scrolling (DISABLED ON MOBILE)
        // On iOS/Android, the pull-to-refresh → window.location.reload() causes scroll traps
        // Mobile browsers have native pull-to-refresh anyway
        const isMobileDevice = /iP(ad|hone|od)|Android/i.test(navigator.userAgent);
        if (!isMobileDevice) {
            new ChatTouchOptimizer();
            console.log('✅ ChatTouchOptimizer enabled (desktop)');
        } else {
            console.log('⏭️  ChatTouchOptimizer disabled (mobile - prevents reload scroll trap)');
        }
        
        // Initialize existing scroll button functionality
        const chatMessagesElement = document.getElementById('chat-messages');
        if (chatMessagesElement) {
            chatMessagesElement.addEventListener('scroll', updateScrollButton);
            updateScrollButton(); // Initial check
            
            // Auto-scroll to bottom when page loads
            autoScrollOnLoad();
        }

        // Ensure latest message isn't hidden by the translucent input bar
        const chatMessagesRef = document.getElementById('chat-messages');
        const inputBar = document.querySelector('.chat-input-container');
        // Bottom spacer buffers
        function getNonFocusBufferPx() { return (window.innerWidth <= 768) ? 10 : 12; }

        function isNearBottom(el) {
            if (!el) return false;
            return (el.scrollHeight - el.scrollTop - el.clientHeight) < 100;
        }
        function isNearTop(el) {
            if (!el) return false;
            return el.scrollTop < 40; // small threshold
        }

        function applyBottomPadding(nudgeScroll) {
            if (!chatMessagesRef || !inputBar) return;
            const wasNearBottom = isNearBottom(chatMessagesRef);
            const inputHeight = inputBar.offsetHeight || 0;
            const buffer = getNonFocusBufferPx();
            const safeArea = 16; /* env(safe-area-inset-bottom) fallback */
            const spacerHeight = Math.max(88, inputHeight + buffer + safeArea);
            // Spacer removed - if (spacer) spacer.style.height = spacerHeight + 'px';
            // Remove direct padding-bottom manipulations to avoid conflicts
            chatMessagesRef.style.removeProperty('padding-bottom');
            chatMessagesRef.style.setProperty('--chat-input-h', spacerHeight + 'px');
            const isMobileViewport = window.innerWidth <= 768 || /iP(ad|hone|od)/i.test(navigator.userAgent);
            if (!isMobileViewport && nudgeScroll && wasNearBottom) {
                chatMessagesRef.scrollTop = chatMessagesRef.scrollHeight - chatMessagesRef.clientHeight;
            }
        }

        // Initial application after first paint
        setTimeout(() => applyBottomPadding(true), 30);
        // Re-apply after resize/input changes as needed
        window.addEventListener('resize', () => applyBottomPadding(false));
        // Recompute when focus mode toggles (padding rule removed from CSS)
        document.addEventListener('click', (e) => {
            if (e.target && (e.target.id === 'focus-mode-toggle' || e.target.closest('#focus-mode-toggle'))) {
                setTimeout(() => applyBottomPadding(true), 80);
            }
        });

        // React to input bar size changes (responsive/font changes)
        if (window.ResizeObserver && inputBar) {
            const ro = new ResizeObserver(() => applyBottomPadding(true));
            ro.observe(inputBar);
        }
        
        // Chat Sidebar Toggle functionality (mobile only)
        const chatSidebarToggle = document.getElementById('chat-sidebar-toggle');
        const chatSidebar = document.querySelector('.chat-sidebar');
        
        if (chatSidebarToggle && chatSidebar) {
            chatSidebarToggle.addEventListener('click', function() {
                chatSidebar.classList.toggle('open');
                
                // Update the icon
                const icon = chatSidebarToggle.querySelector('i');
                if (icon) {
                    if (chatSidebar.classList.contains('open')) {
                        icon.setAttribute('data-lucide', 'x');
                    } else {
                        icon.setAttribute('data-lucide', 'panel-left');
                    }
                    
                    // Reinitialize Lucide icons
                    lucide.createIcons();
                }
            });
            
            // Close sidebar when clicking outside (mobile only)
            document.addEventListener('click', function(e) {
                if (window.innerWidth <= 768 && 
                    !chatSidebar.contains(e.target) && 
                    !chatSidebarToggle.contains(e.target) &&
                    chatSidebar.classList.contains('open')) {
                    chatSidebar.classList.remove('open');
                    
                    // Update the icon
                    const icon = chatSidebarToggle.querySelector('i');
                    if (icon) {
                        icon.setAttribute('data-lucide', 'panel-left');
                        lucide.createIcons();
                    }
                }
            });
        }

        // Focus mode toggle with persistence
        const focusToggle = document.getElementById('focus-mode-toggle');
        const FOCUS_KEY = 'chat_focus_mode';
        function applyFocusMode(enabled) {
            if (enabled) {
                document.body.classList.add('focus-mode');
                if (focusToggle) focusToggle.textContent = 'Exit Focus';
            } else {
                document.body.classList.remove('focus-mode');
                if (focusToggle) focusToggle.textContent = 'Focus';
            }
        }
        function enforceFocusModeLayout() {
            /* Focus mode: ONLY sidebar collapses (CSS). Composer stays sticky. */
            applyBottomPadding(true);
        }
        try {
            const saved = localStorage.getItem(FOCUS_KEY);
            if (saved === 'true') {
                applyFocusMode(true);
                setTimeout(enforceFocusModeLayout, 50);
            }
        } catch (e) {}
        if (focusToggle) {
            focusToggle.addEventListener('click', function() {
                const enabled = !document.body.classList.contains('focus-mode');
                applyFocusMode(enabled);
                try { localStorage.setItem(FOCUS_KEY, enabled.toString()); } catch (e) {}
                // Re-apply padding in case layout heights changed with focus toggle
                setTimeout(() => { applyBottomPadding(true); enforceFocusModeLayout(); }, 50);
            });
        }
        // Keep layout correct on resize while in focus mode
        window.addEventListener('resize', () => { if (document.body.classList.contains('focus-mode')) enforceFocusModeLayout(); });
        // iOS VisualViewport-aware adjustments (single registration)
        if (!window.__chat_vv_bound && window.visualViewport) {
            const vvHandler = () => { try { applyBottomPadding(false); enforceFocusModeLayout(); } catch(e){} };
            window.visualViewport.addEventListener('resize', vvHandler);
            window.visualViewport.addEventListener('scroll', vvHandler);
            window.__chat_vv_bound = true;
        }
        // Input focus/blur adjustments for mobile keyboards (single registration)
        if (!window.__chat_input_bound) {
            const inputEl = document.getElementById('message-input');
            if (inputEl) {
                // Auto-grow textarea on input (desktop). Shift+Enter newline, Enter submits
                inputEl.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        const form = document.getElementById('message-form');
                        if (form && typeof form.requestSubmit === 'function') {
                            form.requestSubmit(); // triggers submit handler (proxy + clear + native submit)
                        } else if (form) {
                            const notCanceled = form.dispatchEvent(
                                new Event('submit', { cancelable: true, bubbles: true })
                            );
                            if (notCanceled) {
                                form.submit();
                            }
                        }
                    }
                });
                const autogrow = () => {
                    try {
                        // Cap differs by viewport size; use computed CSS max-height
                        inputEl.style.height = 'auto';
                        const styles = getComputedStyle(inputEl);
                        const maxH = parseFloat(styles.maxHeight) || (window.innerWidth <= 768 ? window.innerHeight * 0.35 : window.innerHeight * 0.45);
                        const newH = Math.min(inputEl.scrollHeight + 2, maxH);
                        inputEl.style.height = newH + 'px';
                        setTimeout(() => { applyBottomPadding(true); }, 10);
                    } catch (e) {}
                };
                inputEl.addEventListener('input', autogrow);
                // Run once on load to fit any prefilled text
                setTimeout(autogrow, 0);
                inputEl.addEventListener('focus', () => { setTimeout(() => { applyBottomPadding(true); enforceFocusModeLayout(); }, 50); });
                inputEl.addEventListener('blur', () => { setTimeout(() => { applyBottomPadding(true); enforceFocusModeLayout(); }, 50); });
            }
            window.__chat_input_bound = true;
        }
        // iOS VisualViewport-aware adjustments (single registration)
        if (!window.__chat_vv_bound && window.visualViewport) {
            const vvHandler = () => { try { applyBottomPadding(false); enforceFocusModeLayout(); } catch(e){} };
            window.visualViewport.addEventListener('resize', vvHandler);
            window.visualViewport.addEventListener('scroll', vvHandler);
            window.__chat_vv_bound = true;
        }
        // Input focus/blur adjustments for mobile keyboards (single registration)
        if (!window.__chat_input_bound) {
            const inputEl = document.getElementById('message-input');
            if (inputEl) {
                inputEl.addEventListener('focus', () => { setTimeout(() => { applyBottomPadding(true); enforceFocusModeLayout(); }, 50); });
                inputEl.addEventListener('blur', () => { setTimeout(() => { applyBottomPadding(true); enforceFocusModeLayout(); }, 50); });
            }
            window.__chat_input_bound = true;
        }
        // (deduped above)
        // Input focus/blur adjustments for mobile keyboards
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.addEventListener('focus', () => { setTimeout(() => { applyBottomPadding(true); enforceFocusModeLayout(); }, 50); });
            messageInput.addEventListener('blur', () => { setTimeout(() => { applyBottomPadding(true); enforceFocusModeLayout(); }, 50); });
        }
        
        // AI Response Toggle functionality
        const aiToggle = document.getElementById('ai-response-toggle');
        const toggleLabel = document.querySelector('label[for="ai-response-toggle"]');
        
        if (aiToggle && toggleLabel) {
            // Get chat ID for localStorage key
            const chatId = window.location.pathname.split('/').pop();
            const storageKey = `ai_response_${chatId}`;
            
            // Load saved toggle state from localStorage
            const savedState = localStorage.getItem(storageKey);
            if (savedState !== null) {
                aiToggle.checked = savedState === 'true';
            }
            // If no saved state, default to checked (AI responses enabled)
            
            // Update label text based on toggle state
            function updateToggleLabel() {
                if (aiToggle.checked) {
                    toggleLabel.innerHTML = '🤖 AI Response <span class="text-xs text-muted-foreground">(Uncheck to mute AI)</span>';
                } else {
                    toggleLabel.innerHTML = '🤖 AI Response <span class="text-xs text-muted-foreground">(Check to enable AI)</span>';
                }
            }
            
            // Save toggle state to localStorage when it changes
            function saveToggleState() {
                localStorage.setItem(storageKey, aiToggle.checked.toString());
                updateToggleLabel();
            }
            
            // Initialize label
            updateToggleLabel();
            
            // Update label and save state when toggle changes
            aiToggle.addEventListener('change', saveToggleState);
        }
        
        // Try multiple selectors to find the chat messages container
        let chatMessagesEl = document.querySelector('.flex-1.overflow-y-auto.p-4.space-y-4');
        if (!chatMessagesEl) {
            chatMessagesEl = document.querySelector('.flex-1.overflow-y-auto');
        }
        if (!chatMessagesEl) {
            // Fallback: look for any scrollable container with messages
            chatMessagesEl = document.querySelector('[class*="overflow-y-auto"]');
        }
        
        console.log('Chat messages container found:', chatMessagesEl);
        console.log('📱 CONTAINER DIMENSIONS: scrollHeight=' + chatMessagesEl.scrollHeight + ', clientHeight=' + chatMessagesEl.clientHeight + ', scrollTop=' + chatMessagesEl.scrollTop);
        console.log('📱 VIEWPORT: window.innerHeight=' + window.innerHeight + ', window.innerWidth=' + window.innerWidth);
        
        if (chatMessagesEl) {
            console.log('Scrolling to bottom...');
            console.log('Initial scrollTop:', chatMessagesEl.scrollTop);
            console.log('ScrollHeight:', chatMessagesEl.scrollHeight);
            
            // Mobile-friendly auto-scroll on page load
            const isMobile = window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            console.log('📱 MOBILE DETECTION: isMobile=' + isMobile + ', width=' + window.innerWidth + ', userAgent=' + navigator.userAgent.substring(0, 50));
            
            if (isMobile) {
                // Mobile: Single, gentle scroll after content loads
                console.log('Mobile device detected - using gentle scroll');
                setTimeout(() => {
                    chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
                    console.log('Mobile scroll applied - scrollTop:', chatMessagesEl.scrollTop);
                }, 300);  // Single scroll after 300ms
            } else {
                // Desktop: More aggressive scrolling for reliable positioning
                console.log('Desktop device - using standard scroll');
                chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
                console.log('After scroll - scrollTop:', chatMessagesEl.scrollTop);
                
                setTimeout(() => {
                    chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
                    console.log('After 100ms scroll - scrollTop:', chatMessagesEl.scrollTop);
                }, 100);
                
                setTimeout(() => {
                    chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
                    console.log('After 500ms scroll - scrollTop:', chatMessagesEl.scrollTop);
                }, 500);
            }
            
            // Add scroll event listener with mobile user scroll tracking
            chatMessagesEl.addEventListener('scroll', function(e) {
                // Track user scroll activity for mobile
                const isMobile = window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
                if (isMobile) {
                    window.lastUserScrollTime = Date.now();
                }
                markUserActivity();
                
                // Update scroll button visibility
                updateScrollButton();
            });
            
            // Initial check for scroll button visibility
            updateScrollButton();
        } else {
            console.error('Could not find chat messages container');
        }
        
        function escapeHtml(s) {
            if (s == null || s === '') return '';
            const d = document.createElement('div');
            d.textContent = s;
            return d.innerHTML;
        }

        function renderReplyContext(rc) {
            if (!rc || !rc.preview) return '';
            const tintCls = rc.avatar_slot
                ? ('reply-tint-' + rc.avatar_slot)
                : 'reply-tint-assistant';
            return (
                '<div class="message-reply-context ' + tintCls + '" role="note">' +
                '<span class="message-reply-icon" aria-hidden="true">↳</span>' +
                '<div class="message-reply-text">' +
                '<span class="message-reply-author">' + escapeHtml(rc.author_label) + '</span>' +
                '<span class="message-reply-snippet">' + escapeHtml(rc.preview) + '</span>' +
                '</div></div>'
            );
        }

        /** Match server-rendered chat controls (templates/chat/view.html). */
        function buildAppendedMessageActionsHtml(dialogueNum, messageId) {
            const cc = document.querySelector('.chat-container');
            if (!cc || cc.dataset.showMessageActions !== '1') {
                return '';
            }
            const d = String(dialogueNum);
            const mid = String(messageId);
            return (
                '<button type="button" class="text-xs text-muted-foreground hover:text-foreground ml-2" data-toggle-comment data-dialogue="' +
                d +
                '">💬 Add Comment</button>' +
                '<button type="button" class="text-xs ml-2 pin-toggle" data-pin-message="' +
                mid +
                '" data-pinned="false">Pin</button>'
            );
        }

        function buildAppendedCommentFormHtml(dialogueNum) {
            const cc = document.querySelector('.chat-container');
            if (!cc || cc.dataset.showMessageActions !== '1') {
                return '';
            }
            const chatId = String(cc.dataset.chatId || '');
            const csrfInput = document.querySelector('#message-form input[name="csrf_token"]');
            const csrf = csrfInput ? csrfInput.value : '';
            const d = String(dialogueNum);
            const csrfField = csrf
                ? '<input type="hidden" name="csrf_token" value="' + escapeHtml(csrf) + '">'
                : '';
            return (
                '<form method="POST" action="/chat/' +
                escapeHtml(chatId) +
                '/comment" class="comment-form" id="comment-form-' +
                d +
                '" style="display: none;">' +
                csrfField +
                '<input type="hidden" name="dialogue_number" value="' +
                d +
                '">' +
                '<textarea name="comment_content" required class="comment-textarea w-full" rows="2" placeholder="Add your comment here..."></textarea>' +
                '<div class="flex gap-1 mt-1">' +
                '<button type="submit" class="px-2 py-1 text-xs bg-primary text-primary-foreground rounded hover:bg-primary/90">Add</button>' +
                '<button type="button" class="px-2 py-1 text-xs bg-muted text-muted-foreground rounded hover:bg-muted/80" data-toggle-comment data-dialogue="' +
                d +
                '">Cancel</button>' +
                '</div></form>'
            );
        }

        function appendMessageEntries(list) {
            if (!list || !list.length) return;
            const container = document.getElementById('chat-messages');
            if (!container) return;
            const wasNearBottom = isNearBottom(container);
            const wasNearTop = isNearTop(container);
            let dialogueCounter = container.querySelectorAll('[data-message-id]').length;
            list.forEach(msg => {
                if (msg.role === 'assistant') {
                    const pid =
                        msg.parent_message_id != null && msg.parent_message_id !== ''
                            ? Number(msg.parent_message_id)
                            : null;
                    const waiting = streamingForUserMessageId;
                    const hasLocalStream = !!(activeEventSource || activeStreamFetchController);
                    const thisReplyIsOurs =
                        waiting != null && pid != null && !isNaN(pid) && pid === waiting;
                    if (!hasLocalStream || thisReplyIsOurs) {
                        removeStreamingAssistantBubble();
                    }
                }
                const mid = String(msg.id);
                if (container.querySelector(`[data-message-id="${mid}"]`)) {
                    return;
                }
                dialogueCounter += 1;
                const dialogueNum = dialogueCounter;
                const actionsHtml = buildAppendedMessageActionsHtml(dialogueNum, msg.id);
                const commentFormHtml = buildAppendedCommentFormHtml(dialogueNum);
                const wrapper = document.createElement('div');
                wrapper.className = `flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`;
                wrapper.setAttribute('data-message-id', mid);
                wrapper.id = 'message-' + mid;
                const truncAttr = msg.role === 'assistant' ? ` data-truncated="${msg.is_truncated ? 'true' : 'false'}"` : '';
                const replyBlock = msg.role === 'assistant' ? renderReplyContext(msg.reply_context) : '';
                const tsSec = Math.floor(new Date(msg.timestamp).getTime() / 1000);
                wrapper.innerHTML = `
                      <div class="message-bubble ${msg.role === 'user' ? 'user' : 'assistant'}"${truncAttr}>
                        ${msg.role === 'assistant' ? `
                        <div class="flex items-start gap-3">
                          <div class="ai-avatar">AI</div>
                          <div class="flex-1">${replyBlock}<div class="message-content">${msg.rendered_html || `<p>${escapeHtml(msg.content)}</p>`}
                          <p class="message-timestamp"><time class=\"msg-time\" data-ts=\"${tsSec}\"></time>${actionsHtml}</p>
                          </div></div>
                        </div>${commentFormHtml}` : `
                        <div class="flex items-start gap-3">
                          <div class="flex-1"><div class="message-content text-right">${msg.rendered_html || `<p>${escapeHtml(msg.content)}</p>`}
                          <p class="message-timestamp"><time class=\"msg-time\" data-ts=\"${tsSec}\"></time>${actionsHtml}</p>
                          </div></div>
                          ${getUserAvatarHtml(msg.user)}
                        </div>${commentFormHtml}`}
                      </div>`;
                container.appendChild(wrapper);
            });
            if (typeof lucide !== 'undefined') { try { lucide.createIcons(); } catch (e) {} }
            try { formatAllMessageTimes(container); } catch (e) {}
            try { applyBottomPadding(false); } catch (e) {}
            const isMobile = window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            if (wasNearBottom && !wasNearTop) {
                if (isMobile) {
                    updateScrollButton();
                } else {
                    container.scrollTop = container.scrollHeight;
                }
            } else {
                updateScrollButton();
            }
        }

        async function fetchAndAppendMessagesAfter(afterId) {
            let chatId = window.location.pathname.match(/\/chat\/(\d+)/)?.[1];
            if (!chatId) {
                const chatContainer = document.querySelector('.chat-container');
                chatId = chatContainer?.dataset.chatId;
            }
            if (!chatId) return null;
            const resp = await fetch(`/chat/${chatId}/messages?after_id=${afterId}`);
            const data = await resp.json();
            if (!data.success) return null;
            const list = data.messages || [];
            if (list.length) {
                appendMessageEntries(list);
            }
            if (data.last_id != null && data.last_id !== '') {
                const nid = parseInt(String(data.last_id), 10) || 0;
                const cur = getLastMessageId();
                if (nid > cur) {
                    setLastMessageId(nid);
                }
            }
            return data;
        }

        function removeStreamingAssistantBubble() {
            const el = document.getElementById('streaming-assistant-bubble');
            if (!el) {
                clearStreamingTarget();
                return;
            }
            el.remove();
            clearStreamingTarget();
            try {
                applyBottomPadding(true);
            } catch (e) { /* ignore */ }
            try {
                updateScrollButton();
            } catch (e) { /* ignore */ }
        }

        function ensureStreamingAssistantBubble() {
            removeStreamingAssistantBubble();
            const container = document.getElementById('chat-messages');
            if (!container) return null;
            const wrap = document.createElement('div');
            wrap.id = 'streaming-assistant-bubble';
            wrap.className = 'flex justify-start';
            wrap.innerHTML = `
                <div class="message-bubble assistant" data-streaming="true">
                  <div class="flex items-start gap-3">
                    <div class="ai-avatar">AI</div>
                    <div class="flex-1">
                      <div class="message-content streaming-assistant-chunk"><p></p></div>
                      <p class="message-timestamp text-xs text-muted-foreground streaming-writing-label">Writing…</p>
                    </div>
                  </div>
                </div>`;
            container.appendChild(wrap);
            try { applyBottomPadding(false); } catch (e) {}
            const msgEl = document.getElementById('chat-messages');
            if (msgEl) {
                smartScrollToBottom(msgEl);
            }
            return wrap;
        }

        /** Re-append the streaming row so it sits after the latest user message (fetch adds user after bubble otherwise). */
        function moveStreamingBubbleBelowMessages(streamWrap) {
            if (!streamWrap || !streamWrap.id) return;
            const container = document.getElementById('chat-messages');
            if (!container || !document.getElementById('streaming-assistant-bubble')) return;
            container.appendChild(streamWrap);
            try { applyBottomPadding(false); } catch (e) {}
            try { smartScrollToBottom(container); } catch (e) {}
        }

        function hideQueueNotice() {
            const el = document.getElementById('ai-queue-notice');
            if (el) el.classList.add('hidden');
        }

        function applyQueueNoticeFromPayload(j) {
            const el = document.getElementById('ai-queue-notice');
            if (!el || !j || !j.success) return;
            if (!j.show_notice) {
                hideQueueNotice();
                return;
            }
            const p = el.querySelector('.ai-queue-bubble-line-primary');
            const d = el.querySelector('.ai-queue-bubble-line-detail');
            if (p) p.textContent = j.primary_line || (j.queue_position ? ('You are #' + j.queue_position + ' in the queue.') : '');
            if (d) d.textContent = j.detail_line || j.message || '';
            el.classList.remove('hidden');
        }

        function stopQueueStatusPolling() {
            if (queueStatusIntervalId != null) {
                clearInterval(queueStatusIntervalId);
                queueStatusIntervalId = null;
            }
        }

        function isWaitingForAssistantAtBottom() {
            if (document.getElementById('streaming-assistant-bubble')) {
                return true;
            }
            const container = document.getElementById('chat-messages');
            if (!container) return false;
            const rows = container.querySelectorAll('[data-message-id]');
            if (!rows.length) return false;
            const last = rows[rows.length - 1];
            return !!last.querySelector('.message-bubble.user');
        }

        function fetchQueueStatusJson() {
            let chatId = window.location.pathname.match(/\/chat\/(\d+)/)?.[1];
            if (!chatId) {
                const chatContainer = document.querySelector('.chat-container');
                chatId = chatContainer?.dataset.chatId;
            }
            if (!chatId) return Promise.resolve(null);
            const q = encodeURIComponent(String(queuePollSubtractSelf));
            return fetch('/chat/' + chatId + '/queue-status?subtract_self=' + q).then(
                function(r) { return r.json(); }
            );
        }

        async function queueStatusPollTick() {
            if (!isWaitingForAssistantAtBottom()) {
                stopQueueStatusPolling();
                hideQueueNotice();
                queueNoticeMissStreak = 0;
                return;
            }
            try {
                const j = await fetchQueueStatusJson();
                if (j && j.success && j.show_notice) {
                    queueNoticeMissStreak = 0;
                    applyQueueNoticeFromPayload(j);
                } else {
                    queueNoticeMissStreak += 1;
                    if (queueNoticeMissStreak >= QUEUE_NOTICE_MISS_BEFORE_HIDE) {
                        hideQueueNotice();
                    }
                }
            } catch (_) { /* ignore */ }
        }

        function startQueueStatusPolling() {
            stopQueueStatusPolling();
            queueNoticeMissStreak = 0;
            queueStatusPollTick();
            queueStatusIntervalId = setInterval(queueStatusPollTick, 2500);
        }

        /** Token streaming uses the Anthropic streaming API on the server; the browser must use fetch+SSE or EventSource (not a plain form POST). */
        function aiStreamDebugVerbose() {
            try {
                return (
                    localStorage.getItem('collab_ai_stream_debug') === '1' ||
                    new URLSearchParams(window.location.search).get('debug_stream') === '1'
                );
            } catch (_) {
                return false;
            }
        }

        function aiStreamLogVerbose() {
            if (!aiStreamDebugVerbose()) return;
            var args = Array.prototype.slice.call(arguments);
            args.unshift('[AI stream debug]');
            console.info.apply(console, args);
        }

        // Submit: clear textarea immediately via hidden proxy field (native submit reads DOM);
        // optional queue notice before AI round-trip.
        const form = document.getElementById('message-form');
        if (form) {
            form.addEventListener('submit', async function(e) {
                const btn = document.getElementById('send-button');
                const input = document.getElementById('message-input');
                const aiToggle = document.getElementById('ai-response-toggle');
                markUserActivity();

                const messageContent = input ? input.value.trim() : '';

                if (!messageContent) {
                    e.preventDefault();
                    console.log('Empty message prevented');
                    return false;
                }

                e.preventDefault();

                if (activeEventSource || activeStreamFetchController) {
                    console.warn('[AI stream] A reply is already streaming; waiting for it to finish.');
                    return false;
                }

                const aiEnabled = aiToggle ? aiToggle.checked : true;
                const chatContainer = document.querySelector('.chat-container');
                const chatId = chatContainer ? chatContainer.dataset.chatId : null;
                const useAiAsync = !!(
                    chatContainer &&
                    chatContainer.dataset.aiAsync === '1' &&
                    aiEnabled &&
                    chatId
                );

                if (aiEnabled && chatId && !useAiAsync) {
                    console.warn(
                        '[AI stream] Streaming path disabled: chat container is missing data-ai-async="1". ' +
                            'Server must set ai_async_available (e.g. FLASK_ENV=development, or REDIS_URL+worker, or AI_STREAM_IN_REQUEST=1). ' +
                            'Without it, the form does a full submit and the reply appears only after the full response.'
                    );
                }

                function resetSendUi() {
                    if (btn) {
                        btn.classList.remove('sending-state');
                        const sendIcon = btn.querySelector('#send-icon');
                        const loadingIcon = btn.querySelector('#loading-icon');
                        if (sendIcon) sendIcon.style.display = '';
                        if (loadingIcon) loadingIcon.classList.add('hidden');
                    }
                    if (input && !input.getAttribute('name')) {
                        input.setAttribute('name', 'content');
                    }
                }

                let proxy = form.querySelector('input[name="content"][data-send-proxy="1"]');
                if (!proxy) {
                    proxy = document.createElement('input');
                    proxy.type = 'hidden';
                    proxy.name = 'content';
                    proxy.setAttribute('data-send-proxy', '1');
                    form.appendChild(proxy);
                }
                proxy.value = messageContent;
                if (input) {
                    input.value = '';
                    input.style.height = 'auto';
                    try {
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    } catch (_) {}
                    input.removeAttribute('name');
                }

                if (btn) {
                    btn.classList.add('sending-state');
                    const sendIcon = btn.querySelector('#send-icon');
                    const loadingIcon = btn.querySelector('#loading-icon');
                    if (sendIcon) sendIcon.style.display = 'none';
                    if (loadingIcon) loadingIcon.classList.remove('hidden');
                }

                if (aiEnabled && chatId) {
                    try {
                        const r = await fetch('/chat/' + chatId + '/queue-status');
                        const j = await r.json();
                        if (j.success) {
                            applyQueueNoticeFromPayload(j);
                        }
                    } catch (_) { /* still send */ }
                }

                if (useAiAsync) {
                    queuePollSubtractSelf = 0;
                    console.info('[AI stream] Using fetch + X-AI-Async (token streaming path). Verbose:', aiStreamDebugVerbose(), '(add ?debug_stream=1 or localStorage collab_ai_stream_debug=1)');
                    let queueNoticeDismissedForThisStream = false;
                    function dismissQueueNoticeOnceStreamBegan() {
                        if (queueNoticeDismissedForThisStream) {
                            return;
                        }
                        queueNoticeDismissedForThisStream = true;
                        stopQueueStatusPolling();
                        hideQueueNotice();
                    }
                    let fetchController = null;
                    try {
                        const csrf =
                            form.querySelector('input[name="csrf_token"]')?.value || '';
                        fetchController = new AbortController();
                        activeStreamFetchController = fetchController;
                        const res = await fetch(form.action, {
                            method: 'POST',
                            body: new FormData(form),
                            credentials: 'same-origin',
                            signal: fetchController.signal,
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                                'X-AI-Async': '1',
                                Accept: 'application/json, text/event-stream',
                                'X-CSRFToken': csrf,
                            },
                        });
                        const ct = (res.headers.get('content-type') || '').toLowerCase();
                        console.info('[AI stream] POST reply', {
                            status: res.status,
                            ok: res.ok,
                            contentType: ct || '(none)',
                            redirected: res.redirected,
                        });

                        function applySseData(d, chunkEl, streamUserMsgIdRef, dismissQueue) {
                            if (d.type === 'start' && d.user_message_id) {
                                streamUserMsgIdRef.id = d.user_message_id;
                                setStreamingTarget(d.user_message_id);
                                queuePollSubtractSelf = 1;
                                aiStreamLogVerbose('event', d.type, { user_message_id: d.user_message_id });
                                if (typeof dismissQueue === 'function') {
                                    dismissQueue();
                                }
                            }
                            if (
                                d.type === 'chunk' &&
                                typeof d.text === 'string' &&
                                chunkEl
                            ) {
                                if (typeof dismissQueue === 'function') {
                                    dismissQueue();
                                }
                                const p = chunkEl.querySelector('p');
                                if (p) {
                                    p.textContent = (p.textContent || '') + d.text;
                                }
                                const wrapFlex = chunkEl.parentElement;
                                const lbl = wrapFlex && wrapFlex.querySelector('.streaming-writing-label');
                                if (lbl) {
                                    lbl.classList.add('hidden');
                                }
                                const cm = document.getElementById('chat-messages');
                                if (cm) {
                                    smartScrollToBottom(cm);
                                }
                                return 'chunk';
                            }
                            if (d.type === 'error') {
                                aiStreamLogVerbose('event', d.type, d);
                                return 'error';
                            }
                            if (d.type === 'done') {
                                aiStreamLogVerbose('event', d.type, {
                                    message_id: d.message_id,
                                    is_truncated: d.is_truncated,
                                });
                                if (typeof dismissQueue === 'function') {
                                    dismissQueue();
                                }
                                return 'done';
                            }
                            if (d.type === 'connected') {
                                aiStreamLogVerbose('event', d.type);
                                return null;
                            }
                            aiStreamLogVerbose('unhandled SSE payload', d);
                            return null;
                        }

                        async function consumeSseFromFetch(fetchRes, fallbackUserMsgId) {
                            console.info('[AI stream] Consuming in-request SSE (same POST body).');
                            const priorLastId = getLastMessageId();
                            // Must not await this before reading the response body: the server
                            // holds the same connection for in-request SSE; if we delay
                            // getReader(), the socket buffer fills, Flask blocks on write, and
                            // chunks arrive all at once after this fetch completes.
                            const appendPromise = fetchAndAppendMessagesAfter(priorLastId).catch(
                                function() {
                                    return null;
                                }
                            );
                            const streamWrap = ensureStreamingAssistantBubble();
                            appendPromise.finally(function() {
                                moveStreamingBubbleBelowMessages(streamWrap);
                                if (isWaitingForAssistantAtBottom()) {
                                    startQueueStatusPolling();
                                }
                            });
                            const chunkEl = streamWrap
                                ? streamWrap.querySelector('.streaming-assistant-chunk')
                                : null;
                            const streamUserMsgIdRef = { id: fallbackUserMsgId || null };
                            if (streamUserMsgIdRef.id) {
                                setStreamingTarget(streamUserMsgIdRef.id);
                            }
                            const reader = fetchRes.body.getReader();
                            const dec = new TextDecoder();
                            let buf = '';
                            let streamSettled = false;
                            let chunkEvents = 0;
                            let rawReads = 0;
                            /* eslint-disable no-await-in-loop */
                            while (true) {
                                const { done, value } = await reader.read();
                                if (done) {
                                    aiStreamLogVerbose('body read done', {
                                        rawReads: rawReads,
                                        chunkEvents: chunkEvents,
                                        streamSettled: streamSettled,
                                    });
                                    break;
                                }
                                rawReads += 1;
                                buf += dec.decode(value, { stream: true });
                                let sep;
                                while ((sep = buf.indexOf('\n\n')) >= 0) {
                                    const frame = buf.slice(0, sep);
                                    buf = buf.slice(sep + 2);
                                    const lines = frame.split('\n');
                                    for (let li = 0; li < lines.length; li++) {
                                        const line = lines[li];
                                        if (line.startsWith('data:')) {
                                            const jsonPart = line.slice(5).trimStart();
                                            try {
                                                const d = JSON.parse(jsonPart);
                                                const r = applySseData(
                                                    d,
                                                    chunkEl,
                                                    streamUserMsgIdRef,
                                                    dismissQueueNoticeOnceStreamBegan
                                                );
                                                if (r === 'chunk') {
                                                    chunkEvents += 1;
                                                    if (chunkEvents <= 5 || aiStreamDebugVerbose()) {
                                                        aiStreamLogVerbose('chunk #' + chunkEvents, {
                                                            textLen: (d.text && d.text.length) || 0,
                                                            preview:
                                                                d.text &&
                                                                d.text.slice
                                                                    ? JSON.stringify(d.text.slice(0, 80))
                                                                    : '',
                                                        });
                                                    }
                                                }
                                                if (r === 'error') {
                                                    streamSettled = true;
                                                    dismissQueueNoticeOnceStreamBegan();
                                                    removeStreamingAssistantBubble();
                                                    resetSendUi();
                                                    console.error(d.message || 'AI stream error');
                                                    releaseActiveFetchController(fetchController);
                                                    appendPromise
                                                        .finally(function() {
                                                            return fetchAndAppendMessagesAfter(
                                                                streamUserMsgIdRef.id ||
                                                                    fallbackUserMsgId
                                                            );
                                                        })
                                                        .catch(function() {});
                                                    return;
                                                }
                                                if (r === 'done') {
                                                    streamSettled = true;
                                                    removeStreamingAssistantBubble();
                                                    const uid =
                                                        streamUserMsgIdRef.id || fallbackUserMsgId;
                                                    releaseActiveFetchController(fetchController);
                                                    appendPromise
                                                        .then(function() {
                                                            return fetchAndAppendMessagesAfter(uid);
                                                        })
                                                        .catch(function() {
                                                            return fetchAndAppendMessagesAfter(uid);
                                                        })
                                                        .finally(function() {
                                                            removeStreamingAssistantBubble();
                                                            resetSendUi();
                                                            markUserActivity();
                                                        });
                                                    return;
                                                }
                                            } catch (parseErr) {
                                                aiStreamLogVerbose(
                                                    'non-JSON SSE line',
                                                    jsonPart.slice(0, 200),
                                                    parseErr
                                                );
                                            }
                                        }
                                    }
                                }
                            }
                            /* eslint-enable no-await-in-loop */
                            if (!streamSettled) {
                                console.warn('[AI stream] Stream ended without done/error; check server logs.', {
                                    chunkEvents: chunkEvents,
                                    rawReads: rawReads,
                                });
                                dismissQueueNoticeOnceStreamBegan();
                                removeStreamingAssistantBubble();
                                resetSendUi();
                                try {
                                    await appendPromise;
                                } catch (_) {
                                    /* ignore */
                                }
                                fetchAndAppendMessagesAfter(
                                    streamUserMsgIdRef.id || fallbackUserMsgId
                                );
                                releaseActiveFetchController(fetchController);
                            } else if (aiStreamDebugVerbose()) {
                                console.info('[AI stream] Stream settled OK', {
                                    chunkEvents: chunkEvents,
                                    rawReads: rawReads,
                                });
                            }
                            releaseActiveFetchController(fetchController);
                        }

                        if (res.ok && ct.includes('text/event-stream')) {
                            console.info('[AI stream] Branch: in-request SSE (200).');
                            await consumeSseFromFetch(res, null);
                            return false;
                        }
                        if (res.status === 202) {
                            console.info('[AI stream] Branch: async Queue + EventSource (202).');
                            releaseActiveFetchController(fetchController);
                            const payload = await res.json();
                            if (!payload.success || !payload.stream_url) {
                                throw new Error('async payload invalid');
                            }
                            aiStreamLogVerbose('stream_url', payload.stream_url);
                            const priorLastId = getLastMessageId();
                            const appendPromise = fetchAndAppendMessagesAfter(priorLastId).catch(
                                function() {
                                    return null;
                                }
                            );
                            const streamWrap = ensureStreamingAssistantBubble();
                            setStreamingTarget(payload.user_message_id);
                            appendPromise.finally(function() {
                                moveStreamingBubbleBelowMessages(streamWrap);
                                if (isWaitingForAssistantAtBottom()) {
                                    startQueueStatusPolling();
                                }
                            });
                            const chunkEl = streamWrap
                                ? streamWrap.querySelector('.streaming-assistant-chunk')
                                : null;
                            const es = new EventSource(payload.stream_url);
                            activeEventSource = es;
                            let streamSettled = false;
                            let esChunkCount = 0;
                            const streamUserMsgIdRef = { id: payload.user_message_id };
                            es.onopen = function() {
                                aiStreamLogVerbose('EventSource open');
                                // Async path reserves a room slot when the stream connects; exclude our
                                // slot from /queue-status "others" so we do not count ourselves as backlog.
                                queuePollSubtractSelf = 1;
                            };
                            es.onmessage = function(ev) {
                                try {
                                    const d = JSON.parse(ev.data);
                                    const r = applySseData(
                                        d,
                                        chunkEl,
                                        streamUserMsgIdRef,
                                        dismissQueueNoticeOnceStreamBegan
                                    );
                                    if (r === 'chunk') {
                                        esChunkCount += 1;
                                        if (esChunkCount <= 5 || aiStreamDebugVerbose()) {
                                            aiStreamLogVerbose('EventSource chunk #' + esChunkCount);
                                        }
                                    }
                                    if (r === 'error') {
                                        streamSettled = true;
                                        es.close();
                                        releaseActiveEventSource(es);
                                        dismissQueueNoticeOnceStreamBegan();
                                        removeStreamingAssistantBubble();
                                        resetSendUi();
                                        console.error(d.message || 'AI stream error');
                                        appendPromise
                                            .finally(function() {
                                                return fetchAndAppendMessagesAfter(
                                                    streamUserMsgIdRef.id ||
                                                        payload.user_message_id
                                                );
                                            })
                                            .catch(function() {});
                                    } else if (r === 'done') {
                                        streamSettled = true;
                                        es.close();
                                        releaseActiveEventSource(es);
                                        removeStreamingAssistantBubble();
                                        const uid =
                                            streamUserMsgIdRef.id || payload.user_message_id;
                                        appendPromise
                                            .then(function() {
                                                return fetchAndAppendMessagesAfter(uid);
                                            })
                                            .catch(function() {
                                                return fetchAndAppendMessagesAfter(uid);
                                            })
                                            .finally(function() {
                                                removeStreamingAssistantBubble();
                                                resetSendUi();
                                                markUserActivity();
                                            });
                                    }
                                } catch (_) { /* ignore bad frame */ }
                            };
                            es.onerror = function() {
                                if (streamSettled) return;
                                console.warn(
                                    '[AI stream] EventSource error (worker down, wrong token, or network). Chunks received:',
                                    esChunkCount
                                );
                                streamSettled = true;
                                es.close();
                                releaseActiveEventSource(es);
                                dismissQueueNoticeOnceStreamBegan();
                                removeStreamingAssistantBubble();
                                resetSendUi();
                                appendPromise
                                    .finally(function() {
                                        return fetchAndAppendMessagesAfter(
                                            streamUserMsgIdRef.id || payload.user_message_id
                                        );
                                    })
                                    .catch(function() {});
                            };
                            return false;
                        }
                        if (res.redirected && res.url) {
                            console.info('[AI stream] Branch: HTTP redirect — full navigation', res.url);
                            releaseActiveFetchController(fetchController);
                            window.location.assign(res.url);
                            return false;
                        }
                        console.warn(
                            '[AI stream] Unexpected response — not running native submit (avoid duplicate message).',
                            { status: res.status, contentType: ct }
                        );
                        resetSendUi();
                        releaseActiveFetchController(fetchController);
                        clearStreamingTarget();
                        return false;
                    } catch (err) {
                        releaseActiveFetchController(fetchController);
                        clearStreamingTarget();
                        console.warn('[AI stream] Fetch failed, falling back to full submit', err);
                    }
                }

                console.info(
                    '[AI stream] Native form submit (full page). AI:',
                    aiEnabled ? 'on' : 'off',
                    'useAiAsync:',
                    useAiAsync
                );
                HTMLFormElement.prototype.submit.call(form);
                return false;
            });
        }

        // Incremental polling for new messages with adaptive intervals
        // Active polling (5s) when user is interacting = real-time feel
        // Idle polling (90s) after 2 minutes inactive = reduced server load
        const ACTIVE_POLL_MS = 5000;   // 5s  = 720/hour (requires high rate limit)
        const IDLE_POLL_MS = 90000;    // 90s = 40/hour (well under 50/hour cap)
        const IDLE_TIMEOUT_MS = 120000; // 2 minutes before switching to idle
        let lastUserActivity = Date.now();

        let pollTimer = null;
        let backoff = ACTIVE_POLL_MS;
        const maxBackoff = 30000;

        function markUserActivity() {
            lastUserActivity = Date.now();
        }

        function getCurrentPollInterval() {
            const idleDuration = Date.now() - lastUserActivity;
            return idleDuration >= IDLE_TIMEOUT_MS ? IDLE_POLL_MS : ACTIVE_POLL_MS;
        }

        function scheduleNextPoll(delayMs) {
            if (pollTimer) clearTimeout(pollTimer);
            pollTimer = setTimeout(pollNewMessages, delayMs);
        }

        function getLastMessageId() {
            const container = document.getElementById('chat-messages');
            if (!container) return 0;
            const dataAttr = container.getAttribute('data-last-id');
            const last = parseInt(dataAttr || '0', 10);
            if (last) return last;
            // Fallback: read last element
            const items = container.querySelectorAll('[data-message-id]');
            if (items.length) {
                const id = parseInt(items[items.length - 1].getAttribute('data-message-id') || '0', 10);
                return isNaN(id) ? 0 : id;
            }
            return 0;
        }

        function setLastMessageId(id) {
            const container = document.getElementById('chat-messages');
            if (container) container.setAttribute('data-last-id', String(id || 0));
        }

        function isNearBottom(el) {
            if (!el) return false;
            return (el.scrollHeight - el.scrollTop - el.clientHeight) < 120;
        }

        async function pollNewMessages() {
            if (document.hidden) {
                scheduleNextPoll(getCurrentPollInterval());
                return; // pause when tab hidden
            }
            try {
                const lastId = getLastMessageId();
                
                // Get chat ID from URL (more robust than data attribute)
                let chatId = window.location.pathname.match(/\/chat\/(\d+)/)?.[1];
                
                // Fallback: try data attribute if URL parsing fails
                if (!chatId) {
                    const chatContainer = document.querySelector('.chat-container');
                    chatId = chatContainer?.dataset.chatId;
                }
                
                if (!chatId) {
                    console.error('Could not determine chat ID from URL or data attribute');
                    scheduleNextPoll(Math.max(backoff, getCurrentPollInterval()));
                    return;
                }
                
                const resp = await fetch(`/chat/${chatId}/messages?after_id=${lastId}`);
                const data = await resp.json();
                if (!data.success) throw new Error(data.error || 'poll failed');
                const list = data.messages || [];
                if (list.length === 0) {
                    backoff = ACTIVE_POLL_MS; // reset backoff on empty success
                    scheduleNextPoll(Math.max(backoff, getCurrentPollInterval()));
                    return;
                }
                if (list.some(function(m) { return m.role === 'assistant'; })) {
                    stopQueueStatusPolling();
                    hideQueueNotice();
                }
                // New content arrived – treat as fresh activity so we stay on the fast cadence
                markUserActivity();
                appendMessageEntries(list);
                if (data.last_id != null && data.last_id !== '') {
                    const nid = parseInt(String(data.last_id), 10) || 0;
                    const cur = getLastMessageId();
                    if (nid > cur) {
                        setLastMessageId(nid);
                    }
                }
                backoff = ACTIVE_POLL_MS; // reset after success
            } catch (e) {
                // backoff on errors
                backoff = Math.min(backoff * 2, maxBackoff);
            }
            scheduleNextPoll(Math.max(backoff, getCurrentPollInterval()));
        }

        function startPolling() {
            scheduleNextPoll(getCurrentPollInterval());
        }

        document.addEventListener('visibilitychange', function() {
            if (!document.hidden) {
                markUserActivity();
                // trigger an immediate poll when tab becomes visible
                pollNewMessages();
            }
        });

        // kick off
        startPolling();
        if (isWaitingForAssistantAtBottom()) {
            startQueueStatusPolling();
        }
    });
    
    // Learning Progress Assessment Functions
    let lastProgressRecommendation = null;
    const DEFAULT_MODE_ORDER = ['explore', 'focus', 'context', 'proposal', 'outline', 'draft', 'revise', 'evidence', 'citation', 'reflect'];

    function getChatContainer() {
        return document.querySelector('.chat-container');
    }

    function parseDatasetJson(value, fallback = null) {
        if (!value) return fallback;
        try {
            return JSON.parse(value);
        } catch (e) {
            console.warn('Unable to parse dataset JSON value', value, e);
            return fallback;
        }
    }

    let cachedModeOrder = null;
    function getModeOrder() {
        if (cachedModeOrder) return cachedModeOrder;
        const container = getChatContainer();
        if (!container) return DEFAULT_MODE_ORDER;
        const parsed = parseDatasetJson(container.dataset.modeOrder, null);
        cachedModeOrder = Array.isArray(parsed) && parsed.length ? parsed : DEFAULT_MODE_ORDER;
        return cachedModeOrder;
    }

    let cachedModeLabels = null;
    function getModeLabels() {
        if (cachedModeLabels) return cachedModeLabels;
        const container = getChatContainer();
        if (!container) return {};
        const parsed = parseDatasetJson(container.dataset.modeLabels, {});
        cachedModeLabels = parsed && typeof parsed === 'object' ? parsed : {};
        return cachedModeLabels;
    }

    let cachedModeMap = null;
    function getModeChatMap() {
        if (cachedModeMap) return cachedModeMap;
        const container = getChatContainer();
        if (!container) return {};
        const parsed = parseDatasetJson(container.dataset.modeMap, {});
        cachedModeMap = parsed && typeof parsed === 'object' ? parsed : {};
        return cachedModeMap;
    }

    function getExistingChatIdForMode(mode) {
        if (!mode) return null;
        const map = getModeChatMap();
        const entries = map && map[mode];
        if (!entries) return null;
        if (Array.isArray(entries) && entries.length > 0) {
            const last = entries[entries.length - 1];
            if (typeof last === 'number') return last;
            if (last && typeof last === 'object') {
                return last.id || last.chat_id || null;
            }
        } else if (typeof entries === 'number') {
            return entries;
        }
        return null;
    }

    function showRoomCompletionMessage() {
        const progressStatus = document.getElementById('progress-status');
        const progressContent = document.getElementById('progress-content');
        const assessBtn = document.getElementById('assess-progress-btn');
        updateProgressSummary('Room complete');

        if (progressContent) {
            progressContent.innerHTML = `
                <div class="bg-emerald-50 border border-emerald-200 rounded-md p-3">
                    <div class="flex items-start gap-2">
                        <div class="text-emerald-600 text-lg">🎉</div>
                        <div class="flex-1">
                            <p class="font-medium text-emerald-800 mb-1">Congratulations! Room completed</p>
                            <p class="text-emerald-700 text-xs">You’ve finished every step in this learning journey. Feel free to review past chats or start a new room to keep exploring.</p>
                        </div>
                    </div>
                </div>
            `;
        }

        if (progressStatus) {
            progressStatus.classList.remove('hidden');
        }

        if (assessBtn) {
            assessBtn.disabled = true;
            assessBtn.textContent = 'Room completed';
        }
    }

    function assessLearningProgress() {
        console.log('🔍 Assess Progress button clicked!');
        
        const assessBtn = document.getElementById('assess-progress-btn');
        const progressStatus = document.getElementById('progress-status');
        const progressLoading = document.getElementById('progress-loading');
        const progressContent = document.getElementById('progress-content');
        
        console.log('Elements found:', { assessBtn, progressStatus, progressLoading, progressContent });
        
        // Show loading state
        assessBtn.disabled = true;
        assessBtn.textContent = 'Analyzing...';
        progressStatus.classList.add('hidden');
        progressLoading.classList.remove('hidden');
        
        // Make API request
        const chatContainer = getChatContainer();
        console.log('Chat container:', chatContainer);
        console.log('Dataset:', chatContainer ? chatContainer.dataset : 'No container found');
        
        const chatId = chatContainer ? chatContainer.dataset.chatId : null;
        console.log('Chat ID:', chatId);
        
        if (!chatId) {
            console.error('❌ No chat ID found! Cannot proceed.');
            displayProgressError('Configuration error. Please refresh the page.');
            return;
        }
        
        fetch(`/chat/${chatId}/assess-progression`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading state
            progressLoading.classList.add('hidden');
            
            if (data.success) {
                displayProgressResult(data.recommendation);
            } else {
                displayProgressError(data.error || 'Assessment failed');
            }
        })
        .catch(error => {
            console.error('Assessment error:', error);
            progressLoading.classList.add('hidden');
            displayProgressError('Network error. Please try again.');
        })
        .finally(() => {
            // Reset button
            assessBtn.disabled = false;
            assessBtn.textContent = '🔍 Assess Progress';
        });
    }
    
    function displayProgressResult(recommendation) {
        const progressStatus = document.getElementById('progress-status');
        const progressContent = document.getElementById('progress-content');
        lastProgressRecommendation = recommendation || null;
        
        // Update Tools summary with assessment result
        const summaryLabel = recommendation && recommendation.ready ? 'Ready to advance' : 
                           recommendation && recommendation.confidence > 0.7 ? 'Good progress' :
                           'In progress';
        updateProgressSummary(summaryLabel);
        
        let html = '';
        
        if (recommendation.type === 'ready') {
            html = `
                <div class="bg-green-50 border border-green-200 rounded-md p-3">
                    <div class="flex items-start gap-2">
                        <div class="text-green-600 text-lg">🎉</div>
                        <div class="flex-1">
                            <p class="font-medium text-green-800 mb-2">${recommendation.message}</p>
                            <p class="text-green-700 text-xs mb-3">Confidence: ${Math.round(recommendation.confidence * 100)}%</p>
                            ${recommendation.next_step ? `
                                <div class="bg-white rounded p-2 mb-2">
                                    <p class="font-medium text-green-800 text-xs">Next Step: ${recommendation.next_step.label}</p>
                                    <p class="text-green-700 text-xs">${recommendation.next_step.description}</p>
                                </div>
                            ` : ''}
                            <button onclick="createNextStepChat()" 
                                    class="text-xs px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors">
                                Create Next Step Chat
                            </button>
                        </div>
                    </div>
                </div>
            `;
        } else if (recommendation.type === 'almost_ready') {
            html = `
                <div class="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                    <div class="flex items-start gap-2">
                        <div class="text-yellow-600 text-lg">👍</div>
                        <div class="flex-1">
                            <p class="font-medium text-yellow-800 mb-2">${recommendation.message}</p>
                            <p class="text-yellow-700 text-xs mb-3">Confidence: ${Math.round(recommendation.confidence * 100)}%</p>
                            <div class="bg-white rounded p-2">
                                <p class="font-medium text-yellow-800 text-xs mb-1">Suggestions:</p>
                                <ul class="text-yellow-700 text-xs space-y-1">
                                    ${recommendation.suggestions.map(suggestion => `<li>• ${suggestion}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            html = `
                <div class="bg-blue-50 border border-blue-200 rounded-md p-3">
                    <div class="flex items-start gap-2">
                        <div class="text-blue-600 text-lg">📚</div>
                        <div class="flex-1">
                            <p class="font-medium text-blue-800 mb-2">${recommendation.message}</p>
                            <p class="text-blue-700 text-xs mb-3">Confidence: ${Math.round(recommendation.confidence * 100)}%</p>
                            <div class="bg-white rounded p-2">
                                <p class="font-medium text-blue-800 text-xs mb-1">Keep working on:</p>
                                <ul class="text-blue-700 text-xs space-y-1">
                                    ${recommendation.suggestions.map(suggestion => `<li>• ${suggestion}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        progressContent.innerHTML = html;
        progressStatus.classList.remove('hidden');
    }
    
    function displayProgressError(error) {
        const progressStatus = document.getElementById('progress-status');
        const progressContent = document.getElementById('progress-content');
        lastProgressRecommendation = null;
        
        progressContent.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-md p-3">
                <div class="flex items-start gap-2">
                    <div class="text-red-600 text-lg">⚠️</div>
                    <div class="flex-1">
                        <p class="font-medium text-red-800">Assessment Error</p>
                        <p class="text-red-700 text-xs">${error}</p>
                    </div>
                </div>
            </div>
        `;
        progressStatus.classList.remove('hidden');
    }
    
    async function createNextStepChat() {
        const chatContainer = getChatContainer();
        if (!chatContainer) {
            console.error('Chat container not found');
            return;
        }

        const roomId = chatContainer.dataset.roomId;
        const currentMode = chatContainer.dataset.chatMode || 'explore';

        if (!roomId) {
            console.error('Room ID missing on chat container');
            return;
        }

        const nextStep = getNextStepFromRecommendation();
        if (!nextStep) {
            console.log('No next step available - room complete');
            showRoomCompletionMessage();
            return;
        }

        const mode = nextStep.key || currentMode || 'explore';
        const modeLabels = getModeLabels();
        const label = nextStep.label || modeLabels[mode] || mode;
        const existingChatId = getExistingChatIdForMode(mode);
        if (existingChatId) {
            console.log(`Next step chat already exists for mode ${mode} (chat ${existingChatId}) - redirecting`);
            window.location.href = `/chat/${existingChatId}`;
            return;
        }

        const title = `Next Step: ${label}`;

        try {
            const response = await fetch(`/room/${roomId}/chat/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title,
                    mode,
                    source: 'next_step'
                })
            });

            if (!response.ok) {
                throw new Error(`Request failed with status ${response.status}`);
            }

            const data = await response.json();
            if (data?.success && data?.chat_id) {
                window.location.href = `/chat/${data.chat_id}`;
                return;
            }
            if (data?.existing && data?.chat_id) {
                window.location.href = `/chat/${data.chat_id}`;
                return;
            }

            // Unexpected response shape – fallback to legacy page
            console.warn('Unexpected response creating chat:', data);
            window.location.href = `/room/${roomId}/chat/create?mode=${mode}`;
        } catch (error) {
            console.error('Failed to create next step chat:', error);
            // Fallback to legacy flow on error
            window.location.href = `/room/${roomId}/chat/create?mode=${mode}`;
        }
    }
    
    function getNextStepFromRecommendation() {
        if (lastProgressRecommendation && lastProgressRecommendation.next_step && lastProgressRecommendation.next_step.key) {
            return lastProgressRecommendation.next_step;
        }

        const chatContainer = getChatContainer();
        const currentMode = chatContainer?.dataset?.chatMode;
        if (!currentMode) return null;

        const modeOrder = getModeOrder();
        const labels = getModeLabels();
        const currentIndex = modeOrder.indexOf(currentMode);

        if (currentIndex >= 0 && currentIndex < modeOrder.length - 1) {
            const key = modeOrder[currentIndex + 1];
            return {
                key,
                label: labels[key] || `Step ${currentIndex + 2}`
            };
        }

        return null;
    }

    // ===================================
    // Tools Summary Status Updates
    // ===================================
    
    // Tone level names
    const TONE_LABELS = ['Not set', 'Very Supportive', 'Supportive', 'Balanced', 'Critical', 'Very Critical'];
    
    function updateToneSummary(level) {
        const summaryEl = document.getElementById('tone-summary');
        if (summaryEl) {
            summaryEl.textContent = TONE_LABELS[level] || 'Not set';
        }
    }
    
    function updateProgressSummary(status) {
        const summaryEl = document.getElementById('progress-summary');
        if (summaryEl) {
            summaryEl.textContent = status || 'Not assessed';
        }
    }
    
    // Listen for tone changes (from critique component)
    document.addEventListener('tone:change', function(e) {
        if (e.detail && typeof e.detail.level !== 'undefined') {
            updateToneSummary(e.detail.level);
        }
    });
    
    // Initialize tone from sessionStorage if available
    try {
        // Get chat ID from URL
        const chatId = window.location.pathname.match(/\/chat\/(\d+)/)?.[1];
        if (chatId) {
            // Try new key first (chat_${chatId}_critique)
            let savedTone = sessionStorage.getItem(`chat_${chatId}_critique`);
            
            // Fallback to legacy key (room81_critique_level) for transition
            if (!savedTone) {
                savedTone = sessionStorage.getItem('room81_critique_level');
            }
            
            if (savedTone) {
                updateToneSummary(parseInt(savedTone, 10));
            }
        }
    } catch (e) {
        console.log('Could not load saved tone:', e);
    }
