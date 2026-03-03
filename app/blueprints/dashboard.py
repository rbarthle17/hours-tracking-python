from flask import Blueprint, render_template
from app.auth import login_required
from app.db import query_one, query

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    active_contracts = query_one(
        "SELECT COUNT(id) AS cnt FROM contracts WHERE status='active'"
    )
    hours_this_month = query_one(
        "SELECT COALESCE(SUM(hours_worked),0) AS total_hours FROM time_entries "
        "WHERE MONTH(entry_date)=MONTH(CURDATE()) AND YEAR(entry_date)=YEAR(CURDATE())"
    )
    outstanding_balance = query_one(
        "SELECT COALESCE(SUM(i.total_amount) - COALESCE(SUM(p.amount),0),0) AS balance "
        "FROM invoices i LEFT JOIN payments p ON i.id=p.invoice_id "
        "WHERE i.status IN ('sent','partial','overdue')"
    )
    monthly_revenue = query_one(
        "SELECT COALESCE(SUM(amount),0) AS revenue FROM payments "
        "WHERE MONTH(payment_date)=MONTH(CURDATE()) AND YEAR(payment_date)=YEAR(CURDATE())"
    )
    recent_entries = query(
        "SELECT te.id, te.entry_date, te.hours_worked, te.notes, "
        "       t.title AS ticket_title, t.id AS ticket_id, "
        "       cl.name AS client_name, "
        "       c.name AS contract_name, c.hourly_rate "
        "FROM time_entries te "
        "JOIN tickets t ON te.ticket_id=t.id "
        "JOIN contracts c ON te.contract_id=c.id "
        "JOIN clients cl ON t.client_id=cl.id "
        "ORDER BY te.entry_date DESC, te.created_at DESC LIMIT 10"
    )
    outstanding_invoices = query(
        "SELECT i.id, i.invoice_number, i.invoice_date, i.due_date, "
        "       i.total_amount, i.status, cl.name AS client_name, "
        "       COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id=i.id),0) AS total_paid "
        "FROM invoices i JOIN clients cl ON i.client_id=cl.id "
        "WHERE i.status IN ('sent','partial','overdue') ORDER BY i.due_date ASC"
    )
    return render_template('dashboard/index.html',
        active_contracts=active_contracts,
        hours_this_month=hours_this_month,
        outstanding_balance=outstanding_balance,
        monthly_revenue=monthly_revenue,
        recent_entries=recent_entries,
        outstanding_invoices=outstanding_invoices,
    )
