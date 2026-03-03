from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.auth import login_required
from app.services.ticket_service import TicketService
from app.services.client_service import ClientService
from app.services.time_entry_service import TimeEntryService

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')
_tickets = TicketService()
_clients = ClientService()
_time_entries = TimeEntryService()


@tickets_bp.route('/')
@login_required
def index():
    client_id = int(request.args.get('client_id', 0) or 0)
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    tickets = _tickets.list(client_id=client_id, status=status, priority=priority)
    clients = _clients.list()
    return render_template('tickets/index.html', tickets=tickets, clients=clients,
                           client_id=client_id, status=status, priority=priority)


@tickets_bp.route('/new')
@login_required
def new():
    clients = _clients.list()
    client_id = int(request.args.get('client_id', 0) or 0)
    return render_template('tickets/new.html', clients=clients, client_id=client_id)


@tickets_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        new_id = _tickets.create(request.form)
        flash('Ticket created successfully.', 'success')
        return redirect(url_for('tickets.show', id=new_id))
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('tickets.new'))


@tickets_bp.route('/<int:id>')
@login_required
def show(id):
    ticket = _tickets.get(id)
    if not ticket:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('tickets.index'))
    entries = _time_entries.list_by_ticket(id)
    return render_template('tickets/show.html', ticket=ticket, entries=entries)


@tickets_bp.route('/<int:id>/edit')
@login_required
def edit(id):
    ticket = _tickets.get(id)
    if not ticket:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('tickets.index'))
    clients = _clients.list()
    return render_template('tickets/edit.html', ticket=ticket, clients=clients)


@tickets_bp.route('/<int:id>', methods=['POST'])
@login_required
def update(id):
    if request.form.get('_method', '').upper() != 'PUT':
        return redirect(url_for('tickets.index'))
    try:
        _tickets.update(id, request.form)
        flash('Ticket updated successfully.', 'success')
        return redirect(url_for('tickets.show', id=id))
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('tickets.edit', id=id))


@tickets_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    try:
        _tickets.delete(id)
        flash('Ticket deleted.', 'success')
    except Exception as e:
        flash(f'Cannot delete ticket: {e}', 'danger')
    return redirect(url_for('tickets.index'))
