API = "/api/v1"

NEW = {
    "module_id": 1, "title": "Counting rows", "minutes": 4, "xp": 12,
    "concept": "Use <b>COUNT</b> to count. <script>alert(1)</script>", "why": "Totals matter.",
    "example_sql": "SELECT COUNT(*) FROM products;", "example_note": "Counts products.",
    "prompt": "Count the products.", "starter": "SELECT ", "solution": "SELECT COUNT(*) FROM products;",
    "hints": ["Use COUNT(*)."], "published": False,
}


def test_students_cannot_use_admin_api(client, auth):
    assert client.get(f"{API}/admin/lessons", headers=auth).status_code == 403
    assert client.post(f"{API}/admin/lessons", json=NEW, headers=auth).status_code == 403
    assert client.get(f"{API}/admin/students", headers=auth).status_code == 403
    assert client.get(f"{API}/admin/lessons").status_code == 401


def test_admin_lists_seeded_lessons_with_solutions(client, admin):
    rows = client.get(f"{API}/admin/lessons", params={"course_id": 1}, headers=admin).json()
    assert len(rows) == 17 and rows[0]["solution"] and rows[0]["hints"]


def test_public_lessons_hide_answers(client, auth):
    rows = client.get(f"{API}/lessons", headers=auth).json()
    assert len(rows) == 17 + 113
    for r in rows:
        assert not {"solution", "hints", "verify", "tests"} & set(r)


def test_seeded_python_course(client, auth, admin):
    courses = {c["slug"]: c for c in client.get(f"{API}/courses", headers=auth).json()}
    py = courses["python"]
    assert py["runtime"] == "python" and py["unlock_mode"] == "by_module" and py["lessons"] == 113 and len(py["modules"]) == 8
    assert [m["title"][:7] for m in py["modules"]] == [f"Level {i}" for i in range(1, 9)]
    rows = client.get(f"{API}/admin/lessons", params={"course_id": py["id"]}, headers=admin).json()
    assert all(r["tests"] and r["tests"]["cases"] and r["solution"] for r in rows)
    # every level opens without finishing the previous one: first lesson of Level 5 is submittable
    first = {}
    for r in rows:
        first.setdefault(r["module_id"], r)
    lvl5 = first[py["modules"][4]["id"]]
    res = client.post(f"{API}/submissions", json={"lesson_id": lvl5["id"], "sql": "pass"}, headers=auth)
    assert res.status_code == 200 and res.json()["passed"] is False
    second = [r for r in rows if r["module_id"] == lvl5["module_id"]][1]
    assert client.post(f"{API}/submissions", json={"lesson_id": second["id"], "sql": "pass"}, headers=auth).status_code == 403


def test_create_draft_is_hidden_until_published(client, admin, auth):
    r = client.post(f"{API}/admin/lessons", json=NEW, headers=admin)
    assert r.status_code == 201
    lid = r.json()["id"]
    assert "<script>" not in r.json()["concept"] and "&lt;script&gt;" in r.json()["concept"]
    assert "<b>COUNT</b>" in r.json()["concept"]
    assert lid not in [l["id"] for l in client.get(f"{API}/lessons", headers=auth).json()]
    assert client.post(f"{API}/submissions", json={"lesson_id": lid, "sql": "SELECT 1"}, headers=auth).status_code == 404
    client.post(f"{API}/admin/lessons/{lid}/publish", json={"published": True}, headers=admin)
    assert lid in [l["id"] for l in client.get(f"{API}/lessons", headers=auth).json()]
    # still locked behind lesson 17 for a fresh student
    assert client.post(f"{API}/submissions", json={"lesson_id": lid, "sql": "SELECT 1"}, headers=auth).status_code == 403


def test_bad_solution_is_rejected(client, admin):
    bad = {**NEW, "solution": "SELEC nonsense"}
    r = client.post(f"{API}/admin/lessons", json=bad, headers=admin)
    assert r.status_code == 422 and "Solution failed" in r.json()["detail"]
    no_result = {**NEW, "solution": "DELETE FROM orders"}
    assert client.post(f"{API}/admin/lessons", json=no_result, headers=admin).status_code == 422
    assert client.post(f"{API}/admin/lessons", json={**NEW, "module_id": 9999}, headers=admin).status_code == 422


def test_update_and_selfcheck(client, admin):
    lid = client.post(f"{API}/admin/lessons", json=NEW, headers=admin).json()["id"]
    upd = client.put(f"{API}/admin/lessons/{lid}", json={**NEW, "title": "Counting everything", "xp": 20}, headers=admin)
    assert upd.json()["title"] == "Counting everything" and upd.json()["xp"] == 20
    assert client.post(f"{API}/admin/lessons/{lid}/check", headers=admin).json()["ok"] is True
    assert client.put(f"{API}/admin/lessons/9999", json=NEW, headers=admin).status_code == 404


