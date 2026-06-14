import sqlite3
from contextlib import contextmanager
from typing import Generator

from fastapi import FastAPI

app = FastAPI()

_DB_PATH = ":memory:"


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'alice')")
    conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'bob')")
    conn.commit()


_conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
_init_db(_conn)


@contextmanager
def _cursor() -> Generator[sqlite3.Cursor, None, None]:
    cur = _conn.cursor()
    try:
        yield cur
    finally:
        cur.close()


@app.get("/users")
def search_users(name: str = "") -> dict:
    # BUG: SQL injection via concatenação de string
    query = f"SELECT id, name FROM users WHERE name = '{name}'"
    with _cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    return {"users": [{"id": r[0], "name": r[1]} for r in rows]}
