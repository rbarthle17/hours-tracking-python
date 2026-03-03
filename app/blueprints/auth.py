from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.auth_service import AuthService
from app.services.user_service import UserService

auth_bp = Blueprint('auth', __name__)
_auth = AuthService()
_users = UserService()


@auth_bp.route('/login', methods=['GET'])
def login_form():
    if 'user' in session:
        return redirect(url_for('dashboard.index'))
    return render_template('auth/login.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    user = _auth.authenticate(email, password)
    if not user:
        flash('Invalid email or password.', 'danger')
        return render_template('auth/login.html', email=email)

    _users.update_last_login(user['id'])
    session['user'] = {
        'id':         user['id'],
        'email':      user['email'],
        'first_name': user['first_name'],
        'last_name':  user['last_name'],
        'role':       user['role'],
    }
    return redirect(url_for('dashboard.index'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_form'))
