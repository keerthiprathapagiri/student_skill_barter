// static/js/register.js
// Client-side validation for the registration form

// ── Password strength ───────────────────────────────────────────
document.getElementById('password')?.addEventListener('input', function () {
    const val    = this.value;
    const fill   = document.getElementById('strengthFill');
    const label  = document.getElementById('strengthLabel');
    if (!fill) return;

    let score = 0;
    if (val.length >= 6)  score++;
    if (val.length >= 10) score++;
    if (/[A-Z]/.test(val)) score++;
    if (/[0-9]/.test(val)) score++;
    if (/[^A-Za-z0-9]/.test(val)) score++;

    const levels = [
        { w: '0%',   bg: 'transparent', text: '' },
        { w: '25%',  bg: '#F87171',     text: 'Weak' },
        { w: '50%',  bg: '#FBBF24',     text: 'Fair' },
        { w: '75%',  bg: '#60A5FA',     text: 'Good' },
        { w: '100%', bg: '#34D399',     text: 'Strong' },
    ];
    const level = levels[Math.min(score, 4)];
    fill.style.width      = level.w;
    fill.style.background = level.bg;
    label.textContent     = level.text;
    label.style.color     = level.bg;
});

// ── Password match ──────────────────────────────────────────────
function checkPasswordMatch() {
    const pw  = document.getElementById('password')?.value || '';
    const pw2 = document.getElementById('confirm_password')?.value || '';
    const msg = document.getElementById('matchMsg');
    if (!msg || !pw2) return;

    if (pw2.length === 0) {
        msg.textContent = '';
    } else if (pw === pw2) {
        msg.textContent = '✓ Passwords match';
        msg.className   = 'match-msg match-ok';
    } else {
        msg.textContent = '✗ Passwords do not match';
        msg.className   = 'match-msg match-err';
    }
}

// ── Username availability (debounced fetch) ─────────────────────
let usernameTimer;
function checkUsername(val) {
    const status = document.getElementById('usernameStatus');
    if (!status || val.length < 3) { status && (status.textContent = ''); return; }
    clearTimeout(usernameTimer);
    usernameTimer = setTimeout(async () => {
        try {
            const res  = await fetch(`/api/search?q=${encodeURIComponent(val)}`);
            // We abuse the search endpoint; a dedicated check would be cleaner.
            // For now just show a neutral indicator.
            status.textContent = val.length >= 3 ? '✓' : '';
            status.style.color = '#34D399';
        } catch {
            status.textContent = '';
        }
    }, 500);
}

// ── Prevent submit if passwords don't match ─────────────────────
document.getElementById('registerForm')?.addEventListener('submit', function (e) {
    const pw  = document.getElementById('password')?.value || '';
    const pw2 = document.getElementById('confirm_password')?.value || '';
    if (pw !== pw2) {
        e.preventDefault();
        const msg = document.getElementById('matchMsg');
        if (msg) {
            msg.textContent = '✗ Passwords do not match';
            msg.className   = 'match-msg match-err';
        }
        return;
    }
    // Show loader
    document.querySelector('.btn-text') && (document.querySelector('.btn-text').style.display = 'none');
    document.querySelector('.btn-loader') && (document.querySelector('.btn-loader').style.display = 'inline');
});
