from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.auth import admin_required
from app.services.user_service import UserService

users_bp = Blueprint('users', __name__, url_prefix='/users')
_users = UserService()


@users_bp.route('/')
@admin_required
def index():
    search = request.args.get('search', '')
    users = _users.list(search=search)
    return render_template('users/index.html', users=users, search=search)


@users_bp.route('/new')
@admin_required
def new():
    return render_template('users/new.html')


@users_bp.route('/', methods=['POST'])
@admin_required
def create():
    try:
        _users.create(request.form)
        flash('User created successfully.', 'success')
        return redirect(url_for('users.index'))
    except Exception as e:
        flash(f'Error creating user: {e}', 'danger')
        return redirect(url_for('users.new'))


@users_bp.route('/<int:id>/edit')
@admin_required
def edit(id):
    user = _users.get(id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('users.index'))
    return render_template('users/edit.html', user=user)


@users_bp.route('/<int:id>', methods=['POST'])
@admin_required
def update(id):
    if request.form.get('_method', '').upper() != 'PUT':
        return redirect(url_for('users.index'))
    _users.update(id, request.form)
    if request.form.get('password', '').strip():
        _users.update_password(id, request.form['password'])
    flash('User updated successfully.', 'success')
    return redirect(url_for('users.index'))


@users_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    if id == session['user']['id']:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('users.index'))
    try:
        _users.delete(id)
        flash('User deleted.', 'success')
    except Exception as e:
        flash(f'Cannot delete user: {e}', 'danger')
    return redirect(url_for('users.index'))
