// Continue Messages Feature
// Adds "Continue" links to AI messages for expansion/completion

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔗 Continue messages script loaded');
    
    // Only run on chat pages
    if (!/^\/chat\/\d+/.test(location.pathname)) {
        console.log('🔗 Not a chat page, skipping');
        return;
    }
    
    console.log('🔗 On chat page, adding continue links');
    addContinueLinks();
    
    // Re-add continue links when new messages are added dynamically
    observeNewMessages();
});

function addContinueLinks() {
    // Find all AI assistant messages using actual DOM structure
    const aiMessages = document.querySelectorAll('.message-bubble.assistant');
    console.log(`🔗 Found ${aiMessages.length} AI messages`);
    
    aiMessages.forEach((messageElement, index) => {
        console.log(`🔗 Processing AI message ${index + 1}`);
        // Skip if already has continue link
        if (messageElement.querySelector('.continue-link')) return;
        
        // Get message ID from parent container
        const messageContainer = messageElement.closest('[data-message-id]');
        const messageId = messageContainer?.dataset.messageId;
        console.log(`🔗 Message ${index + 1} ID: ${messageId}`);
        if (!messageId) {
            console.log(`🔗 No message ID found for message ${index + 1}`);
            return;
        }
        
        // Create continue link
        const continueLink = document.createElement('a');
        continueLink.href = '#';
        continueLink.className = 'continue-link text-xs text-primary hover:underline ml-2 inline-flex items-center gap-1';
        continueLink.innerHTML = '<i data-lucide="arrow-right" class="w-3 h-3"></i>Continue';
        continueLink.title = 'Ask AI to complete or expand this response';
        
        continueLink.addEventListener('click', function(e) {
            e.preventDefault();
            continueMessage(messageId);
        });
        
        // Add continue link inline at the very end of the message text
        const messageContent = messageElement.querySelector('.message-content p');
        if (messageContent) {
            // Create inline span instead of block element
            const continueSpan = document.createElement('span');
            continueSpan.className = 'continue-link text-xs text-primary hover:underline ml-1';
            continueSpan.innerHTML = ' <i data-lucide="arrow-right" class="w-3 h-3 inline"></i>Continue';
            continueSpan.style.cursor = 'pointer';
            
            continueSpan.addEventListener('click', function(e) {
                e.preventDefault();
                continueMessage(messageId);
            });
            
            // Insert at the very end of the paragraph text
            messageContent.appendChild(continueSpan);
        } else {
            // Fallback: add to message content container
            const contentContainer = messageElement.querySelector('.message-content');
            if (contentContainer) {
                contentContainer.appendChild(continueLink);
            }
        }
    });
    
    // Refresh Lucide icons for the new arrow icons
    if (window.lucide && typeof lucide.createIcons === 'function') {
        lucide.createIcons();
    }
}

function getMessageId(messageElement) {
    // Try various ways to get message ID
    return messageElement.dataset.messageId || 
           messageElement.dataset.id ||
           messageElement.id?.replace('message-', '') ||
           messageElement.querySelector('[data-message-id]')?.dataset.messageId ||
           extractIdFromClasses(messageElement);
}

function extractIdFromClasses(element) {
    // Look for ID in class names like "message-123" or "msg-123"
    const classList = Array.from(element.classList);
    for (const className of classList) {
        const match = className.match(/(?:message|msg)-(\d+)/);
        if (match) return match[1];
    }
    return null;
}

function continueMessage(messageId) {
    const chatId = getChatIdFromUrl();
    if (!chatId || !messageId) {
        console.error('Cannot continue: missing chat ID or message ID');
        return;
    }
    
    // Show loading state
    const continueLinks = document.querySelectorAll('.continue-link');
    continueLinks.forEach(link => {
        link.innerHTML = '<i data-lucide="loader-2" class="w-3 h-3 animate-spin"></i>Continuing...';
        link.style.pointerEvents = 'none';
    });
    
    // Create form to submit continue request
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/chat/${chatId}/continue/${messageId}`;
    form.style.display = 'none';
    
    // Add CSRF token
    const token = getCsrfToken();
    if (token) {
        const csrf = document.createElement('input');
        csrf.type = 'hidden';
        csrf.name = 'csrf_token';
        csrf.value = token;
        form.appendChild(csrf);
    }
    
    document.body.appendChild(form);
    form.submit();
}

function getChatIdFromUrl() {
    const match = window.location.pathname.match(/\/chat\/(\d+)/);
    return match ? match[1] : null;
}

function getCsrfToken() {
    return document.cookie.split('; ').find(r => r.startsWith('csrf_token='))?.split('=')[1] || '';
}

function observeNewMessages() {
    // Watch for new messages being added dynamically (e.g., via AJAX)
    const observer = new MutationObserver(function(mutations) {
        let hasNewMessages = false;
        
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) { // Element node
                    // Check if the added node is a message or contains messages
                    if (node.matches && (node.matches('.message, .message-bubble, [data-role="assistant"]') ||
                        node.querySelector('.message, .message-bubble, [data-role="assistant"]'))) {
                        hasNewMessages = true;
                    }
                }
            });
        });
        
        if (hasNewMessages) {
            // Small delay to ensure DOM is stable
            setTimeout(addContinueLinks, 100);
        }
    });
    
    // Observe the chat messages container
    const messagesContainer = document.querySelector('#chat-messages, .messages-container, .chat-container');
    if (messagesContainer) {
        observer.observe(messagesContainer, {
            childList: true,
            subtree: true
        });
    }
}
