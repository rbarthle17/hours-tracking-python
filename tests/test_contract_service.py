import pytest
from app.services.contract_service import ContractService


@pytest.fixture()
def svc():
    return ContractService()


class TestContractCreate:
    def test_create_and_get(self, svc, sample_client):
        contract_id = svc.create({
            "client_id": sample_client["id"],
            "name": "Test Contract",
            "hourly_rate": "125.00",
            "start_date": "2026-01-01",
            "status": "active",
        })
        try:
            contract = svc.get(contract_id)
            assert contract is not None
            assert contract["name"] == "Test Contract"
            assert float(contract["hourly_rate"]) == 125.00
            assert contract["client_name"] == sample_client["name"]
        finally:
            svc.delete(contract_id)

    def test_create_requires_name(self, svc, sample_client):
        with pytest.raises(ValueError, match="Contract name is required"):
            svc.create({
                "client_id": sample_client["id"],
                "name": "",
                "hourly_rate": "100",
                "start_date": "2026-01-01",
            })

    def test_create_requires_hourly_rate(self, svc, sample_client):
        with pytest.raises(ValueError, match="Hourly rate is required"):
            svc.create({
                "client_id": sample_client["id"],
                "name": "No Rate",
                "hourly_rate": "",
                "start_date": "2026-01-01",
            })


class TestContractUpdate:
    def test_update(self, svc, sample_contract, sample_client):
        svc.update(sample_contract["id"], {
            "client_id": sample_client["id"],
            "name": "Updated Contract",
            "hourly_rate": "200.00",
            "start_date": "2026-02-01",
            "end_date": "2026-12-31",
            "status": "paused",
        })
        contract = svc.get(sample_contract["id"])
        assert contract["name"] == "Updated Contract"
        assert float(contract["hourly_rate"]) == 200.00
        assert contract["status"] == "paused"


class TestContractList:
    def test_list_all(self, svc, sample_contract):
        results = svc.list()
        assert any(c["id"] == sample_contract["id"] for c in results)

    def test_list_by_client(self, svc, sample_contract, sample_client):
        results = svc.list(client_id=sample_client["id"])
        assert all(c["client_id"] == sample_client["id"] for c in results)

    def test_list_by_status(self, svc, sample_contract):
        results = svc.list(status="active")
        assert all(c["status"] == "active" for c in results)

    def test_list_by_client_method(self, svc, sample_contract, sample_client):
        results = svc.list_by_client(sample_client["id"])
        assert any(c["id"] == sample_contract["id"] for c in results)


class TestContractDelete:
    def test_delete(self, svc, sample_client):
        contract_id = svc.create({
            "client_id": sample_client["id"],
            "name": "To Delete",
            "hourly_rate": "50",
            "start_date": "2026-01-01",
        })
        svc.delete(contract_id)
        assert svc.get(contract_id) is None
