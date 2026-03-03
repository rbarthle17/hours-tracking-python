from app.db import query, execute
from app.services.invoice_service import InvoiceService


class PaymentService:
    def __init__(self):
        self._invoice_service = InvoiceService()

    def list_by_invoice(self, invoice_id):
        return query(
            "SELECT id, invoice_id, payment_date, amount, method, reference_number, notes, created_at "
            "FROM payments WHERE invoice_id=%s ORDER BY payment_date DESC",
            (invoice_id,)
        )

    def create(self, data):
        if not data.get('amount') or float(data['amount']) <= 0:
            raise ValueError('Payment amount must be greater than zero.')
        payment_id = execute(
            "INSERT INTO payments (invoice_id, payment_date, amount, method, reference_number, notes) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (
                data['invoice_id'],
                data['payment_date'],
                float(data['amount']),
                data.get('method', 'other') or 'other',
                data.get('reference_number', '').strip() or None,
                data.get('notes', '').strip() or None,
            )
        )
        self._invoice_service.recalculate_status(data['invoice_id'])
        return payment_id

    def delete(self, payment_id, invoice_id):
        execute("DELETE FROM payments WHERE id=%s", (payment_id,))
        self._invoice_service.recalculate_status(invoice_id)
