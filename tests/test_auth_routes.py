class TestLoginPage:
    def test_login_page_renders(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200
        assert b"login" in resp.data.lower() or b"Login" in resp.data

    def test_login_redirects_when_logged_in(self, auth_session):
        resp = auth_session.get("/login")
        assert resp.status_code == 302
        assert "/" in resp.headers["Location"]


class TestLoginPost:
    def test_invalid_credentials(self, client):
        resp = client.post("/login", data={
            "email": "bad@example.com",
            "password": "wrong",
        })
        # Should re-render login page (200) with flash message
        assert resp.status_code == 200
        assert b"Invalid" in resp.data

    def test_valid_credentials(self, client, test_user):
        resp = client.post("/login", data={
            "email": test_user["email"],
            "password": "testpass123",
        }, follow_redirects=False)
        assert resp.status_code == 302
        # Should redirect to dashboard
        assert "/" in resp.headers["Location"]


class TestLogout:
    def test_logout_clears_session(self, auth_session):
        resp = auth_session.get("/logout")
        assert resp.status_code == 302
        assert "login" in resp.headers["Location"]

        # Subsequent request should redirect to login
        resp = auth_session.get("/")
        assert resp.status_code == 302
        assert "login" in resp.headers["Location"]