def test_unpublish_keeps_progress_and_all_badge_uses_published(client, admin, auth):
    client.post(f"{API}/submissions", json={"lesson_id": 1, "sql": "SELECT * FROM departments"}, headers=auth)
    client.post(f"{API}/admin/lessons/1/publish", json={"published": False}, headers=admin)
    ids = [l["id"] for l in client.get(f"{API}/lessons", headers=auth).json()]
    assert 1 not in ids
    assert client.get(f"{API}/progress", headers=auth).json()["completed"] == {"1": 10}
    # lesson 2 becomes the first published lesson, so it is unlocked
    r = client.post(f"{API}/submissions", json={"lesson_id": 2, "sql": "SELECT name, salary FROM employees"}, headers=auth)
    assert r.json()["passed"]


def test_students_and_stats(client, admin, auth):
    client.post(f"{API}/submissions", json={"lesson_id": 1, "sql": "SELECT * FROM departments"}, headers=auth)
    client.post(f"{API}/submissions", json={"lesson_id": 1, "sql": "SELECT 1"}, headers=auth)
    s = client.get(f"{API}/admin/students", headers=admin).json()
    ada = next(i for i in s["items"] if i["username"] == "ada")
    assert s["total"] == 2 and ada["xp"] == 10 and ada["lessons_completed"] == 1
    assert "password_hash" not in str(s)
    st = client.get(f"{API}/admin/stats", headers=admin).json()
    assert st["students"] == 1 and st["submissions"] == 2 and st["pass_rate"] == 0.5
    assert st["lessons"][0]["completions"] == 1 and st["lessons"][0]["attempts"] == 2


COURSE = {"slug": "javascript", "title": "JavaScript", "description": "Learn JS.", "icon": "🟨", "runtime": "javascript"}


def test_runtimes_listing(client, admin):
    r = client.get(f"{API}/admin/runtimes", headers=admin).json()
    assert [x["key"] for x in r["available"]] == ["sql", "python"] and "javascript" in r["planned"]


def test_unavailable_runtime_course_can_be_drafted_but_not_published_yet(client, admin, auth):
    r = client.post(f"{API}/admin/courses", json=COURSE, headers=admin)
    assert r.status_code == 201 and r.json()["runtime_available"] is False
    cid = r.json()["id"]
    assert client.post(f"{API}/admin/courses/{cid}/publish", json={"published": True}, headers=admin).status_code == 422
    assert client.post(f"{API}/admin/courses", json={**COURSE, "published": True}, headers=admin).status_code == 422
    assert client.post(f"{API}/admin/courses", json=COURSE, headers=admin).status_code == 409  # slug taken
    mod = client.post(f"{API}/admin/modules", json={"course_id": cid, "title": "Basics"}, headers=admin)
    assert mod.status_code == 201
    lesson = {**NEW, "module_id": mod.json()["id"]}
    assert client.post(f"{API}/admin/lessons", json=lesson, headers=admin).status_code == 422  # no runtime yet
    assert "javascript" not in [c["slug"] for c in client.get(f"{API}/courses", headers=auth).json()]


def test_second_sql_course_is_independent(client, admin, auth):
    c = client.post(f"{API}/admin/courses", json={**COURSE, "slug": "sql-advanced", "title": "SQL Advanced", "runtime": "sql", "published": True}, headers=admin).json()
    m = client.post(f"{API}/admin/modules", json={"course_id": c["id"], "title": "Tuning"}, headers=admin).json()
    l = client.post(f"{API}/admin/lessons", json={**NEW, "module_id": m["id"], "published": True}, headers=admin).json()
    assert l["course_id"] == c["id"]
    courses = client.get(f"{API}/courses", headers=auth).json()
    assert [x["slug"] for x in courses] == ["sql", "python", "sql-advanced"] and courses[0]["lessons"] == 17 and courses[2]["lessons"] == 1
    # the first lesson of a different course is unlocked without finishing the SQL course
    r = client.post(f"{API}/submissions", json={"lesson_id": l["id"], "sql": "SELECT COUNT(*) FROM products"}, headers=auth).json()
    assert r["passed"]
    only = client.get(f"{API}/lessons", params={"course_id": c["id"]}, headers=auth).json()
    assert [x["id"] for x in only] == [l["id"]]


def test_students_cannot_manage_courses(client, auth):
    assert client.post(f"{API}/admin/courses", json=COURSE, headers=auth).status_code == 403
    assert client.get(f"{API}/admin/modules", headers=auth).status_code == 403
