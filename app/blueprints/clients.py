from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.auth import login_required
from app.services.client_service import ClientService
from app.services.contract_service import ContractService
from app.services.ticket_service import TicketService

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')
_clients = ClientService()
_contracts = ContractService()
_tickets = TicketService()


@clients_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '')
    clients = _clients.list(search=search)
    return render_template('clients/index.html', clients=clients, search=search)


@clients_bp.route('/new')
@login_required
def new():
    return render_template('clients/new.html')


@clients_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        new_id = _clients.create(request.form)
        flash('Client created successfully.', 'success')
        return redirect(url_for('clients.show', id=new_id))
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('clients.new'))


@clients_bp.route('/<int:id>')
@login_required
def show(id):
    client = _clients.get(id)
    if not client:
        flash('Client not found.', 'danger')
        return redirect(url_for('clients.index'))
    contracts = _contracts.list_by_client(id)
    tickets = _tickets.list_by_client(id)
    return render_template('clients/show.html', client=client, contracts=contracts, tickets=tickets)


@clients_bp.route('/<int:id>/edit')
@login_required
def edit(id):
    client = _clients.get(id)
    if not client:
        flash('Client not found.', 'danger')
        return redirect(url_for('clients.index'))
    return render_template('clients/edit.html', client=client)


@clients_bp.route('/<int:id>', methods=['POST'])
@login_required
def update(id):
    if request.form.get('_method', '').upper() != 'PUT':
        return redirect(url_for('clients.index'))
    try:
        _clients.update(id, request.form)
        flash('Client updated successfully.', 'success')
        return redirect(url_for('clients.show', id=id))
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('clients.edit', id=id))


@clients_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    try:
        _clients.delete(id)
        flash('Client deleted.', 'success')
    except Exception as e:
        flash(f'Cannot delete client: {e}', 'danger')
    return redirect(url_for('clients.index'))
