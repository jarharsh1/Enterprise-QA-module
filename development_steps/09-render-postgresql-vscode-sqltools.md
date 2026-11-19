# Render PostgreSQL — VS Code SQLTools

Adapted from the supplied SQLTools setup guide. Actual instance hostname, database, username and credentials are omitted because the repository is public.

## 1. Install VS Code extensions

1. Open VS Code and press Ctrl+Shift+X.
2. Install SQLTools (Matheus Teixeira).
3. Install SQLTools PostgreSQL/Cockroach Driver.
4. Open the SQLTools sidebar (database icon).

## 2. Create a connection

Select Add New Connection → PostgreSQL. Fill in values from your Render instance's External Database URL/details.

| Field | Value |
| --- | --- |
| Connection name | Render PostgreSQL |
| Connection group | Optional |
| Connect using | Server and Port |
| Server Address | Your Render external hostname |
| Port | 5432 (or the instance's configured port) |
| Database | Your database name |
| Username | Your database user |
| Use password | Ask on connect |
| SSL | Enabled / Required |

## 3. Test the connection

The source guide stops at the SSL setting; the following is a suggested verification procedure. Save the connection, use Test Connection or Connect, supply the password when prompted, and run:

```sql
SELECT current_database(), current_user;
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('documents','feedback','audit_events','approvals','chat_messages')
ORDER BY table_name;
```

After running scripts/init_db.py, the second query should return five rows. This is a read-only check; it does not prove application connectivity. See [database foundation](04-database-foundation.md). Do not disable SSL to bypass connection errors or save passwords in committed workspace settings.
