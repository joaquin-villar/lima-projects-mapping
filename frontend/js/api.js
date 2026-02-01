// frontend/js/api.js
window.Api = {
    async request(url, options = {}) {
        const token = window.Auth ? window.Auth.getToken() : null;

        const headers = {
            "Content-Type": "application/json",
            ...options.headers
        };

        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        const res = await fetch(url, { ...options, headers });

        if (res.status === 401 || res.status === 403) {
            if (window.Auth) {
                window.Auth.showLoginPrompt();
            }
            throw new Error(`Auth Error: ${res.status}`);
        }

        if (!res.ok) {
            let errorDetail = "";
            try {
                const errorData = await res.json();
                errorDetail = errorData.detail || errorData.message || JSON.stringify(errorData);
            } catch (e) {
                errorDetail = await res.text();
            }
            throw new Error(`HTTP ${res.status}: ${errorDetail || res.statusText}`);
        }

        const text = await res.text();
        if (!text) return {};

        try {
            return JSON.parse(text);
        } catch (e) {
            console.error("JSON parse error on response:", text);
            return { text: text }; // Return as text if not JSON
        }
    },

    async get(url) {
        return this.request(url, { method: "GET" });
    },

    async post(url, data) {
        return this.request(url, {
            method: "POST",
            body: JSON.stringify(data)
        });
    },

    async put(url, data) {
        return this.request(url, {
            method: "PUT",
            body: JSON.stringify(data)
        });
    },

    async del(url) {
        return this.request(url, { method: "DELETE" });
    }
};