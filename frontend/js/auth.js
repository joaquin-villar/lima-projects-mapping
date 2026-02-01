
// frontend/js/auth.js
window.Auth = (function () {
    let authToken = sessionStorage.getItem('litmap_token') || null;
    let lastActivity = Date.now();
    const TIMEOUT_MS = 60 * 60 * 1000; // 60 minutes

    function parseJwt(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(function (c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            return JSON.parse(jsonPayload);
        } catch (e) {
            console.error("JWT Parse Error", e);
            return null;
        }
    }

    function updateStatusUI() {
        const container = document.getElementById('auth-status');
        if (!container) return;

        if (authToken) {
            const payload = parseJwt(authToken);
            const role = (payload && payload.role) ? payload.role.toUpperCase() : "EDITOR";

            container.innerHTML = `
                <div class="auth-user-badge">
                    <i data-lucide="shield-check" style="width: 14px; height: 14px;"></i>
                    Modo ${role}
                </div>
                <button id="auth-logout-btn" class="auth-logout-btn" title="Cerrar Sesión">
                    <i data-lucide="log-out" style="width: 16px; height: 16px;"></i>
                </button>
            `;
            document.getElementById('auth-logout-btn').onclick = () => {
                clearToken();
                location.reload();
            };
        } else {
            container.innerHTML = `
                <a id="auth-login-link" class="auth-login-link">
                    <i data-lucide="log-in" style="width: 14px; height: 14px; vertical-align: middle; margin-right: 4px;"></i>
                    Acceso Editor
                </a>
            `;
            document.getElementById('auth-login-link').onclick = () => showLoginPrompt();
        }

        if (window.lucide) lucide.createIcons();
    }

    function showLoginPrompt() {
        const modal = document.getElementById('login-modal');
        if (modal) {
            modal.classList.add('active');
            if (window.lucide) lucide.createIcons();
        }
    }

    function hideLoginPrompt() {
        const modal = document.getElementById('login-modal');
        if (modal) {
            modal.classList.remove('active');
            document.getElementById('login-error').style.display = 'none';
        }
    }

    function clearToken() {
        authToken = null;
        sessionStorage.removeItem('litmap_token');
        updateStatusUI();
    }

    // Inactivity check
    function checkTimeout() {
        if (authToken && (Date.now() - lastActivity > TIMEOUT_MS)) {
            console.log("Session timed out due to inactivity.");
            clearToken();
            alert("Tu sesión ha expirado por inactividad.");
            location.reload();
        }
    }

    // Activity tracker
    function resetActivity() {
        lastActivity = Date.now();
    }

    // Custom Confirmation Helper
    async function showConfirm(message) {
        return new Promise((resolve) => {
            const modal = document.getElementById('confirm-modal');
            const msgEl = document.getElementById('confirm-message');
            const okBtn = document.getElementById('confirm-ok-btn');
            const cancelBtn = document.getElementById('confirm-cancel-btn');
            const closeX = document.getElementById('confirm-cancel-x');

            msgEl.textContent = message;
            modal.classList.add('active');

            const cleanup = (result) => {
                modal.classList.remove('active');
                okBtn.onclick = null;
                cancelBtn.onclick = null;
                closeX.onclick = null;
                resolve(result);
            };

            okBtn.onclick = () => cleanup(true);
            cancelBtn.onclick = () => cleanup(false);
            closeX.onclick = () => cleanup(false);
        });
    }

    // Initial setup
    document.addEventListener('DOMContentLoaded', () => {
        const loginForm = document.getElementById('login-form');
        const loginCancel = document.getElementById('login-cancel');

        if (loginForm) {
            loginForm.onsubmit = (e) => {
                e.preventDefault();
                const token = document.getElementById('login-token').value;
                if (token) {
                    authToken = token;
                    sessionStorage.setItem('litmap_token', token);
                    hideLoginPrompt();
                    location.reload();
                }
            };
        }

        if (loginCancel) {
            loginCancel.onclick = hideLoginPrompt;
        }

        // Monitoring
        document.addEventListener('mousedown', resetActivity);
        document.addEventListener('keydown', resetActivity);
        setInterval(checkTimeout, 30000); // Check every 30s

        updateStatusUI();
    });

    return {
        getToken: () => authToken,
        setToken: (token) => {
            authToken = token;
            sessionStorage.setItem('litmap_token', token);
            updateStatusUI();
        },
        clearToken,
        showLoginPrompt,
        hideLoginPrompt,
        showConfirm
    };
})();
