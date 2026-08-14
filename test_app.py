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
        "{% for m in get_flashed_messages() %}{{ m }}{% endfor %}"
        "{{ username }}"
        "{% if active_tag %}[filter:{{ active_tag.name }}]{% endif %}"
        "{% for tag in tags %}<b>{{ tag.name }}</b>{% endfor %}"
        "{% for t in todos %}<div>{{ t.title }}:{{ t.status }}:{{ t.tag_name or '' }}</div>{% endfor %}"
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


def add_tag(client, name="work"):
    client.post("/tags/add", data={"name": name})
    with app_module.app.app_context():
        row = app_module.get_db().execute(
            "SELECT id FROM tags WHERE name = ? ORDER BY id DESC LIMIT 1", (name,)
        ).fetchone()
    return row["id"] if row else None


def todo_tag_id(todo_id):
    with app_module.app.app_context():
        row = app_module.get_db().execute(
            "SELECT tag_id FROM todos WHERE id = ?", (todo_id,)
        ).fetchone()
    return row["tag_id"]


def tag_count(name=None):
    with app_module.app.app_context():
        if name is None:
            q, params = "SELECT COUNT(*) c FROM tags", ()
        else:
            q, params = "SELECT COUNT(*) c FROM tags WHERE name = ?", (name,)
        return app_module.get_db().execute(q, params).fetchone()["c"]


# --- 1. /tags/add ---

def test_tags_add_success(client):
    register(client)
    login(client)
    resp = client.post("/tags/add", data={"name": "  work  "}, follow_redirects=True)
    assert "已建立標籤「work」".encode() in resp.data
    assert tag_count("work") == 1


def test_tags_add_invalid_names_flash_redirect(client):
    register(client)
    login(client)
    for bad in ["", "   ", "x" * 31]:
        resp = client.post("/tags/add", data={"name": bad}, follow_redirects=False)
        assert resp.status_code == 302
    assert tag_count() == 0


def test_tags_add_duplicate_same_user_rejected(client):
    register(client)
    login(client)
    add_tag(client, "work")
    resp = client.post("/tags/add", data={"name": "work"}, follow_redirects=True)
    assert "標籤名稱重複".encode() in resp.data
    assert tag_count("work") == 1


def test_tags_add_same_name_different_users_ok(client):
    register(client, "userone", "password123")
    login(client, "userone", "password123")
    add_tag(client, "work")
    client.post("/logout")
    register(client, "usertwo", "password123")
    login(client, "usertwo", "password123")
    add_tag(client, "work")
    assert tag_count("work") == 2


