import sqlite3
import json
import logging
from typing import List
from sergeant.models.base import ModelMessage

logger = logging.getLogger(__name__)

class SQLiteMemory:
    def __init__(self, db_path: str = "sergeant_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    role TEXT,
                    content TEXT,
                    tool_calls TEXT,
                    tool_call_id TEXT,
                    name TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_id ON history(chat_id)")

    def add_message(self, chat_id: int, msg: ModelMessage) -> None:
        tool_calls_json = json.dumps(msg.tool_calls) if msg.tool_calls else None
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO history (chat_id, role, content, tool_calls, tool_call_id, name)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (chat_id, msg.role, msg.content, tool_calls_json, msg.tool_call_id, msg.name)
            )

    def get_history(self, chat_id: int, limit: int = 15) -> List[ModelMessage]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT role, content, tool_calls, tool_call_id, name 
                   FROM history WHERE chat_id = ? 
                   ORDER BY timestamp DESC LIMIT ?""",
                (chat_id, limit)
            )
            rows = cursor.fetchall()

        messages = []
        for row in reversed(rows):
            tool_calls = json.loads(row["tool_calls"]) if row["tool_calls"] else None
            messages.append(ModelMessage(
                role=row["role"],
                content=row["content"],
                tool_calls=tool_calls,
                tool_call_id=row["tool_call_id"],
                name=row["name"]
            ))
        return messages

    def clear_history(self, chat_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM history WHERE chat_id = ?", (chat_id,))