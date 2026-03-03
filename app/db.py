import pymysql
import pymysql.cursors
import os


def get_connection():
    """Return a new PyMySQL connection using env config."""
    return pymysql.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'cfuser'),
        password=os.getenv('DB_PASSWORD', 'cfpassword'),
        database=os.getenv('DB_NAME', 'hours_tracking'),
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4',
        autocommit=True,
    )


def query(sql, params=None):
    """Execute a SELECT and return all rows as a list of dicts."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()


def query_one(sql, params=None):
    """Execute a SELECT and return the first row as a dict, or None."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()


def execute(sql, params=None):
    """Execute an INSERT/UPDATE/DELETE. Returns lastrowid."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            conn.commit()
            return cur.lastrowid


def execute_in_transaction(operations):
    """
    Run multiple operations in a single transaction.
    operations: callable that receives (conn, cursor) and returns a value.
    """
    conn = get_connection()
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            result = operations(conn, cur)
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
