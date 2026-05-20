import sqlite3
import pickle
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "biyatrix.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'anonymous',
            raw_input TEXT NOT NULL,
            problem TEXT,
            constraints TEXT,
            solution TEXT,
            domain TEXT,
            tools TEXT,
            stage TEXT,
            emotion TEXT,
            summary TEXT,
            embedding BLOB,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def save_entry(user_id: str, raw_input: str, extracted: dict, embedding):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO entries
            (user_id, raw_input, problem, constraints, solution, domain, tools, stage, emotion, summary, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        raw_input,
        extracted.get("problem"),
        json.dumps(extracted.get("constraints") or []),
        extracted.get("solution"),
        extracted.get("domain"),
        json.dumps(extracted.get("tools") or []),
        extracted.get("stage"),
        extracted.get("emotion"),
        extracted.get("summary"),
        pickle.dumps(embedding),
    ))
    conn.commit()
    conn.close()


def get_all_entries():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM entries ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_entries(limit: int = 30):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM entries ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
