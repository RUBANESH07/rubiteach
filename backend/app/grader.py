"""Sandboxed SQL grader.

Student SQL never touches the application database. Every run uses a fresh
in-memory SQLite database seeded from content/seed.sql, with an authorizer that
blocks ATTACH/DETACH/PRAGMA and a progress handler that enforces a time limit.
"""
import json
import sqlite3
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .config import settings

CONTENT = Path(__file__).parent / "content"
MAX_ROWS = 1000
_DENIED = {sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH, sqlite3.SQLITE_PRAGMA}


@lru_cache(maxsize=1)
def seed_sql() -> str:
    return (CONTENT / "seed.sql").read_text(encoding="utf-8")


def _authorizer(action, *_):
    return sqlite3.SQLITE_DENY if action in _DENIED else sqlite3.SQLITE_OK


def _split(sql: str):
    """Split on ';' but only where SQLite says the statement is complete (handles ; in strings)."""
    buf = ""
    for part in sql.split(";"):
        buf += part + ";"
        if sqlite3.complete_statement(buf):
            if buf.strip(" \n\r\t;"):
                yield buf
            buf = ""
    if buf.strip(" \n\r\t;"):
        yield buf.rstrip(";")


@dataclass
class QueryResult:
    ok: bool
    columns: list[str] | None = None
    rows: list[list] | None = None
    error: str | None = None


def run_sql(sql: str, verify: str | None = None) -> QueryResult:
    if len(sql) > settings.max_query_chars:
        return QueryResult(False, error="Query is too long.")
    con = sqlite3.connect(":memory:")
    try:
        con.executescript(seed_sql())
        con.set_authorizer(_authorizer)
        deadline = time.monotonic() + settings.query_timeout_seconds
        con.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 10000)
        cols, rows = [], []
        for stmt in list(_split(sql)) + ([verify] if verify else []):
            cur = con.execute(stmt)
            if cur.description:
                cols = [d[0] for d in cur.description]
                rows = [list(r) for r in cur.fetchmany(MAX_ROWS)]
            elif stmt is not verify:
                cols, rows = [], []
        return QueryResult(True, cols, rows)
    except sqlite3.Error as e:
        msg = "Query took too long and was stopped." if "interrupted" in str(e) else str(e)
        return QueryResult(False, error=msg)
    finally:
        con.close()


def _norm(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        n = round(float(v), 2)
        return str(int(n)) if n == int(n) else str(n)
    return str(v)


def grade(lesson, sql: str) -> tuple[bool, str]:
    """`lesson` is a Lesson row (or any object with solution, verify, ordered)."""
    user = run_sql(sql, lesson.verify)
    if not user.ok:
        return False, f"Your query has an error: {user.error}"
    ref = run_sql(lesson.solution, lesson.verify)
    if not user.columns:
        return False, "Your query did not return any rows. Did you forget a SELECT?"
    if len(user.columns) != len(ref.columns):
        return False, f"Expected {len(ref.columns)} column(s) but got {len(user.columns)}."
    if len(user.rows) != len(ref.rows):
        return False, f"Expected {len(ref.rows)} row(s) but got {len(user.rows)}. Check your WHERE / GROUP BY / JOIN."
    a = [json.dumps([_norm(v) for v in r]) for r in user.rows]
    b = [json.dumps([_norm(v) for v in r]) for r in ref.rows]
    if a == b or (not lesson.ordered and sorted(a) == sorted(b)):
        return True, "Correct! Your result matches the expected output."
    if lesson.ordered and sorted(a) == sorted(b):
        return False, "The right rows, but in the wrong order. Check your ORDER BY."
    return False, "The rows returned do not match the expected result. Compare your output with the task."
