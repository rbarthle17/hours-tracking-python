from app.db import query, query_one, execute


class TicketService:
    def list(self, client_id=0, status='', priority=''):
        sql = (
            "SELECT t.id, t.client_id, t.title, t.description, t.status, t.priority, "
            "       t.created_at, t.updated_at, cl.name AS client_name "
            "FROM tickets t JOIN clients cl ON t.client_id = cl.id WHERE 1=1"
        )
        params = []
        if client_id:
            sql += " AND t.client_id=%s"
            params.append(client_id)
        if status:
            sql += " AND t.status=%s"
            params.append(status)
        if priority:
            sql += " AND t.priority=%s"
            params.append(priority)
        sql += " ORDER BY cl.name, FIELD(t.priority,'high','medium','low'), t.title"
        return query(sql, params)

    def list_by_client(self, client_id):
        return query(
            "SELECT id, title, status, priority FROM tickets WHERE client_id=%s ORDER BY title",
            (client_id,)
        )

    def get_active_tickets(self):
        return query(
            "SELECT t.id, t.title, t.status, cl.name AS client_name "
            "FROM tickets t JOIN clients cl ON t.client_id = cl.id "
            "WHERE t.status IN ('open','in_progress') ORDER BY cl.name, t.title"
        )

    def get(self, ticket_id):
        return query_one(
            "SELECT t.id, t.client_id, t.title, t.description, t.status, t.priority, "
            "       t.created_at, t.updated_at, cl.name AS client_name "
            "FROM tickets t JOIN clients cl ON t.client_id = cl.id WHERE t.id=%s",
            (ticket_id,)
        )

    def create(self, data):
        if not data.get('title', '').strip():
            raise ValueError('Ticket title is required.')
        return execute(
            "INSERT INTO tickets (client_id, title, description, status, priority) "
            "VALUES (%s, %s, %s, %s, %s)",
            (
                data['client_id'],
                data['title'].strip(),
                data.get('description', '').strip() or None,
                data.get('status', 'open'),
                data.get('priority', 'medium'),
            )
        )

    def update(self, ticket_id, data):
        if not data.get('title', '').strip():
            raise ValueError('Ticket title is required.')
        execute(
            "UPDATE tickets SET client_id=%s, title=%s, description=%s, status=%s, priority=%s "
            "WHERE id=%s",
            (
                data['client_id'],
                data['title'].strip(),
                data.get('description', '').strip() or None,
                data.get('status', 'open'),
                data.get('priority', 'medium'),
                ticket_id,
            )
        )

    def delete(self, ticket_id):
        execute("DELETE FROM tickets WHERE id=%s", (ticket_id,))
