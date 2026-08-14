import os
import re
import sqlite3
from functools import wraps

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

DB_PATH = "todo.db"
STATUS_CYCLE = ["pending", "in_progress", "done"]

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def validate_username(username):
    if not username:
        return False, "帳號必填"
    if not re.fullmatch(r"[A-Za-z0-9_]{3,30}", username):
        return False, "帳號需為 3-30 碼英數字或底線"
    return True, ""


def validate_password(password):
    if not password or len(password) < 8:
        return False, "密碼至少需要 8 碼"
    return True, ""


def validate_title(title):
    title = (title or "").strip()
    if not title:
        return False, "標題必填"
    if len(title) > 200:
        return False, "標題長度上限 200 字"
    return True, ""


def validate_tag_name(name):
    name = (name or "").strip()
    if not name:
        return False, "標籤名稱必填"
    if len(name) > 30:
        return False, "標籤名稱長度上限 30 字"
    return True, ""


def resolve_tag_id(db, raw, user_id):
    """選填 tag_id 表單值 → 自己的 tag id 或 None（非法/非本人/非數字靜默忽略）。"""
    if not raw or not str(raw).isdigit():
        return None
    tag = db.execute(
        "SELECT id FROM tags WHERE id = ? AND user_id = ?", (int(raw), user_id)
    ).fetchone()
    return tag["id"] if tag else None


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','in_progress','done')),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(user_id, name)
            )
            """
        )
        todo_columns = [r[1] for r in db.execute("PRAGMA table_info(todos)")]
        if "tag_id" not in todo_columns:
            db.execute("ALTER TABLE todos ADD COLUMN tag_id INTEGER REFERENCES tags(id)")
        admin_username = os.environ["ADMIN_USERNAME"]
        admin_password = os.environ["ADMIN_PASSWORD"]
        existing = db.execute(
            "SELECT id FROM users WHERE username = ?", (admin_username,)
        ).fetchone()
        if existing is None:
            db.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)",
                (admin_username, generate_password_hash(admin_password)),
            )


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        ok, msg = validate_username(username)
        if ok:
            ok, msg = validate_password(password)
        if ok:
            existing = get_db().execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone()
            if existing is not None:
                ok, msg = False, "帳號已被使用"

        if not ok:
            flash(msg)
            return render_template("register.html")

        get_db().execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        get_db().commit()
        flash("註冊成功，請登入")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("帳號或密碼錯誤")
            return render_template("login.html")
        session["user_id"] = user["id"]
        session["is_admin"] = bool(user["is_admin"])
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    db = get_db()
    active_tag = None
    raw = request.args.get("tag_id")
    tag_filter_id = resolve_tag_id(db, raw, session["user_id"])
    if tag_filter_id is not None:
        active_tag = db.execute(
            "SELECT id, name FROM tags WHERE id = ?", (tag_filter_id,)
        ).fetchone()
    query = (
        "SELECT t.id, t.title, t.status, t.created_at, t.tag_id, tags.name AS tag_name "
        "FROM todos t LEFT JOIN tags ON t.tag_id = tags.id "
        "WHERE t.user_id = ?"
    )
    params = [session["user_id"]]
    if tag_filter_id is not None:
        query += " AND t.tag_id = ?"
        params.append(tag_filter_id)
    todos = db.execute(query + " ORDER BY t.id DESC", params).fetchall()
    tags = db.execute(
        "SELECT id, name FROM tags WHERE user_id = ? ORDER BY name",
        (session["user_id"],),
    ).fetchall()
    user = db.execute(
        "SELECT username FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()
    return render_template(
        "index.html",
        todos=todos,
        tags=tags,
        active_tag=active_tag,
        username=user["username"],
    )


@app.route("/add", methods=["POST"])
@login_required
def add():
    title = request.form.get("title", "")
    ok, msg = validate_title(title)
    if not ok:
        flash(msg)
        return redirect(url_for("index"))
    db = get_db()
    tag_id = resolve_tag_id(db, request.form.get("tag_id"), session["user_id"])
    db.execute(
        "INSERT INTO todos (user_id, title, tag_id) VALUES (?, ?, ?)",
        (session["user_id"], title.strip(), tag_id),
    )
    db.commit()
    return redirect(url_for("index"))


@app.route("/tags/add", methods=["POST"])
@login_required
def add_tag():
    name = request.form.get("name", "").strip()
    ok, msg = validate_tag_name(name)
    if ok:
        existing = get_db().execute(
            "SELECT id FROM tags WHERE user_id = ? AND name = ?",
            (session["user_id"], name),
        ).fetchone()
        if existing is not None:
            ok, msg = False, "標籤名稱重複"
    if not ok:
        flash(msg)
        return redirect(url_for("index"))
    get_db().execute(
        "INSERT INTO tags (user_id, name) VALUES (?, ?)", (session["user_id"], name)
    )
    get_db().commit()
    flash(f"已建立標籤「{name}」")
    return redirect(url_for("index"))


@app.route("/tags/delete/<int:tag_id>", methods=["POST"])
@login_required
def delete_tag(tag_id):
    db = get_db()
    tag = db.execute(
        "SELECT id, name FROM tags WHERE id = ? AND user_id = ?",
        (tag_id, session["user_id"]),
    ).fetchone()
    if tag is None:
        abort(404)
    db.execute("UPDATE todos SET tag_id = NULL WHERE tag_id = ?", (tag_id,))
    db.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
    db.commit()
    flash(f"已刪除標籤「{tag['name']}」")
    return redirect(url_for("index"))


@app.route("/edit/<int:todo_id>", methods=["POST"])
@login_required
def edit(todo_id):
    db = get_db()
    todo = db.execute(
        "SELECT id FROM todos WHERE id = ? AND user_id = ?",
        (todo_id, session["user_id"]),
    ).fetchone()
    if todo is None:
        abort(404)
    title = request.form.get("title", "")
    ok, msg = validate_title(title)
    if not ok:
        flash(msg)
        return redirect(url_for("index"))
    raw_tag = request.form.get("tag_id")
    tag_id = resolve_tag_id(db, raw_tag, session["user_id"])
    db.execute(
        "UPDATE todos SET title = ?, tag_id = ? WHERE id = ?",
        (title.strip(), tag_id, todo_id),
    )
    db.commit()
    flash("已更新")
    return redirect(url_for("index"))


@app.route("/delete/<int:todo_id>", methods=["POST"])
@login_required
def delete(todo_id):
    db = get_db()
    todo = db.execute(
        "SELECT id FROM todos WHERE id = ? AND user_id = ?",
        (todo_id, session["user_id"]),
    ).fetchone()
    if todo is None:
        abort(404)
    db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    db.commit()
    flash("已刪除")
    return redirect(url_for("index"))


@app.route("/status/<int:todo_id>", methods=["POST"])
@login_required
def cycle_status(todo_id):
    db = get_db()
    todo = db.execute(
        "SELECT id, status FROM todos WHERE id = ? AND user_id = ?",
        (todo_id, session["user_id"]),
    ).fetchone()
    if todo is None:
        abort(404)
    if todo["status"] not in STATUS_CYCLE:
        abort(400)
    next_status = STATUS_CYCLE[(STATUS_CYCLE.index(todo["status"]) + 1) % len(STATUS_CYCLE)]
    db.execute("UPDATE todos SET status = ? WHERE id = ?", (next_status, todo_id))
    db.commit()
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin():
    db = get_db()
    users = db.execute(
        "SELECT id, username, created_at FROM users ORDER BY id"
    ).fetchall()
    users_data = []
    for user in users:
        todos = db.execute(
            "SELECT id, title, status, created_at FROM todos WHERE user_id = ? ORDER BY id DESC",
            (user["id"],),
        ).fetchall()
        users_data.append(
            {
                "id": user["id"],
                "username": user["username"],
                "created_at": user["created_at"],
                "todos": todos,
            }
        )
    return render_template("admin.html", users=users_data)


if __name__ == "__main__":
    init_db()
    # ponytail: Flask dev server, swap to gunicorn if this needs to handle real traffic
    app.run(host="0.0.0.0", port=5000)
