from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """Decorator that redirects to login if no user in session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login_form'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator that requires admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login_form'))
        if session['user'].get('role') != 'admin':
            flash('You do not have permission to access that page.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated
