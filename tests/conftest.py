import pytest
from app import create_app
from app.db import execute, query_one
from app.services.auth_service import AuthService


@pytest.fixture(scope="session")
def app():
    """Create a Flask app instance for the entire test session."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture()
def auth_session(client):
    """A test client pre-loaded with an admin session."""
    with client.session_transaction() as sess:
        sess["user"] = {
            "id": 1,
            "email": "test-admin@example.com",
            "first_name": "Test",
            "last_name": "Admin",
            "role": "admin",
        }
    return client


@pytest.fixture()
def contractor_session(client):
    """A test client pre-loaded with a contractor (non-admin) session."""
    with client.session_transaction() as sess:
        sess["user"] = {
            "id": 2,
            "email": "test-contractor@example.com",
            "first_name": "Test",
            "last_name": "Contractor",
            "role": "contractor",
        }
    return client


# ---------------------------------------------------------------------------
# Test user (inserted once per session, cleaned up at the end)
# ---------------------------------------------------------------------------

_TEST_USER_EMAIL = "pytest-testuser@example.com"


@pytest.fixture(scope="session")
def test_user():
    """Insert a test user for the session and delete it when done."""
    auth = AuthService()
    salt = auth.generate_salt()
    password_hash = auth.hash_password("testpass123", salt)
    user_id = execute(
        "INSERT INTO users (email, password_hash, salt, first_name, last_name, role, is_active) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (_TEST_USER_EMAIL, password_hash, salt, "Pytest", "User", "contractor", 1),
    )
    user = query_one("SELECT * FROM users WHERE id=%s", (user_id,))
    yield user
    execute("DELETE FROM users WHERE id=%s", (user_id,))


# ---------------------------------------------------------------------------
# Shared data fixtures (create → yield → cleanup)
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_client():
    """Create a temporary client for testing, delete after."""
    from app.services.client_service import ClientService
    svc = ClientService()
    client_id = svc.create({"name": "Pytest Client", "email": "pytest@example.com"})
    client = svc.get(client_id)
    yield client
    try:
        svc.delete(client_id)
    except Exception:
        pass


@pytest.fixture()
def sample_contract(sample_client):
    """Create a temporary contract (needs a client), delete after."""
    from app.services.contract_service import ContractService
    svc = ContractService()
    contract_id = svc.create({
        "client_id": sample_client["id"],
        "name": "Pytest Contract",
        "hourly_rate": "150.00",
        "start_date": "2026-01-01",
        "status": "active",
    })
    contract = svc.get(contract_id)
    yield contract
    try:
        svc.delete(contract_id)
    except Exception:
        pass


@pytest.fixture()
def sample_ticket(sample_client):
    """Create a temporary ticket (needs a client), delete after."""
    from app.services.ticket_service import TicketService
    svc = TicketService()
    ticket_id = svc.create({
        "client_id": sample_client["id"],
        "title": "Pytest Ticket",
        "description": "Test ticket for pytest",
        "status": "open",
        "priority": "medium",
    })
    ticket = svc.get(ticket_id)
    yield ticket
    try:
        svc.delete(ticket_id)
    except Exception:
        pass


@pytest.fixture()
def sample_time_entry(sample_contract, sample_ticket, test_user):
    """Create a temporary time entry, delete after."""
    from app.services.time_entry_service import TimeEntryService
    svc = TimeEntryService()
    entry_id = svc.create({
        "ticket_id": sample_ticket["id"],
        "contract_id": sample_contract["id"],
        "user_id": test_user["id"],
        "entry_date": "2026-02-15",
        "hours_worked": "2.5",
        "notes": "Pytest time entry",
    })
    entry = svc.get(entry_id)
    yield entry
    try:
        svc.delete(entry_id)
    except Exception:
        pass
