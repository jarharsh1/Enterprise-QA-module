import json
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from app.config import settings

@contextmanager
def connection():
    """
    Context manager for PostgreSQL database connection.
    Decorator to manage the connection lifecycle, ensuring that the connection is properly closed after use.
    """
    url = settings().database_url
    if not url:
        raise RuntimeError("Database URL is not set in the configuration.")
    else:
        with psycopg.connect(url,row_factory=dict_row) as conn: #connect with postgres database using the url from the settings
            yield conn

def audit(conn,actor,tenant,action,detail):
    """
    Function to insert an audit event into the audit_events table.
    Parameters:
        conn: The database connection object.
        actor: The actor performing the action.
        tenant: The tenant associated with the action.
        action: The action being performed.
        detail: Additional details about the action (as a dictionary).
    """
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO audit_events (actor, tenant_id, action, detail) VALUES (%s, %s, %s, %s)",
            (actor, tenant, action, json.dumps(detail))
        )
