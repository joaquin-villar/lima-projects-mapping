
// frontend/js/auth.js
window.Auth = (function () {
    let authToken = localStorage.getItem('litmap_token') || null;

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

    // Initialize listeners
    document.addEventListener('DOMContentLoaded', () => {
        const loginForm = document.getElementById('login-form');
        const cancelButton = document.getElementById('login-cancel');

        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const token = document.getElementById('login-token').value;
                if (token) {
                    authToken = token;
                    localStorage.setItem('litmap_token', token);
                    hideLoginPrompt();
                    // Optionally reload or retry the last failed request
                    location.reload(); // Simple way to ensure all states are reset
                }
            });
        }

        if (cancelButton) {
            cancelButton.addEventListener('click', hideLoginPrompt);
        }
    });

    return {
        getToken: () => authToken,
        setToken: (token) => {
            authToken = token;
            localStorage.setItem('litmap_token', token);
        },
        clearToken: () => {
            authToken = null;
            localStorage.removeItem('litmap_token');
        },
        showLoginPrompt,
        hideLoginPrompt
    };
})();
