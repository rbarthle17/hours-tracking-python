class TestDashboard:
    def test_requires_login(self, client):
        resp = client.get("/")
        assert resp.status_code == 302
        assert "login" in resp.headers["Location"]

    def test_renders_for_logged_in_user(self, auth_session):
        resp = auth_session.get("/")
        assert resp.status_code == 200
        # Dashboard should contain key sections
        assert b"dashboard" in resp.data.lower() or b"Dashboard" in resp.data
