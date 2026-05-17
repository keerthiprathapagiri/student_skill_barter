# routes/auth.py
# Login, register, logout routes

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import DatabaseError, create_user, get_user_by_username, username_exists

auth_bp = Blueprint('auth', __name__)


# ── Register ──────────────────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name  = request.form.get('full_name', '').strip()
        username   = request.form.get('username', '').strip().lower()
        password   = request.form.get('password', '')
        confirm_pw = request.form.get('confirm_password', '')

        # --- Validation ---
        if not all([full_name, username, password, confirm_pw]):
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if password != confirm_pw:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        try:
            if username_exists(username):
                flash('Username already taken. Please choose another.', 'error')
                return render_template('register.html')

            # Hash password and create user
            hashed = generate_password_hash(password)
            user_id = create_user(full_name, username, hashed)

            if not user_id:
                flash('Unable to create account at this time. Please try again later.', 'error')
                return render_template('register.html')

            session['user_id'] = user_id
            session['username'] = username
            session['full_name'] = full_name
            flash('Account created! Welcome to Skill Barter 🎉', 'success')
            return redirect(url_for('main.index'))
        except DatabaseError as exc:
            msg = 'Database connection failed. Check your MySQL credentials and .env file.'
            details = str(getattr(exc, 'original', exc))
            if '1146' in details or "doesn't exist" in details:
                msg = 'Database schema is not initialized. Run database/schema.sql and make sure the users table exists.'
            flash(msg, 'error')
            return render_template('register.html')

    return render_template('register.html')


# ── Login ─────────────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')

        try:
            user = get_user_by_username(username)
        except DatabaseError as exc:
            msg = 'Database connection failed. Check your MySQL credentials and .env file.'
            details = str(getattr(exc, 'original', exc))
            if '1146' in details or "doesn't exist" in details:
                msg = 'Database schema is not initialized. Run database/schema.sql and make sure the users table exists.'
            flash(msg, 'error')
            return render_template('login.html')

        if user and check_password_hash(user['password'], password):
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            flash(f"Welcome back, {user['full_name']}!", 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


# ── Logout ────────────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
