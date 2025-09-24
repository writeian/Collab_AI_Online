(function () {
  // prevent duplicate init
  if (window.__CONTINUE_INIT__) return;
  window.__CONTINUE_INIT__ = 'v1.2';

  function enhanceBubble(bubble) {
    if (!bubble || bubble.dataset.continueEnhanced === '1') return;

    const content = bubble.querySelector('.message-content');
    if (!content) return;

    // remove any old anchors injected elsewhere
    content.querySelectorAll('a.continue-link, .continue-cta').forEach(el => el.remove());

    const ts = content.querySelector('.message-timestamp');

    // figure out the last non-timestamp block to make it feel "end of the message"
    let lastTextEl = null;
    Array.from(content.children).forEach(el => {
      if (!el.classList.contains('message-timestamp')) lastTextEl = el;
    });

    // create CTA (inline-friendly)
    const a = document.createElement('button');
    a.type = 'button';
    a.className = 'continue-cta inline-flex items-center gap-1 text-xs text-primary hover:text-primary/80 ml-2 align-baseline';
    a.setAttribute('aria-label', 'Continue this response');
    a.innerHTML = `<svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
      stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg> Continue`;

    // action: submit the existing form with "continue"
    a.addEventListener('click', () => {
      const form = document.getElementById('message-form');
      const input = document.getElementById('message-input');
      if (!form || !input) return;
      const old = input.value;
      input.value = 'Complete or expand your last message';
      if (typeof form.requestSubmit === 'function') form.requestSubmit(); else form.submit();
      // restore whatever was typed
      setTimeout(() => { input.value = old; }, 0);
    });

    // preferred placement: at the very end of the AI text (inline in the last block if possible)
    if (lastTextEl && lastTextEl.nodeName === 'P') {
      lastTextEl.appendChild(document.createTextNode(' '));
      lastTextEl.appendChild(a);
    } else if (ts) {
      // fallback: just before timestamp (always before it, never after)
      content.insertBefore(a, ts);
    } else {
      content.appendChild(a);
    }

    bubble.dataset.continueEnhanced = '1';
  }

  function enhanceAll() {
    document.querySelectorAll('.message-bubble.assistant').forEach(enhanceBubble);
  }

  // initial pass
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhanceAll);
  } else {
    enhanceAll();
  }

  // observe future messages appended by polling
  const messages = document.getElementById('chat-messages');
  if (messages && !window.__CONTINUE_OBS__) {
    window.__CONTINUE_OBS__ = new MutationObserver(muts => {
      for (const m of muts) {
        m.addedNodes.forEach(node => {
          if (!(node instanceof HTMLElement)) return;
          if (node.matches?.('.message-bubble.assistant')) enhanceBubble(node);
          node.querySelectorAll?.('.message-bubble.assistant').forEach(enhanceBubble);
        });
      }
    });
    window.__CONTINUE_OBS__.observe(messages, { childList: true, subtree: true });
  }
})();

// Old functions removed - using new idempotent approach above
