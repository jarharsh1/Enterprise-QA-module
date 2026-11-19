# Step 05 — Database connection management and auditing

**Source:** [app/db.py](../app/db.py), [app/config.py](../app/config.py), [infra/schema.sql](../infra/schema.sql). Commit [7977406](https://github.com/jarharsh1/Enterprise-QA-module/commit/7977406f507541d79e72b29d68a5f12e044dd073).

## What we built

The connection() function uses contextlib.contextmanager. It retrieves database_url from cached settings, raises RuntimeError if the URL is empty, and yields a psycopg connection configured with dict_row. The psycopg connection context commits normal completion, rolls back on exception and closes the connection. Each invocation opens a new connection; no connection pool is implemented yet.

The audit(conn, actor, tenant, action, detail) helper opens a cursor and inserts an audit_events row. It serializes detail with json.dumps and passes values separately from SQL using %s placeholders. The caller owns the transaction; audit does not commit independently.

## Suggested validation (disposable database only)

First initialize the schema using Step 04, then:

```python
from app.db import connection, audit

with connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT 1 AS ok")
        assert cur.fetchone()["ok"] == 1
    audit(conn, "demo-user", "demo-tenant", "smoke_test",
          {"source": "development"})
```

This writes one synthetic audit record on successful exit. Verify it in a test database with a parameterized query. Check rollback by intentionally raising an exception after a test insert and verifying no row remains.

## Why it matters

Context management centralizes cleanup. Parameterized SQL prevents values from being interpreted as SQL syntax. JSONB allows structured event details. Tenant and actor columns support future audit analysis, but the helper itself does not authenticate the actor or isolate tenants.

## Outstanding

Connection pooling, query timeout/retry policies, authorization, audit redaction and automated tests are future work. Do not write secrets or sensitive document content to audit details.

**Next:** [AWS client factory](06-aws-client.md).
