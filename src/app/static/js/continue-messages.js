(function () {
  if (window.__CONTINUE_INIT__) return;
  window.__CONTINUE_INIT__ = 'v1.5';

  /** Min plain-text length to offer Continue when the DB flag is false (streaming sometimes omits truncation). */
  var LONG_ASSISTANT_CHARS = 3200;

  function enhanceBubble(bubble) {
    if (!bubble) return;

    const content = bubble.querySelector('.message-content');
    if (!content) return;

    content.querySelectorAll('a.continue-link, .continue-cta').forEach(function (el) {
      el.remove();
    });

    const truncatedFlag = bubble.getAttribute('data-truncated') === 'true';
    const textLen = (content.textContent || '').trim().length;
    const showContinue = truncatedFlag || textLen >= LONG_ASSISTANT_CHARS;
    if (!showContinue) {
      delete bubble.dataset.continueEnhanced;
      return;
    }

    const tsRow = content.querySelector('.message-timestamp');

    const a = document.createElement('button');
    a.type = 'button';
    a.className =
      'continue-cta inline-flex items-center justify-center gap-1 text-xs font-semibold ml-2 rounded-md ' +
      'text-blue-800 bg-blue-50 border border-blue-200 hover:bg-blue-100 hover:border-blue-300 ' +
      'dark:text-blue-100 dark:bg-blue-950/50 dark:border-blue-700 dark:hover:bg-blue-900/40';
    a.setAttribute('aria-label', 'Continue this response');
    a.innerHTML =
      '<svg class="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
      'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg> Continue';

    a.addEventListener('click', async function () {
      const messageWrapper = bubble.closest('[data-message-id]');
      if (!messageWrapper) return;

      const messageId = messageWrapper.dataset.messageId;
      const chatId = window.location.pathname.match(/\/chat\/(\d+)/)?.[1];

      if (!chatId || !messageId) {
        console.error('Cannot continue: missing chat ID or message ID');
        return;
      }

      const CONTINUE_ICON =
        '<svg class="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
        'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg> Continue';
      function resetButton() {
        a.disabled = false;
        a.innerHTML = CONTINUE_ICON;
      }

      a.disabled = true;
      a.innerHTML =
        '<svg class="w-3.5 h-3.5 shrink-0 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
        '<path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg> Continuing...';

      try {
        var csrf =
          document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
          document.querySelector('#message-form input[name="csrf_token"]')?.value ||
          '';
        const response = await fetch('/chat/' + chatId + '/continue/' + messageId, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf,
          },
        });

        // Async worker path: 202 + { async, stream_url }. The continuation is generated
        // off-thread by the worker; stream it over the same SSE endpoint the main reply
        // uses, then reload to render it. Reloading (rather than live-appending) keeps
        // this button's long-standing UX while freeing the server thread immediately.
        if (response.status === 202) {
          let data = {};
          try { data = await response.json(); } catch (e) { /* fall through */ }
          if (data && data.async && data.stream_url) {
            let settled = false;
            const es = new EventSource(data.stream_url);
            es.onmessage = function (ev) {
              let d = null;
              try { d = JSON.parse(ev.data); } catch (e) { return; }
              if (d.type === 'done') {
                settled = true;
                es.close();
                window.location.reload();
              } else if (d.type === 'error') {
                settled = true;
                es.close();
                console.error('Continue stream error:', d.message);
                resetButton();
              }
            };
            es.onerror = function () {
              // Stream dropped. If we never saw a terminal event, reload best-effort —
              // the worker may still have persisted the continuation.
              es.close();
              if (!settled) window.location.reload();
            };
            return;
          }
          // Malformed 202 — safe default is to reload.
          window.location.reload();
          return;
        }

        if (response.ok) {
          window.location.reload();
        } else {
          console.error('Continue failed:', response.status);
          resetButton();
        }
      } catch (error) {
        console.error('Continue error:', error);
        resetButton();
      }
    });

    if (tsRow) {
      const pinBtn = tsRow.querySelector('.pin-toggle');
      if (pinBtn) {
        pinBtn.insertAdjacentElement('afterend', a);
      } else {
        tsRow.appendChild(a);
      }
    } else {
      content.appendChild(a);
    }

    bubble.dataset.continueEnhanced = '1';
  }

  function enhanceAll() {
    document.querySelectorAll('.message-bubble.assistant').forEach(function (b) {
      delete b.dataset.continueEnhanced;
      enhanceBubble(b);
    });
  }

  window.refreshContinueButtons = enhanceAll;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhanceAll);
  } else {
    enhanceAll();
  }

  const messages = document.getElementById('chat-messages');
  if (messages && !window.__CONTINUE_OBS__) {
    window.__CONTINUE_OBS__ = new MutationObserver(function (muts) {
      for (var i = 0; i < muts.length; i++) {
        var m = muts[i];
        m.addedNodes.forEach(function (node) {
          if (!(node instanceof HTMLElement)) return;
          if (node.matches && node.matches('.message-bubble.assistant')) {
            delete node.dataset.continueEnhanced;
            enhanceBubble(node);
          }
          if (node.querySelectorAll) {
            node.querySelectorAll('.message-bubble.assistant').forEach(function (b) {
              delete b.dataset.continueEnhanced;
              enhanceBubble(b);
            });
          }
        });
      }
    });
    window.__CONTINUE_OBS__.observe(messages, { childList: true, subtree: true });
  }
})();
