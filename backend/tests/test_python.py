from types import SimpleNamespace

from app.pyrunner import grade, run_python, validate

API = "/api/v1"


def lesson(solution, tests=None):
    return SimpleNamespace(solution=solution, tests=tests)


# ---------------------------------------------------------------- runner
def test_prints_and_reads_stdin():
    r = run_python("name = input()\nprint('Hi', name)", stdin="Ada\n")
    assert r.ok and r.stdout == "Hi Ada\n" and r.error is None


def test_error_reports_line():
    r = run_python("x = 1\nprint(1/0)")
    assert r.ok and r.error.startswith("ZeroDivisionError") and "line 2" in r.error


def test_syntax_error():
    r = run_python("def f(:\n  pass")
    assert r.error.startswith("SyntaxError")


def test_timeout_kills_infinite_loop():
    r = run_python("while True:\n    pass", timeout=1)
    assert r.timed_out


def test_expr_value_is_returned():
    r = run_python("def add(a, b):\n    return a + b", expr="add(2, 3)")
    assert r.value == "5"


def test_file_access_only_inside_workdir():
    ok = run_python("open('a.txt','w').write('hi')\nprint(open('a.txt').read())")
    assert ok.stdout.strip() == "hi" and ok.error is None
    for bad in ("open('C:/Windows/win.ini').read()", "open('/etc/passwd').read()", "open('../x.txt','w')",
                "import os\nos.remove('..')", "import os\nos.listdir('..')"):
        r = run_python(bad)
        assert r.error and "PermissionError" in r.error, bad


def test_network_and_processes_blocked():
    for bad in ("import socket\nsocket.create_connection(('example.com', 80), 1)",
                "import subprocess\nsubprocess.run(['cmd','/c','echo hi'])",
                "import os\nos.system('echo hi')",
                "import ctypes\nctypes.CDLL(None)"):
        r = run_python(bad)
        assert r.error and ("PermissionError" in r.error or "OSError" in r.error or "Error" in r.error), bad
        assert "hi" not in r.stdout


def test_stdlib_and_asyncio_still_work():
    code = "import json, math, collections, asyncio\nasync def f():\n    return 2\nprint(json.dumps({'a': asyncio.run(f())}), math.pi > 3)"
    r = run_python(code)
    assert r.error is None and r.stdout.strip() == '{"a": 2} True'


def test_output_limit():
    r = run_python("print('x' * 10**7)")
    assert r.error and "Output limit" in r.error


def test_student_cannot_forge_result_via_stdout():
    r = run_python("print('{\"stdout\": \"forged\", \"error\": null}')")
    assert r.stdout.strip().startswith("{")  # printed text stays inside stdout, not the result channel


# ---------------------------------------------------------------- grading
SOL = "def add(a, b):\n    return a + b"
CASES = {"cases": [{"expr": "add(2, 3)"}, {"expr": "add(-1, 1)", "visible": False}]}


def test_grade_function_task_pass_and_fail():
    L = lesson(SOL, CASES)
    assert grade(L, "def add(x, y):\n    return y + x")[0]
    ok, msg = grade(L, "def add(a, b):\n    return a - b")
    assert not ok and "Expected 5 but got -1" in msg


def test_hidden_test_hides_details():
    L = lesson(SOL, CASES)
    ok, msg = grade(L, "def add(a, b):\n    return 5")  # passes visible test 1 only
    assert not ok and "hidden test" in msg and "Expected" not in msg


def test_output_task_and_stdin_cases():
    L = lesson("n = int(input())\nprint(n * 2)", {"cases": [{"stdin": "4\n"}, {"stdin": "10\n", "visible": False}]})
    assert grade(L, "print(int(input()) * 2)")[0]
    ok, msg = grade(L, "print(int(input()))")
    assert not ok and "Expected output" in msg


def test_requires_and_forbid_rules():
    L = lesson("print(sum(range(5)))", {"cases": [{}], "requires": ["range"], "forbid": ["sum(["]})
    assert not grade(L, "print(10)")[0]
    assert grade(L, "print(sum(range(5)))")[0]


