/**
 * Shared helpers for Educational Tools API calls.
 * Provides CSRF token retrieval and JSON fetch with CSRF headers.
 */
(function(global) {
    'use strict';

    /**
     * Get CSRF token from meta tag, form, or cookie.
     * @returns {string|null}
     */
    function getCsrfToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) return metaTag.getAttribute('content');
        const form = document.querySelector('form[method="POST"]');
        if (form) {
            const csrfInput = form.querySelector('input[name="csrf_token"]');
            if (csrfInput) return csrfInput.value;
        }
        const match = document.cookie.match(/csrf_token=([^;]+)/);
        return match ? match[1] : null;
    }

    /**
     * JSON fetch with CSRF token for mutating requests.
     * @param {string} url
     * @param {RequestInit} options
     * @returns {Promise<Response>}
     */
    function jsonFetch(url, options) {
        const opts = options || {};
        const method = (opts.method || 'GET').toUpperCase();
        const headers = new Headers(opts.headers || {});
        if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
            const token = getCsrfToken();
            if (token) headers.set('X-CSRFToken', token);
        }
        if (!headers.has('Content-Type') && opts.body && typeof opts.body === 'string') {
            headers.set('Content-Type', 'application/json');
        }
        return fetch(url, { ...opts, headers });
    }

    global.getCsrfToken = getCsrfToken;
    global.jsonFetch = jsonFetch;
})(typeof window !== 'undefined' ? window : this);
