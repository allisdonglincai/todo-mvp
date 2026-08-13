# v1 MVP 介面契約

backend 實作、frontend 依賴、devops 驗證的共同介面，先定好避免三個 lane 互相 `orchestration ask` 來回。任何一方想改這裡列的東西，一律先透過 `orca orchestration ask` 給 main 裁決，不要自己單方面改掉別人依賴的介面。

## 路由

| Method | Path | 需要登入 | 需要 admin | 說明 |
|---|---|---|---|---|
| GET/POST | `/register` | 否 | 否 | 註冊；成功後導向 `/login` 並 flash 成功訊息 |
| GET/POST | `/login` | 否 | 否 | 登入；成功後導向 `/`；失敗 flash 錯誤訊息、留在頁面 |
| POST | `/logout` | 是 | 否 | 清 session，導向 `/login` |
| GET | `/` | 是 | 否 | 未登入導向 `/login`；只列當前使用者自己的 todo |
| POST | `/add` | 是 | 否 | 新增 todo，`user_id` = 當前登入者 |
| POST | `/status/<int:todo_id>` | 是 | 否 | 循環切換該 todo 狀態（必須是自己的 todo，否則 404/403） |
| GET | `/admin` | 是 | 是 | 非 admin 存取回 403；列所有使用者與各自的 todo |

## Session keys

- `session['user_id']`：int，登入者的 `users.id`
- `session['is_admin']`：bool

## 環境變數

- `SECRET_KEY`：Flask session 簽章用，devops 在 `docker run` 時提供，backend 從 `os.environ["SECRET_KEY"]` 讀（沒有就啟動失敗，不要生預設值掩蓋忘記設定的問題）
- `ADMIN_USERNAME` / `ADMIN_PASSWORD`：backend 在 app 啟動、`init_db()` 時用來 seed 第一個 admin 帳號（若該 username 已存在則跳過，不重複建立）

## 資料模型

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','in_progress','done')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

狀態循環順序：`pending` → `in_progress` → `done` → `pending` → …

## Template 變數（backend 傳給 frontend 的 render_template 參數）

- `index.html`：`todos`（list，每筆有 `id`/`title`/`status`/`created_at`）、`username`（當前登入者）
- `admin.html`：`users`（list，每筆有 `id`/`username`/`created_at`/`todos`，`todos` 是該使用者的 todo list，欄位同上）
- `login.html` / `register.html`：不需要特殊變數，錯誤/成功訊息走 flash

## 輸入驗證規則（前端 HTML5 屬性 + 後端二次驗證都要）

- **username**：必填、3–30 字、只允許英數字與底線（前端 `pattern="[A-Za-z0-9_]{3,30}"`），後端額外檢查不重複
- **password**：必填、至少 8 碼（前端 `minlength="8"`）
- **todo 標題**：必填（trim 後非空）、上限 200 字（前端 `maxlength="200"`）
- **status**：前端只能透過按鈕循環（不開放自由輸入），後端仍要檢查更新後的值落在 `pending`/`in_progress`/`done` 三者之一

## 共用頁面元素（避免四個頁面各自兜一套，走同一個 base template）

- `templates/base.html`：放 loading 遮罩的 markup/CSS/JS、flash 訊息渲染區塊，其他頁面 `{% extends "base.html" %}`
- Flash 訊息用 Flask 內建 `flash()`，不裝新套件

## Verify 用的完整流程（devops lane 的 `scripts/verify_deploy.sh` 依此串）

1. 建置、啟動 container（帶 `SECRET_KEY`/`ADMIN_USERNAME`/`ADMIN_PASSWORD`）
2. `curl` 註冊一個測試帳號 → 登入 → 新增一筆 todo → 連續切換狀態三次確認回到 `pending` → 登出
3. 用 `ADMIN_USERNAME`/`ADMIN_PASSWORD` 登入 → `GET /admin` 確認測試帳號與其 todo 出現在結果裡
4. `docker restart` → 重新登入確認資料仍在
5. 清理 container
