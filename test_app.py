import os

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "adminpass123")

import pytest
from jinja2 import DictLoader

import app as app_module

# Backend tests own app.py logic only; templates/ belongs to the frontend
# lane and doesn't exist in this worktree, so routes render against a
# minimal stub loader instead of the real templates.
STUB_TEMPLATES = {
    "register.html": "{% for m in get_flashed_messages() %}{{ m }}{% endfor %}",
    "login.html": "{% for m in get_flashed_messages() %}{{ m }}{% endfor %}",
    "index.html": (
        "{{ username }}"
        "{% for t in todos %}<div>{{ t.title }}:{{ t.status }}</div>{% endfor %}"
    ),
    "admin.html": (
        "{% for u in users %}<div>{{ u.username }}"
        "{% for t in u.todos %}<span>{{ t.title }}:{{ t.status }}</span>{% endfor %}"
        "</div>{% endfor %}"
    ),
}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "DB_PATH", str(tmp_path / "test.db"))
    app_module.app.config.update(TESTING=True)
    app_module.app.jinja_env.loader = DictLoader(STUB_TEMPLATES)
    app_module.init_db()
    with app_module.app.test_client() as c:
        yield c


def register(client, username="alice", password="password123"):
    return client.post(
        "/register",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


def login(client, username="alice", password="password123"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


def todo_status(todo_id):
    with app_module.app.app_context():
        row = app_module.get_db().execute(
            "SELECT status FROM todos WHERE id = ?", (todo_id,)
        ).fetchone()
    return row["status"]


def test_register_login_add_toggle_logout(client):
    resp = register(client)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

    resp = login(client)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")

    resp = client.post("/add", data={"title": "buy milk"}, follow_redirects=False)
    assert resp.status_code == 302

    with app_module.app.app_context():
        todo = app_module.get_db().execute("SELECT id, status FROM todos").fetchone()
    todo_id = todo["id"]
    assert todo["status"] == "pending"

    client.post(f"/status/{todo_id}")
    assert todo_status(todo_id) == "in_progress"

    client.post(f"/status/{todo_id}")
    assert todo_status(todo_id) == "done"

    client.post(f"/status/{todo_id}")
    assert todo_status(todo_id) == "pending"

    resp = client.post("/logout", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")


def test_duplicate_username_rejected(client):
    register(client, "bob", "password123")
    resp = register(client, "bob", "password123")
    assert resp.status_code == 200

    with app_module.app.app_context():
        count = app_module.get_db().execute(
            "SELECT COUNT(*) c FROM users WHERE username = ?", ("bob",)
        ).fetchone()["c"]
    assert count == 1


def test_short_password_rejected(client):
    resp = register(client, "carol", "short")
    assert resp.status_code == 200

    with app_module.app.app_context():
        user = app_module.get_db().execute(
            "SELECT id FROM users WHERE username = ?", ("carol",)
        ).fetchone()
    assert user is None


def test_index_requires_login(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")


def add_todo(client, title="task"):
    client.post("/add", data={"title": title})
    with app_module.app.app_context():
        row = app_module.get_db().execute(
            "SELECT id FROM todos ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return row["id"]


def todo_title(todo_id):
    with app_module.app.app_context():
        row = app_module.get_db().execute(
            "SELECT title FROM todos WHERE id = ?", (todo_id,)
        ).fetchone()
    return row["title"] if row else None


def test_edit_own_todo(client):
    register(client)
    login(client)
    todo_id = add_todo(client, "old title")
    resp = client.post(f"/edit/{todo_id}", data={"title": "new title"})
    assert resp.status_code == 302
    assert todo_title(todo_id) == "new title"


def test_edit_invalid_title_rejected(client):
    register(client)
    login(client)
    todo_id = add_todo(client, "keep me")
    for bad in ["", "   ", "x" * 201]:
        resp = client.post(f"/edit/{todo_id}", data={"title": bad})
        assert resp.status_code == 302
        assert todo_title(todo_id) == "keep me"


def test_edit_others_todo_404(client):
    register(client, "owner", "password123")
    login(client, "owner", "password123")
    todo_id = add_todo(client, "owner task")
    client.post("/logout")

    register(client, "intruder", "password123")
    login(client, "intruder", "password123")
    resp = client.post(f"/edit/{todo_id}", data={"title": "hacked"})
    assert resp.status_code == 404
    assert todo_title(todo_id) == "owner task"


def test_delete_own_todo(client):
    register(client)
    login(client)
    todo_id = add_todo(client)
    resp = client.post(f"/delete/{todo_id}")
    assert resp.status_code == 302
    assert todo_title(todo_id) is None


def test_delete_others_todo_404(client):
    register(client, "owner", "password123")
    login(client, "owner", "password123")
    todo_id = add_todo(client, "owner task")
    client.post("/logout")

    register(client, "intruder", "password123")
    login(client, "intruder", "password123")
    resp = client.post(f"/delete/{todo_id}")
    assert resp.status_code == 404
    assert todo_title(todo_id) == "owner task"


def test_edit_delete_require_login(client):
    for path in ["/edit/1", "/delete/1"]:
        resp = client.post(path, follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/login")


def test_admin_forbidden_for_non_admin(client):
    register(client, "dave", "password123")
    login(client, "dave", "password123")
    resp = client.get("/admin")
    assert resp.status_code == 403


def test_admin_sees_other_users_todos(client):
    register(client, "eve", "password123")
    login(client, "eve", "password123")
    client.post("/add", data={"title": "eve task"})
    client.post("/logout")

    login(client, os.environ["ADMIN_USERNAME"], os.environ["ADMIN_PASSWORD"])
    resp = client.get("/admin")
    assert resp.status_code == 200
    assert b"eve" in resp.data
    assert b"eve task" in resp.data
