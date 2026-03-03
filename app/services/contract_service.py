from app.db import query, query_one, execute


class ContractService:
    def list(self, client_id=0, status=''):
        sql = (
            "SELECT c.id, c.client_id, c.name, c.hourly_rate, c.start_date, c.end_date, c.status, "
            "       c.created_at, c.updated_at, cl.name AS client_name "
            "FROM contracts c JOIN clients cl ON c.client_id = cl.id WHERE 1=1"
        )
        params = []
        if client_id:
            sql += " AND c.client_id=%s"
            params.append(client_id)
        if status:
            sql += " AND c.status=%s"
            params.append(status)
        sql += " ORDER BY cl.name, c.name"
        return query(sql, params)

    def list_by_client(self, client_id):
        return query(
            "SELECT id, name, hourly_rate, start_date, end_date, status "
            "FROM contracts WHERE client_id=%s ORDER BY name",
            (client_id,)
        )

    def get_active_contracts(self):
        return query(
            "SELECT c.id, c.name, c.hourly_rate, cl.name AS client_name "
            "FROM contracts c JOIN clients cl ON c.client_id = cl.id "
            "WHERE c.status='active' ORDER BY cl.name, c.name"
        )

    def get(self, contract_id):
        return query_one(
            "SELECT c.id, c.client_id, c.name, c.hourly_rate, c.start_date, c.end_date, c.status, "
            "       c.created_at, c.updated_at, cl.name AS client_name "
            "FROM contracts c JOIN clients cl ON c.client_id = cl.id WHERE c.id=%s",
            (contract_id,)
        )

    def create(self, data):
        if not data.get('name', '').strip():
            raise ValueError('Contract name is required.')
        if not data.get('hourly_rate'):
            raise ValueError('Hourly rate is required.')
        return execute(
            "INSERT INTO contracts (client_id, name, hourly_rate, start_date, end_date, status) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                data['client_id'],
                data['name'].strip(),
                float(data['hourly_rate']),
                data['start_date'],
                data.get('end_date') or None,
                data.get('status', 'active'),
            )
        )

    def update(self, contract_id, data):
        if not data.get('name', '').strip():
            raise ValueError('Contract name is required.')
        execute(
            "UPDATE contracts SET client_id=%s, name=%s, hourly_rate=%s, start_date=%s, "
            "end_date=%s, status=%s WHERE id=%s",
            (
                data['client_id'],
                data['name'].strip(),
                float(data['hourly_rate']),
                data['start_date'],
                data.get('end_date') or None,
                data.get('status', 'active'),
                contract_id,
            )
        )

    def delete(self, contract_id):
        execute("DELETE FROM contracts WHERE id=%s", (contract_id,))
