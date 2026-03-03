import re
import pytest
from app.services.invoice_service import InvoiceService
from app.services.time_entry_service import TimeEntryService
from app.db import execute


@pytest.fixture()
def svc():
    return InvoiceService()


@pytest.fixture()
def time_svc():
    return TimeEntryService()


class TestGenerateNumber:
    def test_format(self, svc):
        number = svc.generate_number()
        assert re.match(r"^INV-\d{4}-\d{4}$", number)

    def test_starts_with_current_year(self, svc):
        number = svc.generate_number()
        import datetime
        year = datetime.date.today().year
        assert number.startswith(f"INV-{year}-")


class TestCreateFromTimeEntries:
    def test_creates_invoice_with_line_items(self, svc, sample_time_entry, sample_client):
        invoice_id = svc.create_from_time_entries(
            client_id=sample_client["id"],
            time_entry_ids=[sample_time_entry["id"]],
            invoice_date="2026-02-28",
            due_date="2026-03-30",
            notes="Test invoice",
        )
        try:
            invoice = svc.get(invoice_id)
            assert invoice is not None
            assert invoice["status"] == "draft"
            assert invoice["client_id"] == sample_client["id"]

            line_items = svc.get_line_items(invoice_id)
            assert len(line_items) == 1
            assert line_items[0]["time_entry_id"] == sample_time_entry["id"]

            expected_total = float(sample_time_entry["hours_worked"]) * float(sample_time_entry["hourly_rate"])
            assert float(invoice["total_amount"]) == pytest.approx(expected_total)
        finally:
            # Clean up line items first (foreign key), then invoice
            execute("DELETE FROM invoice_line_items WHERE invoice_id=%s", (invoice_id,))
            execute("DELETE FROM invoices WHERE id=%s", (invoice_id,))

    def test_empty_entries_raises(self, svc, sample_client):
        with pytest.raises(ValueError, match="Select at least one time entry"):
            svc.create_from_time_entries(
                client_id=sample_client["id"],
                time_entry_ids=[],
                invoice_date="2026-02-28",
                due_date="2026-03-30",
            )


class TestInvoiceStatusRecalculation:
    def test_draft_not_recalculated(self, svc, sample_time_entry, sample_client):
        """Draft invoices should keep their status even after recalculate."""
        invoice_id = svc.create_from_time_entries(
            client_id=sample_client["id"],
            time_entry_ids=[sample_time_entry["id"]],
            invoice_date="2026-02-28",
            due_date="2026-03-30",
        )
        try:
            svc.recalculate_status(invoice_id)
            invoice = svc.get(invoice_id)
            assert invoice["status"] == "draft"
        finally:
            execute("DELETE FROM invoice_line_items WHERE invoice_id=%s", (invoice_id,))
            execute("DELETE FROM invoices WHERE id=%s", (invoice_id,))

    def test_sent_becomes_paid_when_fully_paid(self, svc, sample_time_entry, sample_client):
        invoice_id = svc.create_from_time_entries(
            client_id=sample_client["id"],
            time_entry_ids=[sample_time_entry["id"]],
            invoice_date="2026-02-28",
            due_date="2026-03-30",
        )
        try:
            # Mark as sent
            svc.update_status(invoice_id, "sent")

            # Add a payment covering the full amount
            invoice = svc.get(invoice_id)
            total = float(invoice["total_amount"])
            execute(
                "INSERT INTO payments (invoice_id, payment_date, amount, method) "
                "VALUES (%s, %s, %s, %s)",
                (invoice_id, "2026-03-01", total, "check"),
            )

            svc.recalculate_status(invoice_id)
            invoice = svc.get(invoice_id)
            assert invoice["status"] == "paid"
        finally:
            execute("DELETE FROM payments WHERE invoice_id=%s", (invoice_id,))
            execute("DELETE FROM invoice_line_items WHERE invoice_id=%s", (invoice_id,))
            execute("DELETE FROM invoices WHERE id=%s", (invoice_id,))

    def test_sent_becomes_partial_when_partially_paid(self, svc, sample_time_entry, sample_client):
        invoice_id = svc.create_from_time_entries(
            client_id=sample_client["id"],
            time_entry_ids=[sample_time_entry["id"]],
            invoice_date="2026-02-28",
            due_date="2026-03-30",
        )
        try:
            svc.update_status(invoice_id, "sent")

            # Pay less than total
            execute(
                "INSERT INTO payments (invoice_id, payment_date, amount, method) "
                "VALUES (%s, %s, %s, %s)",
                (invoice_id, "2026-03-01", 1.00, "check"),
            )

            svc.recalculate_status(invoice_id)
            invoice = svc.get(invoice_id)
            assert invoice["status"] == "partial"
        finally:
            execute("DELETE FROM payments WHERE invoice_id=%s", (invoice_id,))
            execute("DELETE FROM invoice_line_items WHERE invoice_id=%s", (invoice_id,))
            execute("DELETE FROM invoices WHERE id=%s", (invoice_id,))


class TestInvoiceUpdate:
    def test_update(self, svc, sample_time_entry, sample_client):
        invoice_id = svc.create_from_time_entries(
            client_id=sample_client["id"],
            time_entry_ids=[sample_time_entry["id"]],
            invoice_date="2026-02-28",
            due_date="2026-03-30",
        )
        try:
            svc.update(invoice_id, {
                "invoice_date": "2026-03-01",
                "due_date": "2026-04-01",
                "notes": "Updated notes",
            })
            invoice = svc.get(invoice_id)
            assert str(invoice["invoice_date"]) == "2026-03-01"
            assert invoice["notes"] == "Updated notes"
        finally:
            execute("DELETE FROM invoice_line_items WHERE invoice_id=%s", (invoice_id,))
            execute("DELETE FROM invoices WHERE id=%s", (invoice_id,))


class TestInvoiceDelete:
    def test_delete(self, svc, sample_time_entry, sample_client):
        invoice_id = svc.create_from_time_entries(
            client_id=sample_client["id"],
            time_entry_ids=[sample_time_entry["id"]],
            invoice_date="2026-02-28",
            due_date="2026-03-30",
        )
        # Delete line items first, then the invoice
        execute("DELETE FROM invoice_line_items WHERE invoice_id=%s", (invoice_id,))
        svc.delete(invoice_id)
        assert svc.get(invoice_id) is None
