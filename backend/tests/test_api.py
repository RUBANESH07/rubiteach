import json
from types import SimpleNamespace

from app.grader import grade, run_sql
from app.services.lessons import SEED_FILE


def lessons():
    return {l["id"]: l for l in json.loads(SEED_FILE.read_text(encoding="utf-8"))}


API = "/api/v1"


def submit(client, auth, lesson_id, sql):
    return client.post(f"{API}/submissions", json={"lesson_id": lesson_id, "sql": sql}, headers=auth)


def test_every_reference_solution_passes_and_select_1_fails():
    for lid, lesson in lessons().items():
        assert grade(SimpleNamespace(**lesson), lesson["solution"])[0], f"lesson {lid} solution rejected"
        assert not grade(SimpleNamespace(**lesson), "SELECT 1")[0], f"lesson {lid} accepts a wrong answer"


def test_register_login_me(client):
    body = {"username": "bob", "email": "Bob@Example.com", "password": "password123"}
    assert client.post(f"{API}/auth/register", json=body).status_code == 201
    assert client.post(f"{API}/auth/register", json=body).status_code == 409
    r = client.post(f"{API}/auth/login", json={"email": "bob@example.com", "password": "password123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert "password" not in r.text
    me = client.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["username"] == "bob" and me.json()["role"] == "student"


def test_bad_login_and_validation(client):
    assert client.post(f"{API}/auth/login", json={"email": "x@y.com", "password": "nope"}).status_code == 401
    weak = {"username": "a", "email": "bad", "password": "short"}
    assert client.post(f"{API}/auth/register", json=weak).status_code == 422


def test_protected_routes_need_token(client):
    assert client.get(f"{API}/progress").status_code == 401
    assert client.post(f"{API}/submissions", json={"lesson_id": 1, "sql": "SELECT 1"}).status_code == 401
    assert client.get(f"{API}/progress", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_correct_submission_awards_xp_once(client, auth):
    first = submit(client, auth, 1, "select * from departments").json()
    assert first["passed"] and first["xp_awarded"] == 10 and "first" in first["new_badges"]
    again = submit(client, auth, 1, "SELECT * FROM departments;").json()
    assert again["passed"] and again["xp_awarded"] == 0
    assert again["progress"]["xp"] == 10 and again["progress"]["streak"] == 1


def test_wrong_submission_gives_feedback_and_no_xp(client, auth):
    r = submit(client, auth, 1, "SELECT name FROM departments").json()
    assert not r["passed"] and r["xp_awarded"] == 0 and "column" in r["message"]
    err = submit(client, auth, 1, "SELEC oops").json()
    assert not err["passed"] and "error" in err["message"].lower()


def test_client_cannot_claim_xp_directly(client, auth):
    r = client.post(f"{API}/submissions", json={"lesson_id": 1, "sql": "SELECT 1", "xp": 9999, "passed": True}, headers=auth)
    assert r.json()["xp_awarded"] == 0
    assert client.get(f"{API}/progress", headers=auth).json()["xp"] == 0


def test_lessons_unlock_in_order(client, auth):
    assert submit(client, auth, 2, "SELECT name, salary FROM employees").status_code == 403
    assert client.post(f"{API}/lessons/2/hint", headers=auth).status_code == 403
    assert submit(client, auth, 999, "SELECT 1").status_code == 404


def test_hint_halves_xp(client, auth):
    h = client.post(f"{API}/lessons/1/hint", headers=auth).json()
    assert h["level"] == 1 and h["total"] >= 1 and h["hint"]
    r = submit(client, auth, 1, "SELECT * FROM departments").json()
    assert r["xp_awarded"] == 5
    assert client.get(f"{API}/hints/1", headers=auth).json() == [h["hint"]]


def test_full_course_flow_badges_and_leaderboard(client, auth):
    for lid, lesson in lessons().items():
        r = submit(client, auth, lid, lesson["solution"]).json()
        assert r["passed"], (lid, r["message"])
    p = client.get(f"{API}/progress", headers=auth).json()
    assert len(p["completed"]) == len(lessons())
    assert p["xp"] == sum(l["xp"] for l in lessons().values())
    assert {"first", "five", "xp100", "join", "window", "all"} <= set(p["badges"])
    board = client.get(f"{API}/leaderboard", headers=auth).json()
    assert board[0]["username"] == "ada" and board[0]["rank"] == 1


def test_sandbox_blocks_attach_and_pragma():
    assert not run_sql("ATTACH DATABASE 'x.db' AS x").ok
    assert not run_sql("PRAGMA table_info(employees)").ok


def test_sandbox_stops_runaway_query(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "query_timeout_seconds", 0.3)
    res = run_sql("WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM r) SELECT count(*) FROM r")
    assert not res.ok and "too long" in res.error


def test_sandbox_isolated_between_runs():
    assert run_sql("DELETE FROM employees").ok
    assert run_sql("SELECT COUNT(*) FROM employees").rows == [[12]]


def test_semicolon_inside_string_is_not_split():
    res = run_sql("SELECT 'a;b' AS x")
    assert res.ok and res.rows == [["a;b"]]
