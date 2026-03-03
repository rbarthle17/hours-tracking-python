from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.auth import login_required
from app.services.invoice_service import InvoiceService
from app.services.client_service import ClientService
from app.services.time_entry_service import TimeEntryService
from app.services.payment_service import PaymentService

invoices_bp = Blueprint('invoices', __name__, url_prefix='/invoices')
_invoices = InvoiceService()
_clients = ClientService()
_entries = TimeEntryService()
_payments = PaymentService()


@invoices_bp.route('/')
@login_required
def index():
    client_id = int(request.args.get('client_id', 0) or 0)
    status = request.args.get('status', '')
    invoices = _invoices.list(client_id=client_id, status=status)
    clients = _clients.list()
    return render_template('invoices/index.html', invoices=invoices, clients=clients,
                           client_id=client_id, status=status)


@invoices_bp.route('/new')
@login_required
def new():
    clients = _clients.list()
    client_id = int(request.args.get('client_id', 0) or 0)
    uninvoiced = _entries.get_uninvoiced(client_id=client_id) if client_id else []
    return render_template('invoices/new.html', clients=clients, client_id=client_id,
                           uninvoiced=uninvoiced)


@invoices_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        time_entry_ids = request.form.getlist('time_entry_ids')
        new_id = _invoices.create_from_time_entries(
            client_id=request.form['client_id'],
            time_entry_ids=[int(x) for x in time_entry_ids],
            invoice_date=request.form['invoice_date'],
            due_date=request.form['due_date'],
            notes=request.form.get('notes', ''),
        )
        flash('Invoice created successfully.', 'success')
        return redirect(url_for('invoices.show', id=new_id))
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('invoices.new'))


@invoices_bp.route('/<int:id>')
@login_required
def show(id):
    invoice = _invoices.get(id)
    if not invoice:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('invoices.index'))
    line_items = _invoices.get_line_items(id)
    payments = _payments.list_by_invoice(id)
    return render_template('invoices/show.html', invoice=invoice,
                           line_items=line_items, payments=payments)


@invoices_bp.route('/<int:id>/edit')
@login_required
def edit(id):
    invoice = _invoices.get(id)
    if not invoice:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('invoices.index'))
    if invoice['status'] != 'draft':
        flash('Only draft invoices can be edited.', 'danger')
        return redirect(url_for('invoices.show', id=id))
    return render_template('invoices/edit.html', invoice=invoice)


@invoices_bp.route('/<int:id>', methods=['POST'])
@login_required
def update(id):
    if request.form.get('_method', '').upper() != 'PUT':
        return redirect(url_for('invoices.index'))
    try:
        _invoices.update(id, request.form)
        flash('Invoice updated successfully.', 'success')
        return redirect(url_for('invoices.show', id=id))
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('invoices.edit', id=id))


@invoices_bp.route('/<int:id>/send', methods=['POST'])
@login_required
def send(id):
    _invoices.update_status(id, 'sent')
    flash('Invoice marked as sent.', 'success')
    return redirect(url_for('invoices.show', id=id))


@invoices_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    try:
        _invoices.delete(id)
        flash('Invoice deleted.', 'success')
    except Exception as e:
        flash(f'Cannot delete invoice: {e}', 'danger')
    return redirect(url_for('invoices.index'))
