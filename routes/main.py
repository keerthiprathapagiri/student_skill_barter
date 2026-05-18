# routes/main.py
# Home, profile, skill management, search

from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, flash, jsonify)
from models.user    import get_user_by_id, update_bio
from models.skill   import (add_skill, delete_skill, get_skills_for_user,
                             search_users_by_skill, get_suggested_matches)
from models.progress import get_my_learning, get_my_teaching
from models.message  import get_unread_count

main_bp = Blueprint('main', __name__)


def login_required(f):
    """Simple decorator – redirect to login if not authenticated."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'info')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


# ── Home / Index ──────────────────────────────────────────────────────────────
@main_bp.route('/')
def index():
    user = None
    skills = {}
    matches = []
    unread = 0

    if 'user_id' in session:
        user_obj = get_user_by_id(session['user_id'])
        user = user_obj.to_dict() if user_obj else None
        skills = get_skills_for_user(session['user_id'])
        matches = get_suggested_matches(session['user_id'])
        unread = get_unread_count(session['user_id'])

    return render_template('index.html',
                           user=user,
                           skills=skills,
                           matches=matches,
                           unread=unread)


# ── Profile ───────────────────────────────────────────────────────────────────
@main_bp.route('/profile')
@login_required
def profile():
    user_obj = get_user_by_id(session['user_id'])
    user = user_obj.to_dict() if user_obj else None
    skills   = get_skills_for_user(session['user_id'])
    learning = get_my_learning(session['user_id'])
    teaching = get_my_teaching(session['user_id'])
    unread   = get_unread_count(session['user_id'])
    return render_template('profile.html',
                           user=user,
                           skills=skills,
                           learning=learning,
                           teaching=teaching,
                           unread=unread)


# ── Update bio ────────────────────────────────────────────────────────────────
@main_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    bio = request.form.get('bio', '').strip()
    update_bio(session['user_id'], bio)
    flash('Profile updated!', 'success')
    return redirect(url_for('main.profile'))


# ── Add skill ─────────────────────────────────────────────────────────────────
@main_bp.route('/skills/add', methods=['POST'])
@login_required
def add_skill_route():
    skill_name = request.form.get('skill_name', '').strip()
    skill_type = request.form.get('skill_type', '')
    if skill_name and skill_type in ('offered', 'needed'):
        add_skill(session['user_id'], skill_name, skill_type)
        flash(f'Skill "{skill_name}" added!', 'success')
    else:
        flash('Invalid skill data.', 'error')

    # Return to wherever we came from
    next_page = request.form.get('next', url_for('main.profile'))
    return redirect(next_page)


# ── Delete skill ──────────────────────────────────────────────────────────────
@main_bp.route('/skills/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill_route(skill_id):
    delete_skill(skill_id, session['user_id'])
    flash('Skill removed.', 'info')
    return redirect(url_for('main.profile'))


# ── Search API (JSON) ─────────────────────────────────────────────────────────
@main_bp.route('/api/search')
def api_search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    exclude = session.get('user_id')
    results = search_users_by_skill(query, exclude_user_id=exclude)
    return jsonify(results)


# ── Suggested matches API (JSON) ──────────────────────────────────────────────
@main_bp.route('/api/matches')
@login_required
def api_matches():
    matches = get_suggested_matches(session['user_id'])
    return jsonify(matches)


# ── View another user's public profile ───────────────────────────────────────
@main_bp.route('/user/<username>')
def view_user(username):
    from models.user import get_user_by_username
    target_obj = get_user_by_username(username)
    if not target_obj:
        flash('User not found.', 'error')
        return redirect(url_for('main.index'))
    target = target_obj.to_dict()
    skills = get_skills_for_user(target_obj.id)
    current_user_obj = get_user_by_id(session['user_id']) if 'user_id' in session else None
    current_user = current_user_obj.to_dict() if current_user_obj else None
    unread = get_unread_count(session['user_id']) if 'user_id' in session else 0
    return render_template('user_profile.html',
                           target=target,
                           skills=skills,
                           current_user=current_user,
                           unread=unread)


# ── Contact page ──────────────────────────────────────────────────────────────
@main_bp.route('/contact')
def contact():
    user_obj = get_user_by_id(session['user_id']) if 'user_id' in session else None
    user = user_obj.to_dict() if user_obj else None
    unread = get_unread_count(session['user_id']) if 'user_id' in session else 0
    return render_template('contact.html', user=user, unread=unread)


# ── Update learning progress (AJAX-friendly POST) ─────────────────────────────
@main_bp.route('/progress/update', methods=['POST'])
@login_required
def update_progress():
    """
    Update or create a learning progress record.
    Expects JSON body: {teacher_id, skill_name, progress_pct, notes}
    """
    from models.progress import upsert_progress
    data = request.get_json(silent=True) or request.form

    teacher_id   = data.get('teacher_id')
    skill_name   = data.get('skill_name', '').strip()
    progress_pct = int(data.get('progress_pct', 0))
    notes        = data.get('notes', '').strip()

    if not teacher_id or not skill_name:
        return jsonify({'ok': False, 'error': 'Missing fields'}), 400

    upsert_progress(session['user_id'], int(teacher_id), skill_name, progress_pct, notes)
    return jsonify({'ok': True})


# ── Error handlers ────────────────────────────────────────────────────────────
from flask import Blueprint

@main_bp.app_errorhandler(404)
def not_found(e):
    user_obj = get_user_by_id(session['user_id']) if 'user_id' in session else None
    user = user_obj.to_dict() if user_obj else None
    unread = get_unread_count(session['user_id']) if 'user_id' in session else 0
    return render_template('404.html', user=user, unread=unread), 404


@main_bp.app_errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
