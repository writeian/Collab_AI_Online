/**
 * Shared API helpers for educational tools.
 * Adds consistent CSRF handling for JSON requests.
 */
(function() {
    'use strict';

    function getCsrfToken() {
        const metaToken = document.querySelector('meta[name="csrf-token"]')?.content;
        if (metaToken) {
            return metaToken;
        }

        const cookieMatch = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]+)/);
        if (cookieMatch && cookieMatch[1]) {
            return decodeURIComponent(cookieMatch[1]);
        }

        const formToken = document.querySelector('input[name="csrf_token"]')?.value;
        return formToken || null;
    }

    function jsonFetch(url, payload, options = {}) {
        const method = (options.method || 'POST').toUpperCase();
        const headers = Object.assign(
            {
                'Accept': 'application/json',
            },
            options.headers || {}
        );

        if (method !== 'GET' && method !== 'HEAD') {
            headers['Content-Type'] = headers['Content-Type'] || 'application/json';
            const csrfToken = getCsrfToken();
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }
        }

        const fetchOptions = Object.assign({}, options, {
            method: method,
            credentials: options.credentials || 'same-origin',
            headers: headers,
        });

        if (payload !== undefined) {
            fetchOptions.body = headers['Content-Type'] === 'application/json'
                ? JSON.stringify(payload)
                : payload;
        }

        return fetch(url, fetchOptions);
    }

    window.toolApi = {
        getCsrfToken,
        jsonFetch,
    };
})();

