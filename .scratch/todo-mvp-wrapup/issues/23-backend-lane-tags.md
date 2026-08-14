Type: task
Mode: execution
Lane: backend
Status: resolved

> main 第二層驗證（2026-08-14）：diff 範圍確認只動 app.py/test_app.py（自 016abb1，commit c07d32c）；main 自己在該 worktree 重跑 docker pytest → **27 passed, exit 0**；抽查 app.py diff 符合 v3-tags-return.md §3-4 與 §7 全部裁決（靜默忽略非法 tag_id、302+flash、PRAGMA 後才 ALTER、admin 未動）。已 merge 進 master（origin/master `33277b8`）。

開工前先讀 [operating-principles.md](../operating-principles.md) 與 [v1-contract.md](../v1-contract.md)。**本 ticket 的規格權威來源是 [v3-tags-return.md](../v3-tags-return.md)**（含第 7 節 coordinator 裁決，遇到與本 ticket 摘要不一致處以該文件為準）。

## Worktree

全部工作在 `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/backend-lane-tags`（分支 `allisdonglincai/backend-lane-tags`，從 master HEAD `016abb1` 分出）下進行，不要碰 master 主 checkout。

## Owned files

`app.py`、`test_app.py`。不可改 `templates/`、`static/`、`Dockerfile`、`requirements.txt`。

## Task（細節見 v3-tags-return.md §3–4、§7）

1. **Schema/migration**：新增 `tags` 表（`UNIQUE(user_id, name)`）；`todos` 加 `tag_id INTEGER REFERENCES tags(id)`。`init_db()` 對新舊 DB 都要能跑（`PRAGMA table_info` 檢查後才 ALTER；demo container 的 todo.db 是既有資料庫）。
2. **新路由**：`POST /tags/add`（name trim 非空、≤30 字、同 user 不重名；失敗 302 + flash，不是 400）；`POST /tags/delete/<int:tag_id>`（非本人 404；先把其下 todo 的 tag_id 置 NULL 再刪）。
3. **既有路由擴充**：`GET /` 支援 `?tag_id=` 篩選（僅限自己的 tag，無效值視同無篩選）並多傳 `tags`/`active_tag`，todos 每筆多 `tag_id`/`tag_name`（LEFT JOIN）；`POST /add`、`POST /edit/<id>` 多收選填 `tag_id`——**非法/非本人/非數字一律靜默忽略視同 NULL**（§7 裁決 1），`/edit` 收空字串 = 設回 NULL。
4. `/status`、`/delete`、auth 路由行為不變；**admin 完全不動**（§7 裁決 4）。標籤名驗證函式獨立（SRP，同 `validate_title` 風格）。

## Verification（closed loop）

```
/goal pytest test_app.py 全部通過（exit 0），既有測項一個都不能壞，stop after 5 tries
```

新測項至少覆蓋 v3-tags-return.md §5 Backend 全部六組（依 §7 裁決調整：空白/重名/超長是 302+flash；非法 tag_id 是靜默忽略），特別含 migration 測試：對「已有 todos 表但無 tag_id 欄」的 DB 跑 `init_db()` 能升級且資料不丟。

環境提示：host 無 pip/flask，沿用 `docker run --rm -v "$(pwd)":/app -w /app python:3.12-slim bash -c "pip install --quiet flask pytest && python -m pytest test_app.py -v"`。

5 次沒過或連續兩次同因失敗就停下，把輸出寫進 Answer 回報 main。回報後 main 會獨立重跑。`## Answer`/`Status` 一律寫 master 路徑下這份檔案，`Status: resolved` 由 main 標記。

## Answer

完成，commit `c07d32c`（分支 `allisdonglincai/backend-lane-tags`，worktree backend-lane-tags）。

**實作（app.py）**
- `init_db()`：新增 `tags` 表（`UNIQUE(user_id, name)`）；用 `PRAGMA table_info(todos)` 檢查後才 `ALTER TABLE todos ADD COLUMN tag_id INTEGER REFERENCES tags(id)`，新舊 DB 皆可跑、可重複執行。
- `validate_tag_name()`：獨立驗證函式（trim 非空、≤30 字），風格同 `validate_title`。
- `resolve_tag_id(db, raw, user_id)`：共用 helper，非數字/不存在/非本人 tag 一律回 None（§7 裁決 1 靜默忽略），`/`、`/add`、`/edit` 三處共用。
- `POST /tags/add`：trim、驗證、同 user 重名檢查；失敗 302 + flash（§7 裁決 2，非 400）；成功 flash「已建立標籤「X」」。
- `POST /tags/delete/<int:tag_id>`：非本人 404；先 `UPDATE todos SET tag_id = NULL` 再刪 tag。
- `GET /`：`?tag_id=` 篩選（僅自己的 tag，無效視同無篩選）；todos LEFT JOIN tags 多回 `tag_id`/`tag_name`；template 多傳 `tags`、`active_tag`。
- `POST /add`、`POST /edit/<id>`：選填 `tag_id`，`/edit` 空字串 = NULL。`/status`、`/delete`、auth、admin 全部未動。

**驗證（真實執行）**：`docker run --rm -v "$(pwd)":/app -w /app python:3.12-slim bash -c "pip install --quiet flask pytest && python -m pytest test_app.py -v"` → **27 passed, exit 0**（第 2 次嘗試通過，5 次上限內）。既有 13 測項全過；新增 14 測項覆蓋 §5 Backend 六組：tags/add 成功/空白/超長/重名/跨 user 同名/未登入、tags/delete 本人（todo tag_id 置 NULL 且 todo 保留）/非本人 404、/add 與 /edit 帶合法/非法/非本人/非數字/空字串 tag_id、`?tag_id=` 篩選與無效值、migration 測試（舊 schema DB 升級後資料保留且 idempotent）。

第 1 次失敗原因（已修，皆為測試側問題）：index stub template 沒渲染 flash；測試用 username "u1"/"u2" 不符既有 3-30 碼規則導致註冊失敗。app.py 邏輯未因此改動。


### Main 第二層驗證（獨立重跑，非採信自我陳述）

main 在 `backend-lane-tags` worktree 獨立重跑 pytest（python:3.12-slim）：**27 passed，EXIT=0**。抽查 diff：`PRAGMA table_info` 後才 ALTER 的 migration guard、`validate_tag_name`/`resolve_tag_id` 獨立函式、admin 與 /status 未動、app.py 僅 6 行既有行變動。已 merge + push（master `33277b8`）。
