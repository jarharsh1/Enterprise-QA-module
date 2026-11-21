import uuid
from app.db import connection
from app.config import settings

def history(tenant:str, conversation_id:uuid.UUID):
    """Return the conversation history for the given tenant and conversation ID."""
    with connection() as conn:
        rows = conn.execute(
            """SELECT role, content from 
            (select id,role,content,craeted_at from chat_messages where tenant_id=%s and conversation_id=%s 
            order by id desc limit %s) as sub order by id asc""",
            (tenant, str(conversation_id),settings().memory_turns*2)
        ).fetchall()
    return rows

def save_turn(tenant:str,conversation_id:uuid.UUID,question:str, response:str):
    with connection() as conn:
        conn.execute("""INSERT INTO chat_messages(tenant_id,conversation_id,role,content)
                                VALUES (%s,%s,'user',%s),(%s,%s,'assistant',%s)""",
                    (tenant,conversation_id,question,tenant,conversation_id,response))

def list_messages(tenant: str, conversation_id: uuid.UUID):
    with connection() as conn:
        return conn.execute("""SELECT role,content,created_at FROM chat_messages
          WHERE tenant_id=%s AND conversation_id=%s ORDER BY id ASC LIMIT 100""",
          (tenant,conversation_id)).fetchall()