def test_tags_routes_require_login(client):
    for path in ["/tags/add", "/tags/delete/1"]:
        resp = client.post(path, follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/login")


# --- 2. /tags/delete ---

def test_tags_delete_own_nulls_todos(client):
    register(client)
    login(client)
    tag_id = add_tag(client, "work")
    client.post("/add", data={"title": "tagged", "tag_id": str(tag_id)})
    todo_id = add_todo(client, "tagged2")
    client.post(f"/edit/{todo_id}", data={"title": "tagged2", "tag_id": str(tag_id)})
    resp = client.post(f"/tags/delete/{tag_id}")
    assert resp.status_code == 302
    assert tag_count("work") == 0
    assert todo_tag_id(todo_id) is None
    assert todo_title(todo_id) == "tagged2"


def test_tags_delete_others_404(client):
    register(client, "owner", "password123")
    login(client, "owner", "password123")
    tag_id = add_tag(client, "work")
    client.post("/logout")
    register(client, "intruder", "password123")
    login(client, "intruder", "password123")
    resp = client.post(f"/tags/delete/{tag_id}")
    assert resp.status_code == 404
    assert tag_count("work") == 1


# --- 3. /add 帶 tag_id ---

def test_add_with_own_tag(client):
    register(client)
    login(client)
    tag_id = add_tag(client, "work")
    client.post("/add", data={"title": "t", "tag_id": str(tag_id)})
    with app_module.app.app_context():
        row = app_module.get_db().execute(
            "SELECT tag_id FROM todos ORDER BY id DESC LIMIT 1"
        ).fetchone()
    assert row["tag_id"] == tag_id


def test_add_with_invalid_tag_silently_null(client):
    register(client, "owner", "password123")
    login(client, "owner", "password123")
    other_tag = add_tag(client, "work")
    client.post("/logout")
    register(client, "usertwo", "password123")
    login(client, "usertwo", "password123")
    for bad in [str(other_tag), "9999", "abc", ""]:
        client.post("/add", data={"title": "t", "tag_id": bad})
        with app_module.app.app_context():
            row = app_module.get_db().execute(
                "SELECT id, tag_id FROM todos ORDER BY id DESC LIMIT 1"
            ).fetchone()
        assert row["tag_id"] is None


# --- 4. /edit 帶 tag_id ---

def test_edit_updates_title_and_tag(client):
    register(client)
    login(client)
    tag_id = add_tag(client, "work")
    todo_id = add_todo(client, "old")
    resp = client.post(f"/edit/{todo_id}", data={"title": "new", "tag_id": str(tag_id)})
    assert resp.status_code == 302
    assert todo_title(todo_id) == "new"
    assert todo_tag_id(todo_id) == tag_id


def test_edit_empty_tag_sets_null(client):
    register(client)
    login(client)
    tag_id = add_tag(client, "work")
    todo_id = add_todo(client, "t")
    client.post(f"/edit/{todo_id}", data={"title": "t", "tag_id": str(tag_id)})
    assert todo_tag_id(todo_id) == tag_id
    client.post(f"/edit/{todo_id}", data={"title": "t", "tag_id": ""})
    assert todo_tag_id(todo_id) is None


def test_edit_with_others_tag_silently_null(client):
    register(client, "owner", "password123")
    login(client, "owner", "password123")
    other_tag = add_tag(client, "work")
    client.post("/logout")
    register(client, "usertwo", "password123")
    login(client, "usertwo", "password123")
    todo_id = add_todo(client, "t")
    resp = client.post(f"/edit/{todo_id}", data={"title": "t2", "tag_id": str(other_tag)})
    assert resp.status_code == 302
    assert todo_title(todo_id) == "t2"
    assert todo_tag_id(todo_id) is None


# --- 5. GET /?tag_id= 篩選 ---

def test_index_filter_by_tag(client):
    register(client)
    login(client)
    tag_id = add_tag(client, "work")
    client.post("/add", data={"title": "tagged one", "tag_id": str(tag_id)})
    add_todo(client, "untagged one")
    resp = client.get(f"/?tag_id={tag_id}")
    assert b"tagged one" in resp.data
    assert b"untagged one" not in resp.data
    assert "[filter:work]".encode() in resp.data
    resp = client.get("/")
    assert b"tagged one" in resp.data
    assert b"untagged one" in resp.data


def test_index_invalid_filter_shows_all(client):
    register(client, "owner", "password123")
    login(client, "owner", "password123")
    other_tag = add_tag(client, "work")
    client.post("/logout")
    register(client, "usertwo", "password123")
    login(client, "usertwo", "password123")
    add_todo(client, "mine")
    for bad in [str(other_tag), "9999", "abc"]:
        resp = client.get(f"/?tag_id={bad}")
        assert b"mine" in resp.data
        assert b"[filter:" not in resp.data


# --- 6. migration ---

def test_init_db_migrates_legacy_db(tmp_path, monkeypatch):
    import sqlite3

    legacy = tmp_path / "legacy.db"
    with sqlite3.connect(legacy) as db:
        db.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, "
            "is_admin INTEGER NOT NULL DEFAULT 0, "
            "created_at TEXT NOT NULL DEFAULT (datetime('now')))"
        )
        db.execute(
            "CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "user_id INTEGER NOT NULL REFERENCES users(id), title TEXT NOT NULL, "
            "status TEXT NOT NULL DEFAULT 'pending', "
            "created_at TEXT NOT NULL DEFAULT (datetime('now')))"
        )
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES ('old', 'hash')"
        )
        db.execute("INSERT INTO todos (user_id, title) VALUES (1, 'legacy task')")

    monkeypatch.setattr(app_module, "DB_PATH", str(legacy))
    app_module.init_db()
    app_module.init_db()  # idempotent: tag_id 已存在時不能炸

    with sqlite3.connect(legacy) as db:
        db.row_factory = sqlite3.Row
        cols = [r[1] for r in db.execute("PRAGMA table_info(todos)")]
        assert "tag_id" in cols
        row = db.execute("SELECT title, tag_id FROM todos").fetchone()
        assert row["title"] == "legacy task"
        assert row["tag_id"] is None
        assert db.execute(
            "SELECT COUNT(*) FROM tags"
        ).fetchone()[0] == 0


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
