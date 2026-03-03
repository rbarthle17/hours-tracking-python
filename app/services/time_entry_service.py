from app.db import query, query_one, execute


class TimeEntryService:
    def list(self, client_id=0, contract_id=0, ticket_id=0, start_date='', end_date=''):
        sql = (
            "SELECT te.id, te.ticket_id, te.contract_id, te.user_id, te.entry_date, "
            "       te.hours_worked, te.notes, te.created_at, "
            "       t.title AS ticket_title, t.client_id, "
            "       cl.name AS client_name, "
            "       c.name AS contract_name, c.hourly_rate, "
            "       CONCAT(u.first_name,' ',u.last_name) AS user_name "
            "FROM time_entries te "
            "JOIN tickets t ON te.ticket_id = t.id "
            "JOIN clients cl ON t.client_id = cl.id "
            "JOIN contracts c ON te.contract_id = c.id "
            "JOIN users u ON te.user_id = u.id "
            "WHERE 1=1"
        )
        params = []
        if client_id:
            sql += " AND t.client_id=%s"
            params.append(client_id)
        if contract_id:
            sql += " AND te.contract_id=%s"
            params.append(contract_id)
        if ticket_id:
            sql += " AND te.ticket_id=%s"
            params.append(ticket_id)
        if start_date:
            sql += " AND te.entry_date>=%s"
            params.append(start_date)
        if end_date:
            sql += " AND te.entry_date<=%s"
            params.append(end_date)
        sql += " ORDER BY te.entry_date DESC, te.created_at DESC"
        return query(sql, params)

    def list_by_ticket(self, ticket_id):
        return query(
            "SELECT te.id, te.entry_date, te.hours_worked, te.notes, "
            "       c.name AS contract_name, c.hourly_rate, "
            "       CONCAT(u.first_name,' ',u.last_name) AS user_name "
            "FROM time_entries te "
            "JOIN contracts c ON te.contract_id = c.id "
            "JOIN users u ON te.user_id = u.id "
            "WHERE te.ticket_id=%s ORDER BY te.entry_date DESC",
            (ticket_id,)
        )

    def list_by_contract(self, contract_id):
        return query(
            "SELECT te.id, te.entry_date, te.hours_worked, te.notes, "
            "       t.title AS ticket_title, "
            "       CONCAT(u.first_name,' ',u.last_name) AS user_name "
            "FROM time_entries te "
            "JOIN tickets t ON te.ticket_id = t.id "
            "JOIN users u ON te.user_id = u.id "
            "WHERE te.contract_id=%s ORDER BY te.entry_date DESC",
            (contract_id,)
        )

    def get(self, entry_id):
        return query_one(
            "SELECT te.id, te.ticket_id, te.contract_id, te.user_id, te.entry_date, "
            "       te.hours_worked, te.notes, "
            "       t.title AS ticket_title, t.client_id, "
            "       cl.name AS client_name, "
            "       c.name AS contract_name, c.hourly_rate, "
            "       CONCAT(u.first_name,' ',u.last_name) AS user_name "
            "FROM time_entries te "
            "JOIN tickets t ON te.ticket_id = t.id "
            "JOIN clients cl ON t.client_id = cl.id "
            "JOIN contracts c ON te.contract_id = c.id "
            "JOIN users u ON te.user_id = u.id "
            "WHERE te.id=%s",
            (entry_id,)
        )

    def get_uninvoiced(self, client_id=0):
        sql = (
            "SELECT te.id, te.entry_date, te.hours_worked, te.notes, "
            "       t.title AS ticket_title, t.client_id, "
            "       c.id AS contract_id, c.name AS contract_name, c.hourly_rate "
            "FROM time_entries te "
            "JOIN tickets t ON te.ticket_id = t.id "
            "JOIN contracts c ON te.contract_id = c.id "
            "WHERE te.id NOT IN ("
            "    SELECT COALESCE(time_entry_id,0) FROM invoice_line_items WHERE time_entry_id IS NOT NULL"
            ")"
        )
        params = []
        if client_id:
            sql += " AND t.client_id=%s"
            params.append(client_id)
        sql += " ORDER BY te.entry_date ASC"
        return query(sql, params)

    def create(self, data):
        if not data.get('hours_worked'):
            raise ValueError('Hours worked is required.')
        return execute(
            "INSERT INTO time_entries (ticket_id, contract_id, user_id, entry_date, hours_worked, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                data['ticket_id'],
                data['contract_id'],
                data['user_id'],
                data['entry_date'],
                float(data['hours_worked']),
                data.get('notes', '').strip() or None,
            )
        )

    def update(self, entry_id, data):
        execute(
            "UPDATE time_entries SET ticket_id=%s, contract_id=%s, entry_date=%s, "
            "hours_worked=%s, notes=%s WHERE id=%s",
            (
                data['ticket_id'],
                data['contract_id'],
                data['entry_date'],
                float(data['hours_worked']),
                data.get('notes', '').strip() or None,
                entry_id,
            )
        )

    def delete(self, entry_id):
        execute("DELETE FROM time_entries WHERE id=%s", (entry_id,))
