"""Registry of course runtimes.

A runtime knows how to validate an admin's reference solution and grade a student answer. Grading always
happens on the server. To add a technology, implement `validate` and `grade` (run student code in an isolated
process, never in the API process) and register it in RUNTIMES.
"""
from dataclasses import dataclass
from typing import Callable

from . import grader, pyrunner


@dataclass(frozen=True)
class Runtime:
    key: str
    label: str
    validate: Callable      # (lesson_data: dict) -> error message or None
    grade: Callable         # (lesson, code) -> (passed, message)
    server_run: bool = False  # True when the browser runs code through POST /run (otherwise it runs locally)


def _validate_sql(data: dict) -> str | None:
    res = grader.run_sql(data["solution"], data.get("verify"))
    if not res.ok:
        return f"Solution failed to run: {res.error}"
    if not res.columns:
        return "Solution must produce a result set (add a verify query for INSERT/UPDATE/DELETE)."
    return None


RUNTIMES: dict[str, Runtime] = {
    "sql": Runtime("sql", "SQL (SQLite sandbox)", _validate_sql, grader.grade),
    "python": Runtime("python", "Python (sandboxed process)", pyrunner.validate, pyrunner.grade, server_run=True),
}

# Shown to admins as roadmap; not selectable until implemented.
PLANNED = ["javascript", "html-css", "git", "linux"]
