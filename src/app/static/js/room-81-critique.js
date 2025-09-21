// Room 81 Specific Critique Tool - Test Implementation
// Only activates for chats in room 81

document.addEventListener('DOMContentLoaded', function() {
    // Only run on chat pages
    if (!window.location.pathname.includes('/chat/')) return;
    
    // Check if this chat belongs to room 81
    checkIfRoom81Chat().then(isRoom81 => {
        if (isRoom81) {
            console.log('🎚️ Room 81 critique tool activated');
            initializeCritiqueTool();
        }
    });
});

async function checkIfRoom81Chat() {
    try {
        // Get chat info from page content
        const roomLink = document.querySelector('a[href*="/room/81"]') || 
                        document.querySelector('a[href*="room/81"]');
        
        if (roomLink) {
            return true;
        }
        
        // Fallback: check page title or breadcrumb
        const pageText = document.body.textContent;
        return pageText.includes('room/81') || 
               document.title.includes('Room 81') ||
               window.location.search.includes('room_id=81');
               
    } catch (error) {
        console.warn('Could not determine if room 81:', error);
        return false;
    }
}

function initializeCritiqueTool() {
    const chatId = getChatIdFromUrl();
    if (!chatId) return;
    
    // Add critique slider to chat header
    addCritiqueSlider(chatId);
    
    // Intercept message forms to include critique level
    interceptMessageForms(chatId);
}

function getChatIdFromUrl() {
    const match = window.location.pathname.match(/\/chat\/(\d+)/);
    return match ? match[1] : null;
}

function addCritiqueSlider(chatId) {
    // Find a good spot in the chat interface
    const chatHeader = document.querySelector('h1, h2, .text-2xl') || 
                      document.querySelector('.chat-header') ||
                      document.querySelector('form')?.parentElement;
    
    if (!chatHeader) {
        console.warn('Could not find chat header for critique slider');
        return;
    }
    
    // Get current level from session (default to 3)
    const currentLevel = getCritiqueLevel(chatId);
    const levelNames = ['', 'Very Supportive', 'Supportive', 'Balanced', 'Critical', 'Very Critical'];
    
    // Create slider container
    const sliderContainer = document.createElement('div');
    sliderContainer.className = 'mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg';
    sliderContainer.innerHTML = `
        <div class="text-sm font-medium text-blue-800 mb-2 flex items-center gap-2">
            🎚️ AI Feedback Style (Room 81 Test)
        </div>
        <div class="flex items-center gap-3">
            <span class="text-xs text-gray-600">🤝 Supportive</span>
            <input id="room81-critique-slider" 
                   type="range" 
                   min="1" 
                   max="5" 
                   value="${currentLevel}"
                   class="flex-1 h-2 bg-gradient-to-r from-green-400 via-yellow-400 to-red-400 rounded-lg appearance-none cursor-pointer"
                   title="AI feedback style" />
            <span class="text-xs text-gray-600">🔎 Critical</span>
        </div>
        <div class="text-xs text-gray-600 mt-1 text-center">
            Current: <span id="critique-level-display">${levelNames[currentLevel]}</span>
        </div>
    `;
    
    // Insert after chat header
    chatHeader.parentNode.insertBefore(sliderContainer, chatHeader.nextSibling);
    
    // Add event listener
    const slider = document.getElementById('room81-critique-slider');
    const display = document.getElementById('critique-level-display');
    
    if (slider && display) {
        slider.addEventListener('input', function() {
            const level = parseInt(this.value);
            display.textContent = levelNames[level] || 'Balanced';
            
            // Store in session storage for this session
            sessionStorage.setItem(`room81_chat_${chatId}_critique`, level);
            
            // Show brief feedback
            showFeedback(`AI style changed to: ${levelNames[level]}`);
        });
    }
}

function getCritiqueLevel(chatId) {
    // Get from session storage (persists for browser session)
    return sessionStorage.getItem(`room81_chat_${chatId}_critique`) || '3';
}

function interceptMessageForms(chatId) {
    // Find message forms and add critique level
    const forms = document.querySelectorAll('form[method="POST"]');
    
    forms.forEach(form => {
        const contentField = form.querySelector('textarea[name="content"], input[name="content"]');
        if (!contentField) return;
        
        // Add hidden field for critique level
        const critiqueInput = document.createElement('input');
        critiqueInput.type = 'hidden';
        critiqueInput.name = 'room81_critique_level';
        critiqueInput.id = 'room81-critique-input';
        form.appendChild(critiqueInput);
        
        // Update critique level before form submission
        form.addEventListener('submit', function() {
            const currentLevel = getCritiqueLevel(chatId);
            critiqueInput.value = currentLevel;
            
            // Add critique instructions as hidden field
            const instructions = getCritiqueInstructions(parseInt(currentLevel));
            
            let instructionsInput = form.querySelector('#room81-critique-instructions');
            if (!instructionsInput) {
                instructionsInput = document.createElement('input');
                instructionsInput.type = 'hidden';
                instructionsInput.name = 'room81_critique_instructions';
                instructionsInput.id = 'room81-critique-instructions';
                form.appendChild(instructionsInput);
            }
            instructionsInput.value = instructions;
        });
    });
}

function getCritiqueInstructions(level) {
    const instructions = {
        1: "Be warmly supportive. Praise effort and provide at most two gentle suggestions. Focus on what's working well and provide encouraging guidance.",
        2: "Be friendly and constructive. Balance praise with specific suggestions. Ask clarifying questions to understand intent.",
        3: "Be neutral and concise. Give balanced pros and cons. Provide three actionable improvements with clear examples.",
        4: "Be rigorous and analytical. Challenge assumptions and require evidence for claims. Rank issues by impact and push for higher standards.",
        5: "Act as an exacting reviewer. Insist on evidence for all claims. Provide pointed, actionable edits with no fluff. Be demanding about quality and precision."
    };
    return instructions[level] || instructions[3];
}

function showFeedback(message) {
    const feedback = document.createElement('div');
    feedback.className = 'fixed top-4 right-4 bg-blue-100 border border-blue-300 text-blue-800 px-4 py-2 rounded-lg text-sm z-50 shadow-lg';
    feedback.textContent = message;
    document.body.appendChild(feedback);
    
    setTimeout(() => {
        if (feedback.parentNode) {
            feedback.style.opacity = '0';
            feedback.style.transform = 'translateY(-10px)';
            feedback.style.transition = 'all 0.3s ease';
            setTimeout(() => feedback.remove(), 300);
        }
    }, 2000);
}
