from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.auth import login_required
from app.services.contract_service import ContractService
from app.services.client_service import ClientService
from app.services.time_entry_service import TimeEntryService

contracts_bp = Blueprint('contracts', __name__, url_prefix='/contracts')
_contracts = ContractService()
_clients = ClientService()
_time_entries = TimeEntryService()


@contracts_bp.route('/')
@login_required
def index():
    client_id = int(request.args.get('client_id', 0) or 0)
    status = request.args.get('status', '')
    contracts = _contracts.list(client_id=client_id, status=status)
    clients = _clients.list()
    return render_template('contracts/index.html', contracts=contracts, clients=clients,
                           client_id=client_id, status=status)


@contracts_bp.route('/new')
@login_required
def new():
    clients = _clients.list()
    client_id = int(request.args.get('client_id', 0) or 0)
    return render_template('contracts/new.html', clients=clients, client_id=client_id)


@contracts_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        new_id = _contracts.create(request.form)
        flash('Contract created successfully.', 'success')
        return redirect(url_for('contracts.show', id=new_id))
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('contracts.new'))


@contracts_bp.route('/<int:id>')
@login_required
def show(id):
    contract = _contracts.get(id)
    if not contract:
        flash('Contract not found.', 'danger')
        return redirect(url_for('contracts.index'))
    entries = _time_entries.list_by_contract(id)
    return render_template('contracts/show.html', contract=contract, entries=entries)


@contracts_bp.route('/<int:id>/edit')
@login_required
def edit(id):
    contract = _contracts.get(id)
    if not contract:
        flash('Contract not found.', 'danger')
        return redirect(url_for('contracts.index'))
    clients = _clients.list()
    return render_template('contracts/edit.html', contract=contract, clients=clients)


@contracts_bp.route('/<int:id>', methods=['POST'])
@login_required
def update(id):
    if request.form.get('_method', '').upper() != 'PUT':
        return redirect(url_for('contracts.index'))
    try:
        _contracts.update(id, request.form)
        flash('Contract updated successfully.', 'success')
        return redirect(url_for('contracts.show', id=id))
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('contracts.edit', id=id))


@contracts_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    try:
        _contracts.delete(id)
        flash('Contract deleted.', 'success')
    except Exception as e:
        flash(f'Cannot delete contract: {e}', 'danger')
    return redirect(url_for('contracts.index'))
