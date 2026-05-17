// static/js/search.js
// Live skill search + render matching user cards on the home page

const searchInput   = document.getElementById('skillSearch');
const resultsGrid   = document.getElementById('searchResults');
const emptyState    = document.getElementById('searchEmpty');

let debounceTimer;

// ── Search on keyup ─────────────────────────────────────────────
searchInput?.addEventListener('keyup', (e) => {
    if (e.key === 'Enter') {
        searchSkills();
        return;
    }
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(searchSkills, 350);
});

// ── Triggered by button OR debounce ────────────────────────────
async function searchSkills() {
    const q = searchInput?.value?.trim();
    if (!q) {
        hideResults();
        return;
    }
    try {
        const res   = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
        const users = await res.json();
        renderResults(users);
    } catch (err) {
        console.error('Search error:', err);
    }
}

// ── Render card grid ────────────────────────────────────────────
function renderResults(users) {
    if (!resultsGrid) return;

    if (users.length === 0) {
        resultsGrid.style.display = 'none';
        emptyState.style.display  = 'block';
        return;
    }

    emptyState.style.display  = 'none';
    resultsGrid.style.display = 'grid';
    resultsGrid.innerHTML     = users.map(buildCard).join('');

    // Animate cards in
    resultsGrid.querySelectorAll('.user-card').forEach((card, i) => {
        card.style.opacity   = '0';
        card.style.transform = 'translateY(16px)';
        setTimeout(() => {
            card.style.transition = 'opacity .25s ease, transform .25s ease';
            card.style.opacity    = '1';
            card.style.transform  = 'translateY(0)';
        }, i * 60);
    });
}

function hideResults() {
    if (resultsGrid) resultsGrid.style.display = 'none';
    if (emptyState)  emptyState.style.display  = 'none';
}

// ── Build a single card HTML string ────────────────────────────
function buildCard(user) {
    const initials = (user.full_name || user.username || '?')[0].toUpperCase();
    const color    = user.avatar_color || '#4A90D9';

    const offeredTags = (user.offered_skills || []).slice(0, 3)
        .map(s => `<span class="skill-tag skill-offered">${escHtml(s)}</span>`).join('');
    const neededTags  = (user.needed_skills || []).slice(0, 3)
        .map(s => `<span class="skill-tag skill-needed">${escHtml(s)}</span>`).join('');
    const extraOff = (user.offered_skills || []).length > 3
        ? `<span class="skill-more">+${user.offered_skills.length - 3}</span>` : '';

    return `
    <div class="user-card">
        <div class="card-body">
            <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.5rem">
                <div class="card-avatar" style="background:${color}">${initials}</div>
                <div>
                    <h3>${escHtml(user.full_name)}</h3>
                    <p class="card-username">@${escHtml(user.username)}</p>
                </div>
            </div>
            ${user.bio ? `<p class="card-bio">${escHtml(user.bio.substring(0,80))}${user.bio.length>80?'…':''}</p>` : ''}
            <div class="card-skills">
                <div class="skill-row">
                    <span class="skill-label">Offers:</span>
                    ${offeredTags}${extraOff}
                </div>
                <div class="skill-row">
                    <span class="skill-label">Needs:</span>
                    ${neededTags}
                </div>
            </div>
            <div class="card-actions">
                <a href="/chat/${escHtml(user.username)}" class="btn-card btn-chat">💬 Chat</a>
                <a href="/user/${escHtml(user.username)}" class="btn-card btn-view">View</a>
            </div>
        </div>
    </div>`;
}

function escHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g,'&amp;')
        .replace(/</g,'&lt;')
        .replace(/>/g,'&gt;')
        .replace(/"/g,'&quot;');
}
