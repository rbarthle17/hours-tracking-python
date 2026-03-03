from app.db import query, query_one, execute
from app.services.auth_service import AuthService


class UserService:
    def __init__(self):
        self._auth = AuthService()

    def list(self, search=''):
        if search:
            return query(
                "SELECT id, email, first_name, last_name, role, is_active, last_login_at, created_at "
                "FROM users WHERE first_name LIKE %s OR last_name LIKE %s OR email LIKE %s "
                "ORDER BY last_name, first_name",
                (f'%{search}%', f'%{search}%', f'%{search}%')
            )
        return query(
            "SELECT id, email, first_name, last_name, role, is_active, last_login_at, created_at "
            "FROM users ORDER BY last_name, first_name"
        )

    def get(self, user_id):
        return query_one(
            "SELECT id, email, first_name, last_name, role, is_active, last_login_at, created_at "
            "FROM users WHERE id = %s",
            (user_id,)
        )

    def get_by_email(self, email):
        return query_one(
            "SELECT id, email, password_hash, salt, first_name, last_name, role, is_active "
            "FROM users WHERE email = %s",
            (email,)
        )

    def create(self, data):
        if not data.get('email', '').strip():
            raise ValueError('Email is required.')
        if not data.get('password', '').strip():
            raise ValueError('Password is required.')
        if not data.get('first_name', '').strip():
            raise ValueError('First name is required.')
        if not data.get('last_name', '').strip():
            raise ValueError('Last name is required.')

        salt = self._auth.generate_salt()
        password_hash = self._auth.hash_password(data['password'], salt)
        is_active = 1 if data.get('is_active') in (1, '1', True, 'on') else 0

        return execute(
            "INSERT INTO users (email, password_hash, salt, first_name, last_name, role, is_active) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                data['email'].strip(),
                password_hash,
                salt,
                data['first_name'].strip(),
                data['last_name'].strip(),
                data.get('role', 'contractor'),
                is_active,
            )
        )

    def update(self, user_id, data):
        is_active = 1 if data.get('is_active') in (1, '1', True, 'on') else 0
        execute(
            "UPDATE users SET email=%s, first_name=%s, last_name=%s, role=%s, is_active=%s "
            "WHERE id=%s",
            (
                data['email'].strip(),
                data['first_name'].strip(),
                data['last_name'].strip(),
                data.get('role', 'contractor'),
                is_active,
                user_id,
            )
        )

    def update_password(self, user_id, password):
        salt = self._auth.generate_salt()
        password_hash = self._auth.hash_password(password, salt)
        execute(
            "UPDATE users SET password_hash=%s, salt=%s WHERE id=%s",
            (password_hash, salt, user_id)
        )

    def update_last_login(self, user_id):
        execute(
            "UPDATE users SET last_login_at=NOW() WHERE id=%s",
            (user_id,)
        )

    def delete(self, user_id):
        execute("DELETE FROM users WHERE id=%s", (user_id,))
