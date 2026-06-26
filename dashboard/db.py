"""
db.py — SQLite storage helper for the AI LogMon dashboard.

Provides simple functions to create tables, insert logs/errors,
and query data. Uses a single SQLite file (logs.db) stored in
the dashboard/ directory.
"""

import sqlite3
import os
from datetime import datetime

# Path to the SQLite database file (next to this script)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs.db")


def get_connection():
    """Create and return a database connection with WAL mode enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent read/write
    return conn


def init_db():
    """Create the logs and errors tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT    NOT NULL,
            level     TEXT    NOT NULL,
            source    TEXT    NOT NULL,
            message   TEXT    NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS errors (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT    NOT NULL,
            source    TEXT    NOT NULL,
            message   TEXT    NOT NULL,
            severity  TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def insert_log(level, source, message):
    """Insert a single log entry into the logs table."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO logs (timestamp, level, source, message) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), level, source, message),
    )
    conn.commit()
    conn.close()


def insert_error(source, message, severity):
    """Insert a single error entry into the errors table."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO errors (timestamp, source, message, severity) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), source, message, severity),
    )
    conn.commit()
    conn.close()


def get_logs(limit=100, level=None):
    """
    Fetch recent log entries, newest first.

    Args:
        limit: Maximum number of rows to return (default 100).
        level: Optional filter — e.g. "ERROR", "WARNING". None = all levels.

    Returns:
        A list of dicts, each with keys: id, timestamp, level, source, message.
    """
    conn = get_connection()

    if level:
        rows = conn.execute(
            "SELECT * FROM logs WHERE level = ? ORDER BY id DESC LIMIT ?",
            (level, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM logs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    conn.close()
    return [dict(row) for row in rows]


def get_errors(limit=50):
    """
    Fetch recent error entries, newest first.

    Args:
        limit: Maximum number of rows to return (default 50).

    Returns:
        A list of dicts, each with keys: id, timestamp, source, message, severity.
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM errors ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stats():
    """
    Compute aggregate statistics from the logs and errors tables.

    Returns:
        A dict with keys: total_logs, total_errors, and a breakdown
        of log counts by level (info, warning, error, debug).
    """
    conn = get_connection()

    total_logs = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
    total_errors = conn.execute("SELECT COUNT(*) FROM errors").fetchone()[0]

    # Count logs by level
    info_count = conn.execute(
        "SELECT COUNT(*) FROM logs WHERE level = 'INFO'"
    ).fetchone()[0]
    warning_count = conn.execute(
        "SELECT COUNT(*) FROM logs WHERE level = 'WARNING'"
    ).fetchone()[0]
    error_count = conn.execute(
        "SELECT COUNT(*) FROM logs WHERE level = 'ERROR'"
    ).fetchone()[0]
    debug_count = conn.execute(
        "SELECT COUNT(*) FROM logs WHERE level = 'DEBUG'"
    ).fetchone()[0]

    conn.close()

    return {
        "total_logs": total_logs,
        "total_errors": total_errors,
        "info": info_count,
        "warning": warning_count,
        "error": error_count,
        "debug": debug_count,
    }
