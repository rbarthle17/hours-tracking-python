import pytest
from app.services.ticket_service import TicketService


@pytest.fixture()
def svc():
    return TicketService()


class TestTicketCreate:
    def test_create_and_get(self, svc, sample_client):
        ticket_id = svc.create({
            "client_id": sample_client["id"],
            "title": "Test Ticket",
            "description": "A test ticket",
            "status": "open",
            "priority": "high",
        })
        try:
            ticket = svc.get(ticket_id)
            assert ticket is not None
            assert ticket["title"] == "Test Ticket"
            assert ticket["status"] == "open"
            assert ticket["priority"] == "high"
            assert ticket["client_name"] == sample_client["name"]
        finally:
            svc.delete(ticket_id)

    def test_create_requires_title(self, svc, sample_client):
        with pytest.raises(ValueError, match="Ticket title is required"):
            svc.create({"client_id": sample_client["id"], "title": ""})

    def test_create_defaults(self, svc, sample_client):
        """Status defaults to open, priority to medium."""
        ticket_id = svc.create({
            "client_id": sample_client["id"],
            "title": "Defaults Ticket",
        })
        try:
            ticket = svc.get(ticket_id)
            assert ticket["status"] == "open"
            assert ticket["priority"] == "medium"
        finally:
            svc.delete(ticket_id)


class TestTicketUpdate:
    def test_update(self, svc, sample_ticket, sample_client):
        svc.update(sample_ticket["id"], {
            "client_id": sample_client["id"],
            "title": "Updated Ticket",
            "description": "Updated desc",
            "status": "in_progress",
            "priority": "high",
        })
        ticket = svc.get(sample_ticket["id"])
        assert ticket["title"] == "Updated Ticket"
        assert ticket["status"] == "in_progress"
        assert ticket["priority"] == "high"


class TestTicketList:
    def test_list_all(self, svc, sample_ticket):
        results = svc.list()
        assert any(t["id"] == sample_ticket["id"] for t in results)

    def test_list_by_client(self, svc, sample_ticket, sample_client):
        results = svc.list(client_id=sample_client["id"])
        assert all(t["client_id"] == sample_client["id"] for t in results)

    def test_list_by_status(self, svc, sample_ticket):
        results = svc.list(status="open")
        assert all(t["status"] == "open" for t in results)

    def test_list_by_priority(self, svc, sample_ticket):
        results = svc.list(priority="medium")
        assert all(t["priority"] == "medium" for t in results)

    def test_list_by_client_method(self, svc, sample_ticket, sample_client):
        results = svc.list_by_client(sample_client["id"])
        assert any(t["id"] == sample_ticket["id"] for t in results)


class TestTicketDelete:
    def test_delete(self, svc, sample_client):
        ticket_id = svc.create({
            "client_id": sample_client["id"],
            "title": "To Delete",
        })
        svc.delete(ticket_id)
        assert svc.get(ticket_id) is None
