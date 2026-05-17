// static/js/main.js
// Global utilities and navbar behavior

// ── Mobile menu toggle ─────────────────────────────────────────
function toggleMenu() {
    const menu = document.getElementById('mobileMenu');
    if (menu) menu.classList.toggle('open');
}

// ── Password visibility toggle ──────────────────────────────────
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    field.type = field.type === 'password' ? 'text' : 'password';
}

// ── Auto-dismiss flash messages after 5 s ───────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(f => {
        setTimeout(() => {
            f.style.opacity = '0';
            f.style.transform = 'translateX(120%)';
            f.style.transition = 'all .4s ease';
            setTimeout(() => f.remove(), 400);
        }, 5000);
    });
});
