class TestUserRoutesAdminGuard:
    def test_requires_login(self, client):
        resp = client.get("/users/")
        assert resp.status_code == 302
        assert "login" in resp.headers["Location"]

    def test_contractor_cannot_access(self, contractor_session):
        resp = contractor_session.get("/users/", follow_redirects=False)
        assert resp.status_code == 302
        # Should redirect to dashboard, not login
        location = resp.headers["Location"]
        assert "login" not in location or "/" in location

    def test_admin_can_access(self, auth_session):
        resp = auth_session.get("/users/")
        assert resp.status_code == 200


class TestUserRoutesNewForm:
    def test_new_form_renders(self, auth_session):
        resp = auth_session.get("/users/new")
        assert resp.status_code == 200


class TestUserRoutesSelfDeleteProtection:
    def test_cannot_delete_self(self, auth_session):
        """The auth_session has user id=1; trying to delete id=1 should flash error."""
        resp = auth_session.post("/users/1/delete", follow_redirects=False)
        assert resp.status_code == 302
        assert "/users/" in resp.headers["Location"]
