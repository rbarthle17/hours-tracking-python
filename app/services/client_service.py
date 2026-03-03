from app.db import query, query_one, execute


class ClientService:
    def list(self, search=''):
        if search:
            return query(
                "SELECT id, name, email, phone, address, created_at, updated_at "
                "FROM clients WHERE name LIKE %s OR email LIKE %s ORDER BY name",
                (f'%{search}%', f'%{search}%')
            )
        return query(
            "SELECT id, name, email, phone, address, created_at, updated_at "
            "FROM clients ORDER BY name"
        )

    def get(self, client_id):
        return query_one(
            "SELECT id, name, email, phone, address, created_at, updated_at "
            "FROM clients WHERE id=%s",
            (client_id,)
        )

    def create(self, data):
        if not data.get('name', '').strip():
            raise ValueError('Client name is required.')
        return execute(
            "INSERT INTO clients (name, email, phone, address) VALUES (%s, %s, %s, %s)",
            (
                data['name'].strip(),
                data.get('email', '').strip() or None,
                data.get('phone', '').strip() or None,
                data.get('address', '').strip() or None,
            )
        )

    def update(self, client_id, data):
        if not data.get('name', '').strip():
            raise ValueError('Client name is required.')
        execute(
            "UPDATE clients SET name=%s, email=%s, phone=%s, address=%s WHERE id=%s",
            (
                data['name'].strip(),
                data.get('email', '').strip() or None,
                data.get('phone', '').strip() or None,
                data.get('address', '').strip() or None,
                client_id,
            )
        )

    def delete(self, client_id):
        execute("DELETE FROM clients WHERE id=%s", (client_id,))
