from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.auth import login_required
from app.services.time_entry_service import TimeEntryService
from app.services.ticket_service import TicketService
from app.services.contract_service import ContractService
from app.services.client_service import ClientService

timeentries_bp = Blueprint('timeentries', __name__, url_prefix='/timeentries')
_entries = TimeEntryService()
_tickets = TicketService()
_contracts = ContractService()
_clients = ClientService()


@timeentries_bp.route('/')
@login_required
def index():
    client_id = int(request.args.get('client_id', 0) or 0)
    contract_id = int(request.args.get('contract_id', 0) or 0)
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    entries = _entries.list(client_id=client_id, contract_id=contract_id,
                            start_date=start_date, end_date=end_date)
    clients = _clients.list()
    contracts = _contracts.get_active_contracts()
    return render_template('timeentries/index.html', entries=entries, clients=clients,
                           contracts=contracts, client_id=client_id, contract_id=contract_id,
                           start_date=start_date, end_date=end_date)


@timeentries_bp.route('/new')
@login_required
def new():
    tickets = _tickets.get_active_tickets()
    contracts = _contracts.get_active_contracts()
    return render_template('timeentries/new.html', tickets=tickets, contracts=contracts)


@timeentries_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        data = request.form.to_dict()
        data['user_id'] = session['user']['id']
        new_id = _entries.create(data)
        flash('Time entry logged successfully.', 'success')
        return redirect(url_for('timeentries.show', id=new_id))
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('timeentries.new'))


@timeentries_bp.route('/<int:id>')
@login_required
def show(id):
    entry = _entries.get(id)
    if not entry:
        flash('Time entry not found.', 'danger')
        return redirect(url_for('timeentries.index'))
    return render_template('timeentries/show.html', entry=entry)


@timeentries_bp.route('/<int:id>/edit')
@login_required
def edit(id):
    entry = _entries.get(id)
    if not entry:
        flash('Time entry not found.', 'danger')
        return redirect(url_for('timeentries.index'))
    tickets = _tickets.get_active_tickets()
    contracts = _contracts.get_active_contracts()
    return render_template('timeentries/edit.html', entry=entry, tickets=tickets, contracts=contracts)


@timeentries_bp.route('/<int:id>', methods=['POST'])
@login_required
def update(id):
    if request.form.get('_method', '').upper() != 'PUT':
        return redirect(url_for('timeentries.index'))
    try:
        _entries.update(id, request.form)
        flash('Time entry updated successfully.', 'success')
        return redirect(url_for('timeentries.show', id=id))
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('timeentries.edit', id=id))


@timeentries_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    try:
        _entries.delete(id)
        flash('Time entry deleted.', 'success')
    except Exception as e:
        flash(f'Cannot delete time entry: {e}', 'danger')
    return redirect(url_for('timeentries.index'))
