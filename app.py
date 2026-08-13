import sqlite3

from flask import Flask, g, redirect, render_template, request, url_for

DB_PATH = "todo.db"

app = Flask(__name__)


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


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )


@app.route("/")
def index():
    todos = get_db().execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    return render_template("index.html", todos=todos)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    if title:
        get_db().execute("INSERT INTO todos (title) VALUES (?)", (title,))
        get_db().commit()
    return redirect(url_for("index"))


@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    get_db().execute(
        "UPDATE todos SET done = NOT done WHERE id = ?", (todo_id,)
    )
    get_db().commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    # ponytail: Flask dev server, swap to gunicorn if this needs to handle real traffic
    app.run(host="0.0.0.0", port=5000)
