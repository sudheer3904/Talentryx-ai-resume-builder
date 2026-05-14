from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from functools import wraps
from app.database.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in as admin to access this page.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.feedback_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'resumebuilder' and password == 'Resumebuilder333':
            session['admin_logged_in'] = True
            flash('Successfully logged in as admin.', 'success')
            return redirect(url_for('admin.feedback_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('admin/admin_login.html')

@bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Successfully logged out.', 'info')
    return redirect(url_for('admin.login'))

@bp.route('/dashboard')
@admin_required
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Stats
    cursor.execute("SELECT COUNT(*) as count FROM users")
    total_users = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM resumes")
    total_resumes = cursor.fetchone()['count']
    
    # Users List with Resume Count
    cursor.execute("""
        SELECT u.id, u.username, u.email, COUNT(r.id) as resume_count, u.created_at
        FROM users u
        LEFT JOIN resumes r ON u.id = r.user_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)
    users = cursor.fetchall()
    
    return render_template('admin/dashboard.html', 
                           total_users=total_users, 
                           total_resumes=total_resumes,
                           users=users)

@bp.route('/feedback')
@admin_required
def feedback_dashboard():
    return render_template('admin/feedback.html')
