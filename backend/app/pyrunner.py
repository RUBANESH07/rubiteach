"""Runs and grades student Python in a separate, time-limited process (never inside the API process)."""
import json
import os
import secrets
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .config import settings

CHILD = str(Path(__file__).with_name("pysandbox_child.py"))
MAX_CODE = 20_000
MAX_OUT = 100_000


@dataclass
class PyResult:
    ok: bool = True               # process ran and returned a result
    stdout: str = ""
    error: str | None = None      # exception / syntax error raised by student code
    value: str | None = None      # repr() of the test expression, when one was given
    has_value: bool = False
    timed_out: bool = False
    ms: int = 0
    system_error: str | None = None


def run_python(code: str, stdin: str = "", expr: str | None = None, timeout: float | None = None) -> PyResult:
    timeout = timeout or settings.python_timeout_seconds
    if len(code) > MAX_CODE:
        return PyResult(error="Code is too long.")
    nonce = secrets.token_hex(12) + ":"
    t0 = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="rt_py_", ignore_cleanup_errors=True) as work:
        payload = json.dumps({"code": code, "stdin": stdin[:10_000], "expr": expr, "nonce": nonce,
                              "work": work, "max_out": MAX_OUT}).encode("utf-8")
        env = {"PYTHONIOENCODING": "utf-8", "PYTHONHASHSEED": "0"}
        if os.name == "nt":
            env["SYSTEMROOT"] = os.environ.get("SYSTEMROOT", r"C:\Windows")
        try:
            proc = subprocess.run([sys.executable, "-I", CHILD], input=payload, capture_output=True,
                                  timeout=timeout, cwd=work, env=env)
        except subprocess.TimeoutExpired:
            return PyResult(timed_out=True, ms=int((time.monotonic() - t0) * 1000))
        except OSError as e:
            return PyResult(ok=False, system_error=str(e))
    ms = int((time.monotonic() - t0) * 1000)
    for line in reversed(proc.stdout.decode("utf-8", "replace").splitlines()):
        if line.startswith(nonce):
            data = json.loads(line[len(nonce):])
            return PyResult(stdout=data["stdout"], error=data["error"], value=data["value"],
                            has_value=data["has_value"], ms=ms)
    tail = proc.stderr.decode("utf-8", "replace").strip().splitlines()[-1:] or ["no result"]
    return PyResult(ok=False, system_error=f"Runner failed: {tail[0][:200]}", ms=ms)


def _norm(s: str) -> str:
    return "\n".join(l.rstrip() for l in s.replace("\r\n", "\n").rstrip().split("\n"))


@lru_cache(maxsize=2048)
def _expected(solution: str, stdin: str, expr: str | None) -> PyResult:
    return run_python(solution, stdin, expr, timeout=max(settings.python_timeout_seconds, 8))


def _clip(s: str, n: int = 300) -> str:
    s = s if len(s) <= n else s[:n] + "…"
    return s if s else "(nothing)"


def validate(data: dict) -> str | None:
    """Admin-time check: the reference solution must run cleanly on every test case. Returns an error or None."""
    spec = data.get("tests") or {}
    for i, case in enumerate(spec.get("cases") or [{}], 1):
        r = run_python(data["solution"], case.get("stdin", ""), case.get("expr"), timeout=10)
        if r.timed_out:
            return f"Solution timed out on test {i}."
        if not r.ok:
            return r.system_error
        if r.error:
            return f"Solution failed on test {i}: {r.error}"
        if case.get("expr") is None and not r.stdout.strip():
            return f"Test {i}: the solution prints nothing, so there is nothing to check (add an expr or print something)."
    return None


def grade(lesson, code: str) -> tuple[bool, str]:
    spec = lesson.tests or {}
    for needle in spec.get("requires") or []:
        if needle not in code:
            return False, f"Your solution should use `{needle}` for this exercise."
    for needle in spec.get("forbid") or []:
        if needle in code:
            return False, f"This exercise does not allow `{needle}`. Try solving it the way the lesson shows."
    cases = spec.get("cases") or [{}]
    for i, case in enumerate(cases, 1):
        stdin, expr = case.get("stdin", ""), case.get("expr")
        ref = _expected(lesson.solution, stdin, expr)
        got = run_python(code, stdin, expr)
        if got.timed_out:
            return False, f"Your code ran for more than {settings.python_timeout_seconds:g} seconds. Check for an infinite loop."
        if not got.ok:
            return False, "The code runner had a problem. Please try again."
        if got.error:
            return False, f"Your code raised an error: {got.error}"
        use_value = expr is not None
        same_value = (not use_value) or (got.value == ref.value)
        same_out = (use_value and not case.get("check_stdout")) or _norm(got.stdout) == _norm(ref.stdout)
        if same_value and same_out:
            continue
        visible = case.get("visible", i == 1)
        if not visible:
            return False, f"A hidden test failed (test {i} of {len(cases)}). Re-read the task and check edge cases."
        note = f" ({case['note']})" if case.get("note") else ""
        if not same_value:
            return False, f"Test {i}{note} failed. Expected {_clip(ref.value or '')} but got {_clip(got.value or 'None')}."
        return False, f"Test {i}{note} failed.\nExpected output:\n{_clip(ref.stdout)}\nYour output:\n{_clip(got.stdout)}"
    return True, "Correct! Your code passed every test."
