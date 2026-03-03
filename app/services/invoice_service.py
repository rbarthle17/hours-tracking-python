import datetime
from app.db import query, query_one, execute, execute_in_transaction


class InvoiceService:
    def list(self, client_id=0, status=''):
        sql = (
            "SELECT i.id, i.client_id, i.invoice_number, i.invoice_date, i.due_date, "
            "       i.total_amount, i.status, i.notes, i.created_at, "
            "       cl.name AS client_name, "
            "       COALESCE(SUM(p.amount),0) AS total_paid "
            "FROM invoices i "
            "JOIN clients cl ON i.client_id = cl.id "
            "LEFT JOIN payments p ON i.id = p.invoice_id "
            "WHERE 1=1"
        )
        params = []
        if client_id:
            sql += " AND i.client_id=%s"
            params.append(client_id)
        if status:
            sql += " AND i.status=%s"
            params.append(status)
        sql += " GROUP BY i.id ORDER BY i.invoice_date DESC"
        return query(sql, params)

    def get(self, invoice_id):
        return query_one(
            "SELECT i.id, i.client_id, i.invoice_number, i.invoice_date, i.due_date, "
            "       i.total_amount, i.status, i.notes, i.created_at, "
            "       cl.name AS client_name, "
            "       COALESCE(SUM(p.amount),0) AS total_paid "
            "FROM invoices i "
            "JOIN clients cl ON i.client_id = cl.id "
            "LEFT JOIN payments p ON i.id = p.invoice_id "
            "WHERE i.id=%s GROUP BY i.id",
            (invoice_id,)
        )

    def get_line_items(self, invoice_id):
        return query(
            "SELECT li.id, li.invoice_id, li.contract_id, li.time_entry_id, "
            "       li.hours, li.rate, li.description, li.subtotal, "
            "       c.name AS contract_name "
            "FROM invoice_line_items li "
            "JOIN contracts c ON li.contract_id = c.id "
            "WHERE li.invoice_id=%s ORDER BY li.id",
            (invoice_id,)
        )

    def generate_number(self):
        year = datetime.date.today().year
        row = query_one(
            "SELECT COUNT(*) AS cnt FROM invoices WHERE YEAR(invoice_date)=%s",
            (year,)
        )
        seq = (row['cnt'] if row else 0) + 1
        return f"INV-{year}-{seq:04d}"

    def create_from_time_entries(self, client_id, time_entry_ids, invoice_date, due_date, notes=''):
        if not time_entry_ids:
            raise ValueError('Select at least one time entry.')

        def ops(conn, cur):
            invoice_number = self.generate_number()
            cur.execute(
                "INSERT INTO invoices (client_id, invoice_number, invoice_date, due_date, "
                "total_amount, status, notes) VALUES (%s,%s,%s,%s,0,'draft',%s)",
                (client_id, invoice_number, invoice_date, due_date, notes or None)
            )
            invoice_id = cur.lastrowid

            total = 0
            for entry_id in time_entry_ids:
                cur.execute(
                    "SELECT te.id, te.hours_worked, c.hourly_rate, c.id AS contract_id, "
                    "       t.title AS ticket_title "
                    "FROM time_entries te "
                    "JOIN contracts c ON te.contract_id = c.id "
                    "JOIN tickets t ON te.ticket_id = t.id "
                    "WHERE te.id=%s",
                    (entry_id,)
                )
                entry = cur.fetchone()
                if not entry:
                    continue
                subtotal = float(entry['hours_worked']) * float(entry['hourly_rate'])
                total += subtotal
                description = entry['ticket_title']
                cur.execute(
                    "INSERT INTO invoice_line_items "
                    "(invoice_id, contract_id, time_entry_id, hours, rate, description, subtotal) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (invoice_id, entry['contract_id'], entry['id'],
                     entry['hours_worked'], entry['hourly_rate'], description, subtotal)
                )

            cur.execute("UPDATE invoices SET total_amount=%s WHERE id=%s", (total, invoice_id))
            return invoice_id

        return execute_in_transaction(ops)

    def update(self, invoice_id, data):
        execute(
            "UPDATE invoices SET invoice_date=%s, due_date=%s, notes=%s WHERE id=%s",
            (data['invoice_date'], data['due_date'], data.get('notes', '') or None, invoice_id)
        )

    def update_status(self, invoice_id, status):
        execute("UPDATE invoices SET status=%s WHERE id=%s", (status, invoice_id))

    def recalculate_status(self, invoice_id):
        invoice = self.get(invoice_id)
        if not invoice:
            return
        total = float(invoice['total_amount'])
        paid = float(invoice['total_paid'])
        if invoice['status'] == 'draft':
            return
        if paid >= total:
            status = 'paid'
        elif paid > 0:
            status = 'partial'
        else:
            status = invoice['status']  # keep sent/overdue
        self.update_status(invoice_id, status)

    def delete(self, invoice_id):
        execute("DELETE FROM invoices WHERE id=%s", (invoice_id,))
