import pytest
from app.services.payment_service import PaymentService
from app.services.invoice_service import InvoiceService
from app.db import execute


@pytest.fixture()
def pay_svc():
    return PaymentService()


@pytest.fixture()
def inv_svc():
    return InvoiceService()


@pytest.fixture()
def sample_invoice(inv_svc, sample_time_entry, sample_client):
    """Create a sent invoice for payment testing."""
    invoice_id = inv_svc.create_from_time_entries(
        client_id=sample_client["id"],
        time_entry_ids=[sample_time_entry["id"]],
        invoice_date="2026-02-28",
        due_date="2026-03-30",
    )
    inv_svc.update_status(invoice_id, "sent")
    yield inv_svc.get(invoice_id)
    # Cleanup
    execute("DELETE FROM payments WHERE invoice_id=%s", (invoice_id,))
    execute("DELETE FROM invoice_line_items WHERE invoice_id=%s", (invoice_id,))
    execute("DELETE FROM invoices WHERE id=%s", (invoice_id,))


class TestPaymentCreate:
    def test_create_payment(self, pay_svc, sample_invoice):
        payment_id = pay_svc.create({
            "invoice_id": sample_invoice["id"],
            "payment_date": "2026-03-01",
            "amount": "50.00",
            "method": "check",
            "reference_number": "CHK-001",
            "notes": "Test payment",
        })
        payments = pay_svc.list_by_invoice(sample_invoice["id"])
        assert any(p["id"] == payment_id for p in payments)
        payment = next(p for p in payments if p["id"] == payment_id)
        assert float(payment["amount"]) == 50.00
        assert payment["method"] == "check"

    def test_create_requires_positive_amount(self, pay_svc, sample_invoice):
        with pytest.raises(ValueError, match="greater than zero"):
            pay_svc.create({
                "invoice_id": sample_invoice["id"],
                "payment_date": "2026-03-01",
                "amount": "0",
            })

    def test_create_negative_amount_raises(self, pay_svc, sample_invoice):
        with pytest.raises(ValueError, match="greater than zero"):
            pay_svc.create({
                "invoice_id": sample_invoice["id"],
                "payment_date": "2026-03-01",
                "amount": "-10",
            })

    def test_full_payment_marks_invoice_paid(self, pay_svc, inv_svc, sample_invoice):
        total = float(sample_invoice["total_amount"])
        pay_svc.create({
            "invoice_id": sample_invoice["id"],
            "payment_date": "2026-03-01",
            "amount": str(total),
            "method": "wire",
        })
        invoice = inv_svc.get(sample_invoice["id"])
        assert invoice["status"] == "paid"

    def test_partial_payment_marks_invoice_partial(self, pay_svc, inv_svc, sample_invoice):
        pay_svc.create({
            "invoice_id": sample_invoice["id"],
            "payment_date": "2026-03-01",
            "amount": "1.00",
            "method": "other",
        })
        invoice = inv_svc.get(sample_invoice["id"])
        assert invoice["status"] == "partial"


class TestPaymentDelete:
    def test_delete_payment(self, pay_svc, sample_invoice):
        payment_id = pay_svc.create({
            "invoice_id": sample_invoice["id"],
            "payment_date": "2026-03-01",
            "amount": "25.00",
            "method": "check",
        })
        pay_svc.delete(payment_id, sample_invoice["id"])
        payments = pay_svc.list_by_invoice(sample_invoice["id"])
        assert not any(p["id"] == payment_id for p in payments)
