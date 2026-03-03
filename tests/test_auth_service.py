import hashlib
import re
from app.services.auth_service import AuthService


class TestHashPassword:
    def setup_method(self):
        self.svc = AuthService()

    def test_produces_uppercase_hex(self):
        result = self.svc.hash_password("admin123", "SOME-SALT")
        assert result == result.upper()
        assert len(result) == 128  # SHA-512 hex = 128 chars

    def test_known_value(self):
        """Verify salt-first order: sha512(salt + password)."""
        salt = "TEST-SALT"
        password = "mypassword"
        expected = hashlib.sha512((salt + password).encode("utf-8")).hexdigest().upper()
        assert self.svc.hash_password(password, salt) == expected

    def test_different_salt_different_hash(self):
        h1 = self.svc.hash_password("password", "SALT-A")
        h2 = self.svc.hash_password("password", "SALT-B")
        assert h1 != h2

    def test_salt_first_not_password_first(self):
        """Ensure the order is salt+password, not password+salt."""
        salt = "SALT"
        password = "PASS"
        salt_first = hashlib.sha512((salt + password).encode("utf-8")).hexdigest().upper()
        pass_first = hashlib.sha512((password + salt).encode("utf-8")).hexdigest().upper()
        result = self.svc.hash_password(password, salt)
        assert result == salt_first
        assert result != pass_first


class TestVerifyPassword:
    def setup_method(self):
        self.svc = AuthService()

    def test_correct_password(self):
        salt = "MY-SALT-123"
        hashed = self.svc.hash_password("secret", salt)
        assert self.svc.verify_password("secret", hashed, salt) is True

    def test_wrong_password(self):
        salt = "MY-SALT-123"
        hashed = self.svc.hash_password("secret", salt)
        assert self.svc.verify_password("wrong", hashed, salt) is False

    def test_case_insensitive_hash_comparison(self):
        """The stored hash might be lower or mixed case; verify still works."""
        salt = "SALT"
        hashed = self.svc.hash_password("pass", salt)
        assert self.svc.verify_password("pass", hashed.lower(), salt) is True


class TestGenerateSalt:
    def setup_method(self):
        self.svc = AuthService()

    def test_returns_uppercase_string(self):
        salt = self.svc.generate_salt()
        assert salt == salt.upper()

    def test_uuid_format(self):
        salt = self.svc.generate_salt()
        uuid_pattern = re.compile(
            r"^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$"
        )
        assert uuid_pattern.match(salt)

    def test_unique_each_call(self):
        s1 = self.svc.generate_salt()
        s2 = self.svc.generate_salt()
        assert s1 != s2
