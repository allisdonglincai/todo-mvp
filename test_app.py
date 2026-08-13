import os

import app as app_module

TEST_DB = "test_todo.db"


def run():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    app_module.DB_PATH = TEST_DB
    app_module.init_db()
    client = app_module.app.test_client()

    client.post("/add", data={"title": "buy milk"})
    client.post("/add", data={"title": "  "})  # blank should be ignored

    resp = client.get("/")
    assert b"buy milk" in resp.data
    assert resp.data.count(b"<li") == 1, "blank title should not be added"

    with app_module.app.app_context():
        todo_id = app_module.get_db().execute("SELECT id FROM todos").fetchone()["id"]

    client.post(f"/toggle/{todo_id}")
    resp = client.get("/")
    assert b'class="done"' in resp.data

    client.post(f"/toggle/{todo_id}")
    resp = client.get("/")
    assert b'class="done"' not in resp.data

    os.remove(TEST_DB)
    print("all checks passed")


if __name__ == "__main__":
    run()