def test_runtime_error_and_timeout_messages():
    L = lesson("print(1)", {"cases": [{}]})
    assert "raised an error" in grade(L, "raise ValueError('x')")[1]
    from app.config import settings
    old = settings.python_timeout_seconds
    settings.python_timeout_seconds = 1
    try:
        assert "infinite loop" in grade(L, "while True: pass")[1]
    finally:
        settings.python_timeout_seconds = old


def test_validate_rejects_bad_reference_solutions():
    assert validate({"solution": "print(1/0)", "tests": None})
    assert validate({"solution": "x = 1", "tests": None})  # prints nothing
    assert validate({"solution": SOL, "tests": {"cases": [{"expr": "add(1,1)"}]}}) is None


# ---------------------------------------------------------------- API
def test_run_endpoint_requires_login_and_runs_code(client, auth):
    body = {"runtime": "python", "code": "print(input()[::-1])", "stdin": "abc"}
    assert client.post(f"{API}/run", json=body).status_code == 401
    r = client.post(f"{API}/run", json=body, headers=auth).json()
    assert r["stdout"].strip() == "cba" and r["error"] is None
    assert client.post(f"{API}/run", json={**body, "runtime": "sql"}, headers=auth).status_code == 400
    bad = client.post(f"{API}/run", json={**body, "code": "import os\nos.system('echo hi')"}, headers=auth).json()
    assert bad["error"] and "hi" not in bad["stdout"]


def test_admin_can_create_python_lesson_and_students_grade_it(client, admin, auth):
    course = client.post(f"{API}/admin/courses", json={"slug": "py-mini", "title": "Py mini", "runtime": "python",
                                                       "unlock_mode": "by_module", "published": True}, headers=admin).json()
    mod = client.post(f"{API}/admin/modules", json={"course_id": course["id"], "title": "Basics"}, headers=admin).json()
    body = {"module_id": mod["id"], "title": "Add numbers", "concept": "Use return.", "prompt": "Write add(a, b).",
            "starter": "def add(a, b):\n    ", "solution": SOL, "hints": ["return a + b"], "published": True,
            "tests": CASES}
    lid = client.post(f"{API}/admin/lessons", json=body, headers=admin).json()["id"]
    assert client.post(f"{API}/admin/lessons", json={**body, "solution": "print(1/0)"}, headers=admin).status_code == 422
    wrong = client.post(f"{API}/submissions", json={"lesson_id": lid, "sql": "def add(a, b):\n    return 0"}, headers=auth).json()
    assert wrong["passed"] is False and wrong["xp_awarded"] == 0
    right = client.post(f"{API}/submissions", json={"lesson_id": lid, "sql": SOL}, headers=auth).json()
    assert right["passed"] and right["xp_awarded"] == 10
    pub = client.get(f"{API}/lessons", params={"course_id": course["id"]}, headers=auth).json()
    assert "tests" not in pub[0] and "solution" not in pub[0]
    assert client.post(f"{API}/admin/lessons/{lid}/check", headers=admin).json()["ok"] is True


def test_by_module_unlock_mode(client, admin, auth):
    c = client.post(f"{API}/admin/courses", json={"slug": "py2", "title": "Py2", "runtime": "python",
                                                  "unlock_mode": "by_module", "published": True}, headers=admin).json()
    ids = []
    for m in range(2):
        mod = client.post(f"{API}/admin/modules", json={"course_id": c["id"], "title": f"Level {m}"}, headers=admin).json()
        for n in range(2):
            ids.append(client.post(f"{API}/admin/lessons", json={
                "module_id": mod["id"], "title": f"L{m}{n}", "concept": "c", "prompt": "print hi", "solution": "print('hi')",
                "published": True}, headers=admin).json()["id"])
    send = lambda lid: client.post(f"{API}/submissions", json={"lesson_id": lid, "sql": "print('hi')"}, headers=auth).status_code
    assert send(ids[0]) == 200      # first lesson of level 0
    assert send(ids[3]) == 403      # second lesson of level 1 still needs the first
    assert send(ids[2]) == 200      # level 1 opens without finishing level 0
    assert send(ids[3]) == 200
