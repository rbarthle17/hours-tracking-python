import hashlib
import uuid
from app.db import query_one, execute


class AuthService:
    def authenticate(self, email, password):
        """Verify credentials. Returns user dict or None."""
        user = query_one(
            "SELECT id, email, password_hash, salt, first_name, last_name, role, is_active "
            "FROM users WHERE email = %s",
            (email,)
        )
        if not user:
            return None
        if not user['is_active']:
            return None
        if self.verify_password(password, user['password_hash'], user['salt']):
            return user
        return None

    def hash_password(self, password, salt):
        """SHA-512 hash matching the CFML original: hash(salt & pw, "SHA-512")."""
        raw = (salt + password).encode('utf-8')
        return hashlib.sha512(raw).hexdigest().upper()

    def verify_password(self, password, hashed, salt):
        return self.hash_password(password, salt) == hashed.upper()

    def generate_salt(self):
        return str(uuid.uuid4()).upper()
