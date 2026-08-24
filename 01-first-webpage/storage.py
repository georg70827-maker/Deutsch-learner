import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).with_name("learning.db")


def connect():
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                scene TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
            """
        )


def create_conversation(conversation_id, scene, opening):
    with connect() as connection:
        connection.execute(
            "INSERT INTO conversations (id, scene) VALUES (?, ?)",
            (conversation_id, scene),
        )
        connection.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, "assistant", opening),
        )


def add_message(conversation_id, role, content):
    with connect() as connection:
        connection.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content),
        )


def conversation_exists(conversation_id):
    with connect() as connection:
        row = connection.execute(
            "SELECT 1 FROM conversations WHERE id = ?", (conversation_id,)
        ).fetchone()
    return row is not None


def message_count(conversation_id):
    with connect() as connection:
        row = connection.execute(
            "SELECT COUNT(*) FROM messages WHERE conversation_id = ?",
            (conversation_id,),
        ).fetchone()
    return row[0]
