import pytest
from app.services.time_entry_service import TimeEntryService


@pytest.fixture()
def svc():
    return TimeEntryService()


class TestTimeEntryCreate:
    def test_create_and_get(self, svc, sample_contract, sample_ticket, test_user):
        entry_id = svc.create({
            "ticket_id": sample_ticket["id"],
            "contract_id": sample_contract["id"],
            "user_id": test_user["id"],
            "entry_date": "2026-02-20",
            "hours_worked": "3.5",
            "notes": "Test entry",
        })
        try:
            entry = svc.get(entry_id)
            assert entry is not None
            assert float(entry["hours_worked"]) == 3.5
            assert entry["notes"] == "Test entry"
            assert entry["ticket_title"] == sample_ticket["title"]
            assert entry["contract_name"] == sample_contract["name"]
        finally:
            svc.delete(entry_id)

    def test_create_requires_hours(self, svc, sample_contract, sample_ticket, test_user):
        with pytest.raises(ValueError, match="Hours worked is required"):
            svc.create({
                "ticket_id": sample_ticket["id"],
                "contract_id": sample_contract["id"],
                "user_id": test_user["id"],
                "entry_date": "2026-02-20",
                "hours_worked": "",
            })


class TestTimeEntryUpdate:
    def test_update(self, svc, sample_time_entry, sample_contract, sample_ticket):
        svc.update(sample_time_entry["id"], {
            "ticket_id": sample_ticket["id"],
            "contract_id": sample_contract["id"],
            "entry_date": "2026-02-16",
            "hours_worked": "5.0",
            "notes": "Updated notes",
        })
        entry = svc.get(sample_time_entry["id"])
        assert float(entry["hours_worked"]) == 5.0
        assert entry["notes"] == "Updated notes"


class TestTimeEntryList:
    def test_list_all(self, svc, sample_time_entry):
        results = svc.list()
        assert any(e["id"] == sample_time_entry["id"] for e in results)

    def test_list_by_contract(self, svc, sample_time_entry, sample_contract):
        results = svc.list(contract_id=sample_contract["id"])
        assert all(e["contract_id"] == sample_contract["id"] for e in results)

    def test_list_by_ticket(self, svc, sample_time_entry, sample_ticket):
        results = svc.list(ticket_id=sample_ticket["id"])
        assert all(e["ticket_id"] == sample_ticket["id"] for e in results)

    def test_list_by_date_range(self, svc, sample_time_entry):
        results = svc.list(start_date="2026-02-01", end_date="2026-02-28")
        assert any(e["id"] == sample_time_entry["id"] for e in results)

    def test_list_by_contract_method(self, svc, sample_time_entry, sample_contract):
        results = svc.list_by_contract(sample_contract["id"])
        assert any(e["id"] == sample_time_entry["id"] for e in results)

    def test_list_by_ticket_method(self, svc, sample_time_entry, sample_ticket):
        results = svc.list_by_ticket(sample_ticket["id"])
        assert any(e["id"] == sample_time_entry["id"] for e in results)


class TestTimeEntryDelete:
    def test_delete(self, svc, sample_contract, sample_ticket, test_user):
        entry_id = svc.create({
            "ticket_id": sample_ticket["id"],
            "contract_id": sample_contract["id"],
            "user_id": test_user["id"],
            "entry_date": "2026-02-20",
            "hours_worked": "1.0",
        })
        svc.delete(entry_id)
        assert svc.get(entry_id) is None


class TestUninvoiced:
    def test_get_uninvoiced(self, svc, sample_time_entry):
        """A freshly created time entry should appear in uninvoiced list."""
        results = svc.get_uninvoiced()
        assert any(e["id"] == sample_time_entry["id"] for e in results)

    def test_get_uninvoiced_by_client(self, svc, sample_time_entry, sample_client):
        results = svc.get_uninvoiced(client_id=sample_client["id"])
        assert any(e["id"] == sample_time_entry["id"] for e in results)
