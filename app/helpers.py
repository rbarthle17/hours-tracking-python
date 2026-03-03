from markupsafe import Markup
from flask import session
import datetime


def format_currency(amount):
    """Format a number as US currency string."""
    if amount is None:
        amount = 0
    return '${:,.2f}'.format(float(amount))


def format_app_date(value):
    """Format a date value as 'Mon DD, YYYY'."""
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.date.fromisoformat(value[:10])
        except ValueError:
            return value
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.strftime('%b %d, %Y')
    return str(value)


def status_badge(status):
    """Return a Bootstrap badge HTML snippet for a status string."""
    classes = {
        'active':      'bg-success',
        'completed':   'bg-secondary',
        'paused':      'bg-warning text-dark',
        'draft':       'bg-light text-dark border',
        'sent':        'bg-info text-dark',
        'paid':        'bg-success',
        'partial':     'bg-warning text-dark',
        'overdue':     'bg-danger',
        'open':        'bg-primary',
        'in_progress': 'bg-info text-dark',
        'done':        'bg-success',
        'closed':      'bg-secondary',
        'low':         'bg-light text-dark border',
        'medium':      'bg-warning text-dark',
        'high':        'bg-danger',
        'admin':       'bg-danger',
        'contractor':  'bg-secondary',
    }
    badge_class = classes.get(status, 'bg-secondary')
    display = status.replace('_', ' ').upper()
    return Markup(f'<span class="badge {badge_class}">{display}</span>')


def is_admin():
    """Check if the current session user is an admin."""
    user = session.get('user', {})
    return user.get('role') == 'admin'


def is_logged_in():
    """Check if a user is in session."""
    return 'user' in session


def register_helpers(app):
    """Register all helpers as Jinja2 globals and filters."""
    app.jinja_env.globals.update(
        format_currency=format_currency,
        format_app_date=format_app_date,
        status_badge=status_badge,
        is_admin=is_admin,
        is_logged_in=is_logged_in,
    )
    app.jinja_env.filters['currency'] = format_currency
    app.jinja_env.filters['app_date'] = format_app_date
