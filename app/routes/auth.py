from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user import User
import functools

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password')
        error = None

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'

        if error is None:
            if User.create(username, email, password):
                flash('Registration successful! Please login.')
                return redirect(url_for('auth.login'))
            else:
                error = 'User already registered or error occurred.'

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        
        user = User.get_by_email(email)

        if user is None:
            error = 'Incorrect email.'
        elif not user.check_password(password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('resume.dashboard'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/forgot-password', methods=('GET', 'POST'))
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_password = request.form.get('confirm_password')
        error = None

        user = User.get_by_email(email)

        if user is None:
            error = 'If this email registered, a password reset would occur (for security, we just say incorrect email here but normally we say check email). Actually, Email not found.'
        elif not new_password:
            error = 'New password is required.'
        elif new_password != confirm_password:
            error = 'Passwords do not match.'

        if error is None:
            if user.update_password(new_password):
                flash('Password reset successful. Please login.')
                return redirect(url_for('auth.login'))
            else:
                error = 'Failed to reset password.'

        flash(error)

    return render_template('auth/forgot_password.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/profile', methods=('GET', 'POST'))
@login_required
def profile():
    # Only import User here if needed or use the already imported one (at the top)
    # The file already has: from app.models.user import User
    user = User.get_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password:
            flash('New password cannot be empty.')
        elif new_password != confirm_password:
            flash('Passwords do not match.')
        else:
            if user.update_password(new_password):
                flash('Password successfully updated.')
            else:
                flash('Failed to update password. Please try again.')
                
    return render_template('auth/profile.html', user=user)
