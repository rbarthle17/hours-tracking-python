import datetime
from app.helpers import format_currency, format_app_date, status_badge


class TestFormatCurrency:
    def test_none_returns_zero(self):
        assert format_currency(None) == "$0.00"

    def test_zero(self):
        assert format_currency(0) == "$0.00"

    def test_whole_number(self):
        assert format_currency(100) == "$100.00"

    def test_with_cents(self):
        assert format_currency(99.5) == "$99.50"

    def test_thousands_separator(self):
        assert format_currency(1234.56) == "$1,234.56"

    def test_large_number(self):
        assert format_currency(1000000) == "$1,000,000.00"

    def test_string_number(self):
        assert format_currency("250.75") == "$250.75"

    def test_negative(self):
        assert format_currency(-50) == "$-50.00"


class TestFormatAppDate:
    def test_none_returns_empty(self):
        assert format_app_date(None) == ""

    def test_date_object(self):
        assert format_app_date(datetime.date(2026, 1, 15)) == "Jan 15, 2026"

    def test_datetime_object(self):
        dt = datetime.datetime(2026, 3, 5, 10, 30)
        assert format_app_date(dt) == "Mar 05, 2026"

    def test_iso_string(self):
        assert format_app_date("2026-01-15") == "Jan 15, 2026"

    def test_iso_datetime_string(self):
        assert format_app_date("2026-12-25 14:30:00") == "Dec 25, 2026"

    def test_invalid_string_returned_as_is(self):
        assert format_app_date("not-a-date") == "not-a-date"


class TestStatusBadge:
    def test_active(self):
        result = str(status_badge("active"))
        assert "bg-success" in result
        assert "ACTIVE" in result

    def test_in_progress_underscored(self):
        result = str(status_badge("in_progress"))
        assert "IN PROGRESS" in result
        assert "bg-info" in result

    def test_draft(self):
        result = str(status_badge("draft"))
        assert "bg-light" in result
        assert "DRAFT" in result

    def test_overdue(self):
        result = str(status_badge("overdue"))
        assert "bg-danger" in result

    def test_unknown_gets_secondary(self):
        result = str(status_badge("unknown_status"))
        assert "bg-secondary" in result

    def test_returns_markup(self):
        result = status_badge("paid")
        assert "<span" in str(result)
        assert "badge" in str(result)
