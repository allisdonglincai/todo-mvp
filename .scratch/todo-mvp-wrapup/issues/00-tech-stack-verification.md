Type: research
Status: resolved

## Question

Notes 宣稱的 tech stack（Python + Flask，server-rendered，前後端同一 process + sqlite3 stdlib，無 ORM）是否與實際程式碼相符？

## Answer

相符，逐項核對 `app.py`、`requirements.txt`、`templates/index.html`：

- Flask：`requirements.txt` 只有一行 `flask`；`app.py` 用 `from flask import Flask, g, redirect, render_template, request, url_for`
- Server-rendered、同一 process：`render_template` 渲染 `templates/index.html`（Jinja2），表單 POST 回同一個 Flask app 的路由（`/add`、`/toggle/<id>`），沒有獨立前端 process 或 API 層
- sqlite3 stdlib，無 ORM：`import sqlite3`，直接寫原生 SQL（`db.execute(...)`），沒有 SQLAlchemy 等 ORM

額外發現：`app.py:63` 已有 `# ponytail: Flask dev server, swap to gunicorn if this needs to handle real traffic` 註解，呼應 [MVP 是否需要收尾/加固到可展示程度](01-mvp-hardening-scope.md) 的討論點。
