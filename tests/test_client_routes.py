from app.db import execute


class TestClientRoutesAuthGuard:
    def test_index_requires_login(self, client):
        resp = client.get("/clients/")
        assert resp.status_code == 302
        assert "login" in resp.headers["Location"]

    def test_new_requires_login(self, client):
        resp = client.get("/clients/new")
        assert resp.status_code == 302

    def test_show_requires_login(self, client):
        resp = client.get("/clients/1")
        assert resp.status_code == 302


class TestClientIndex:
    def test_index_returns_200(self, auth_session):
        resp = auth_session.get("/clients/")
        assert resp.status_code == 200

    def test_index_with_search(self, auth_session):
        resp = auth_session.get("/clients/?search=test")
        assert resp.status_code == 200


class TestClientCreate:
    def test_create_redirects_to_show(self, auth_session):
        resp = auth_session.post("/clients/", data={
            "name": "Route Test Client",
            "email": "route@test.com",
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/clients/" in resp.headers["Location"]

        # Clean up — extract ID from redirect Location
        location = resp.headers["Location"]
        client_id = location.rstrip("/").split("/")[-1]
        execute("DELETE FROM clients WHERE id=%s", (client_id,))

    def test_create_with_empty_name_redirects(self, auth_session):
        resp = auth_session.post("/clients/", data={
            "name": "",
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "new" in resp.headers["Location"]


class TestClientShow:
    def test_show_existing(self, auth_session, sample_client):
        resp = auth_session.get(f"/clients/{sample_client['id']}")
        assert resp.status_code == 200
        assert sample_client["name"].encode() in resp.data

    def test_show_nonexistent(self, auth_session):
        resp = auth_session.get("/clients/999999")
        assert resp.status_code == 302
        assert "/clients/" in resp.headers["Location"]


class TestClientUpdate:
    def test_update_with_method_spoofing(self, auth_session, sample_client):
        resp = auth_session.post(f"/clients/{sample_client['id']}", data={
            "_method": "PUT",
            "name": "Route Updated Client",
            "email": "updated@route.com",
            "phone": "",
            "address": "",
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert f"/clients/{sample_client['id']}" in resp.headers["Location"]

    def test_update_without_method_spoof_redirects(self, auth_session, sample_client):
        resp = auth_session.post(f"/clients/{sample_client['id']}", data={
            "name": "Should Not Update",
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/clients/" in resp.headers["Location"]


class TestClientDelete:
    def test_delete_redirects_to_index(self, auth_session):
        # Create a client to delete
        from app.services.client_service import ClientService
        svc = ClientService()
        client_id = svc.create({"name": "To Delete Via Route"})

        resp = auth_session.post(f"/clients/{client_id}/delete", follow_redirects=False)
        assert resp.status_code == 302
        assert "/clients/" in resp.headers["Location"]

        # Verify deleted
        assert svc.get(client_id) is None
