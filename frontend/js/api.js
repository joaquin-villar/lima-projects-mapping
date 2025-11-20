// frontend/js/api.js
window.Api = {
    async get(url) {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`GET ${url} -> ${res.status}`);
        return res.json();
    },

    async post(url, data) {
        const res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error(`POST ${url} -> ${res.status}`);
        return res.json();
    },

    // 🟢 ESTE ES EL MÉTODO QUE FALTABA
    async put(url, data) {
        const res = await fetch(url, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error(`PUT ${url} -> ${res.status}`);
        return res.json();
    },

    async del(url) {
        const res = await fetch(url, { method: "DELETE" });
        if (!res.ok) throw new Error(`DELETE ${url} -> ${res.status}`);
        return res.json();
    }
};