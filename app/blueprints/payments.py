from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.auth import login_required
from app.services.payment_service import PaymentService
from app.services.invoice_service import InvoiceService

payments_bp = Blueprint('payments', __name__)
_payments = PaymentService()
_invoices = InvoiceService()


@payments_bp.route('/invoices/<int:invoice_id>/payments/new')
@login_required
def new(invoice_id):
    invoice = _invoices.get(invoice_id)
    if not invoice:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('invoices.index'))
    balance_due = float(invoice['total_amount']) - float(invoice['total_paid'])
    return render_template('payments/new.html', invoice=invoice, balance_due=balance_due)


@payments_bp.route('/invoices/<int:invoice_id>/payments', methods=['POST'])
@login_required
def create(invoice_id):
    try:
        data = request.form.to_dict()
        data['invoice_id'] = invoice_id
        _payments.create(data)
        flash('Payment recorded successfully.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('invoices.show', id=invoice_id))


@payments_bp.route('/invoices/<int:invoice_id>/payments/<int:id>/delete', methods=['POST'])
@login_required
def delete(invoice_id, id):
    _payments.delete(id, invoice_id)
    flash('Payment deleted.', 'success')
    return redirect(url_for('invoices.show', id=invoice_id))
