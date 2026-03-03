import pytest
from app.services.client_service import ClientService


@pytest.fixture()
def svc():
    return ClientService()


class TestClientCreate:
    def test_create_and_get(self, svc):
        client_id = svc.create({"name": "Test Create Client", "email": "create@test.com"})
        try:
            client = svc.get(client_id)
            assert client is not None
            assert client["name"] == "Test Create Client"
            assert client["email"] == "create@test.com"
        finally:
            svc.delete(client_id)

    def test_create_with_all_fields(self, svc):
        client_id = svc.create({
            "name": "Full Client",
            "email": "full@test.com",
            "phone": "555-1234",
            "address": "123 Test St",
        })
        try:
            client = svc.get(client_id)
            assert client["phone"] == "555-1234"
            assert client["address"] == "123 Test St"
        finally:
            svc.delete(client_id)

    def test_create_requires_name(self, svc):
        with pytest.raises(ValueError, match="Client name is required"):
            svc.create({"name": "", "email": "x@x.com"})

    def test_create_blank_name_raises(self, svc):
        with pytest.raises(ValueError):
            svc.create({"name": "   "})

    def test_create_strips_whitespace(self, svc):
        client_id = svc.create({"name": "  Spacey Name  "})
        try:
            client = svc.get(client_id)
            assert client["name"] == "Spacey Name"
        finally:
            svc.delete(client_id)


class TestClientUpdate:
    def test_update(self, svc, sample_client):
        svc.update(sample_client["id"], {
            "name": "Updated Name",
            "email": "updated@test.com",
            "phone": "",
            "address": "",
        })
        client = svc.get(sample_client["id"])
        assert client["name"] == "Updated Name"
        assert client["email"] == "updated@test.com"

    def test_update_requires_name(self, svc, sample_client):
        with pytest.raises(ValueError, match="Client name is required"):
            svc.update(sample_client["id"], {"name": ""})


class TestClientDelete:
    def test_delete(self, svc):
        client_id = svc.create({"name": "To Delete"})
        svc.delete(client_id)
        assert svc.get(client_id) is None


class TestClientList:
    def test_list_returns_results(self, svc, sample_client):
        results = svc.list()
        assert len(results) > 0

    def test_list_search(self, svc, sample_client):
        results = svc.list(search="Pytest Client")
        assert any(c["id"] == sample_client["id"] for c in results)

    def test_list_search_no_match(self, svc):
        results = svc.list(search="zzz_nonexistent_zzz")
        assert len(results) == 0
