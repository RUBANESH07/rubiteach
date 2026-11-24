API = "/api/v1"
NEWBIE = {"username": "newbie", "email": "n@x.com", "password": "password123", "role": "student"}


def _uid(client, admin, username):
    items = client.get(f"{API}/admin/students", headers=admin).json()["items"]
    return next(i["id"] for i in items if i["username"] == username)


def test_user_management_requires_admin(client, auth):
    assert client.post(f"{API}/admin/users", json=NEWBIE, headers=auth).status_code == 403
    assert client.delete(f"{API}/admin/users/00000000-0000-0000-0000-000000000000", headers=auth).status_code == 403


def test_admin_creates_user_and_manages_role(client, admin):
    r = client.post(f"{API}/admin/users", json=NEWBIE, headers=admin)
    assert r.status_code == 201 and r.json()["role"] == "student" and "password" not in str(r.json())
    uid = r.json()["id"]
    assert client.post(f"{API}/admin/users", json={**NEWBIE, "email": "z@x.com"}, headers=admin).status_code == 409
    assert client.post(f"{API}/admin/users/{uid}/role", json={"role": "admin"}, headers=admin).json()["role"] == "admin"
    assert client.post(f"{API}/admin/users/{uid}/role", json={"role": "student"}, headers=admin).json()["role"] == "student"
    assert client.post(f"{API}/admin/users/{uid}/role", json={"role": "root"}, headers=admin).status_code == 422
    assert client.post(f"{API}/admin/users/not-a-uuid/role", json={"role": "admin"}, headers=admin).status_code == 404


def test_disable_blocks_login_and_existing_token(client, admin, auth):
    uid = _uid(client, admin, "ada")
    assert client.post(f"{API}/admin/users/{uid}/active", json={"active": False}, headers=admin).json()["is_active"] is False
    assert client.get(f"{API}/progress", headers=auth).status_code == 403
    assert client.post(f"{API}/auth/login", json={"email": "ada@example.com", "password": "password123"}).status_code == 403
    client.post(f"{API}/admin/users/{uid}/active", json={"active": True}, headers=admin)
    assert client.post(f"{API}/auth/login", json={"email": "ada@example.com", "password": "password123"}).status_code == 200


def test_reset_password(client, admin, auth):
    uid = _uid(client, admin, "ada")
    assert client.post(f"{API}/admin/users/{uid}/reset-password", json={"password": "short"}, headers=admin).status_code == 422
    assert client.post(f"{API}/admin/users/{uid}/reset-password", json={"password": "brandnew123"}, headers=admin).status_code == 200
    assert client.post(f"{API}/auth/login", json={"email": "ada@example.com", "password": "password123"}).status_code == 401
    assert client.post(f"{API}/auth/login", json={"email": "ada@example.com", "password": "brandnew123"}).status_code == 200


def test_reset_progress_and_delete(client, admin, auth):
    client.post(f"{API}/submissions", json={"lesson_id": 1, "sql": "SELECT * FROM departments"}, headers=auth)
    uid = _uid(client, admin, "ada")
    r = client.post(f"{API}/admin/users/{uid}/reset-progress", headers=admin).json()
    assert r["xp"] == 0 and r["streak"] == 0
    p = client.get(f"{API}/progress", headers=auth).json()
    assert p["completed"] == {} and p["badges"] == []
    again = client.post(f"{API}/submissions", json={"lesson_id": 1, "sql": "SELECT * FROM departments"}, headers=auth).json()
    assert again["xp_awarded"] == 10  # XP can be earned again after a reset
    assert client.delete(f"{API}/admin/users/{uid}", headers=admin).status_code == 204
    assert client.get(f"{API}/progress", headers=auth).status_code == 401
    assert client.delete(f"{API}/admin/users/{uid}", headers=admin).status_code == 404


def test_admin_cannot_lock_themselves_out(client, admin):
    me = _uid(client, admin, "boss")
    assert client.delete(f"{API}/admin/users/{me}", headers=admin).status_code == 400
    assert client.post(f"{API}/admin/users/{me}/active", json={"active": False}, headers=admin).status_code == 400
    assert client.post(f"{API}/admin/users/{me}/role", json={"role": "student"}, headers=admin).status_code == 400
    other = client.post(f"{API}/admin/users", json={**NEWBIE, "username": "second", "email": "s@x.com", "role": "admin"}, headers=admin).json()["id"]
    login = client.post(f"{API}/auth/login", json={"email": "s@x.com", "password": "password123"}).json()
    h2 = {"Authorization": "Bearer " + login["access_token"]}
    assert client.post(f"{API}/admin/users/{me}/role", json={"role": "student"}, headers=h2).status_code == 200
    assert client.post(f"{API}/admin/users/{other}/role", json={"role": "student"}, headers=h2).status_code == 400  # self


def test_last_admin_cannot_be_demoted_by_another_admin(client, admin):
    boss = _uid(client, admin, "boss")
    second = client.post(f"{API}/admin/users", json={**NEWBIE, "username": "second", "email": "s@x.com", "role": "admin"}, headers=admin).json()["id"]
    h2 = {"Authorization": "Bearer " + client.post(f"{API}/auth/login", json={"email": "s@x.com", "password": "password123"}).json()["access_token"]}
    client.post(f"{API}/admin/users/{boss}/active", json={"active": False}, headers=h2)  # boss disabled -> second is the only active admin
    assert client.post(f"{API}/admin/users/{boss}/role", json={"role": "student"}, headers=h2).status_code == 200
    assert second  # second remains admin; they cannot demote themselves
    assert client.post(f"{API}/admin/users/{second}/role", json={"role": "student"}, headers=h2).status_code == 400


def test_admin_bypasses_lesson_lock_and_is_off_leaderboard(client, admin, auth):
    sql = "SELECT name, salary FROM employees ORDER BY salary DESC"
    r = client.post(f"{API}/submissions", json={"lesson_id": 5, "sql": sql}, headers=admin)
    assert r.status_code == 200 and r.json()["passed"]
    client.post(f"{API}/submissions", json={"lesson_id": 1, "sql": "SELECT * FROM departments"}, headers=auth)
    names = [x["username"] for x in client.get(f"{API}/leaderboard", headers=auth).json()]
    assert names == ["ada"]
