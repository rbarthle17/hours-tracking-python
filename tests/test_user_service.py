import pytest
from app.services.user_service import UserService


@pytest.fixture()
def svc():
    return UserService()


class TestUserCreate:
    def test_create_and_get(self, svc):
        user_id = svc.create({
            "email": "newuser-pytest@example.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "User",
            "role": "contractor",
            "is_active": "1",
        })
        try:
            user = svc.get(user_id)
            assert user is not None
            assert user["email"] == "newuser-pytest@example.com"
            assert user["first_name"] == "New"
            assert user["last_name"] == "User"
            assert user["role"] == "contractor"
        finally:
            svc.delete(user_id)

    def test_create_requires_email(self, svc):
        with pytest.raises(ValueError, match="Email is required"):
            svc.create({"email": "", "password": "x", "first_name": "A", "last_name": "B"})

    def test_create_requires_password(self, svc):
        with pytest.raises(ValueError, match="Password is required"):
            svc.create({"email": "a@b.com", "password": "", "first_name": "A", "last_name": "B"})

    def test_create_requires_first_name(self, svc):
        with pytest.raises(ValueError, match="First name is required"):
            svc.create({"email": "a@b.com", "password": "x", "first_name": "", "last_name": "B"})

    def test_create_requires_last_name(self, svc):
        with pytest.raises(ValueError, match="Last name is required"):
            svc.create({"email": "a@b.com", "password": "x", "first_name": "A", "last_name": ""})

    def test_create_admin_role(self, svc):
        user_id = svc.create({
            "email": "admin-pytest@example.com",
            "password": "pass",
            "first_name": "Admin",
            "last_name": "Test",
            "role": "admin",
            "is_active": "1",
        })
        try:
            user = svc.get(user_id)
            assert user["role"] == "admin"
        finally:
            svc.delete(user_id)

    def test_create_inactive_user(self, svc):
        user_id = svc.create({
            "email": "inactive-pytest@example.com",
            "password": "pass",
            "first_name": "Inactive",
            "last_name": "User",
            "is_active": "0",
        })
        try:
            user = svc.get(user_id)
            assert user["is_active"] == 0
        finally:
            svc.delete(user_id)


class TestUserList:
    def test_list_returns_results(self, svc, test_user):
        results = svc.list()
        assert len(results) > 0

    def test_list_search(self, svc, test_user):
        results = svc.list(search="Pytest")
        assert any(u["id"] == test_user["id"] for u in results)

    def test_list_search_by_email(self, svc, test_user):
        results = svc.list(search="pytest-testuser")
        assert any(u["id"] == test_user["id"] for u in results)


class TestUserGetByEmail:
    def test_found(self, svc, test_user):
        user = svc.get_by_email(test_user["email"])
        assert user is not None
        assert user["id"] == test_user["id"]

    def test_not_found(self, svc):
        user = svc.get_by_email("nonexistent@example.com")
        assert user is None


class TestUserUpdatePassword:
    def test_update_password(self, svc, test_user):
        """After updating password, the new password should work."""
        from app.services.auth_service import AuthService
        auth = AuthService()

        svc.update_password(test_user["id"], "newpassword456")
        user = svc.get_by_email(test_user["email"])
        assert auth.verify_password("newpassword456", user["password_hash"], user["salt"])

        # Restore original password for other tests
        svc.update_password(test_user["id"], "testpass123")


class TestUserDelete:
    def test_delete(self, svc):
        user_id = svc.create({
            "email": "todelete-pytest@example.com",
            "password": "pass",
            "first_name": "Del",
            "last_name": "Ete",
        })
        svc.delete(user_id)
        assert svc.get(user_id) is None
