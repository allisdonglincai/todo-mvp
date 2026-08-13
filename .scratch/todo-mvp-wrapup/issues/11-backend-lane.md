Type: task
Mode: execution
Lane: backend

開工前先讀 [operating-principles.md](../operating-principles.md)（stop conditions/cost ceilings、切勿假設應該沒問題、worktree 隔離規則、SOLID/KISS）與 [v1-contract.md](../v1-contract.md)（路由/session/schema/驗證規則的權威定義）。

## Worktree

全部工作在 `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/backend-lane`（分支 `backend-lane`）下進行，不要碰 master 主 checkout。commit 到自己的分支即可，main 驗證通過後會負責合併回 master。

## Owned files

`app.py`、`test_app.py`。不可改 `templates/`、`Dockerfile`、`requirements.txt`；若需要這些檔案改動，用 `orca orchestration ask` 交給 main session 裁決。

## Task（見 [Ticket 20](20-v1-mvp-scope-reopen.md) 完整背景）

依 [v1-contract.md](../v1-contract.md) 重寫 `app.py`：

1. **Schema**：`init_db()` 改建 `users`/`todos` 兩張表（見 contract 的 CREATE TABLE），不保留舊的 `todos` schema，不用寫 migration
2. **Admin seed**：啟動時用 `os.environ["ADMIN_USERNAME"]`/`os.environ["ADMIN_PASSWORD"]` seed 第一個 admin（若該 username 已存在就跳過）；`SECRET_KEY` 從 `os.environ["SECRET_KEY"]` 讀，缺少就讓 app 啟動失敗，不要生預設值蓋掉忘記設定的問題
3. **路由**：`/register`、`/login`、`/logout`、`/`、`/add`、`/status/<int:todo_id>`、`/admin`——method、登入/admin 要求、行為都照 contract 表格
4. **密碼**：`werkzeug.security.generate_password_hash`/`check_password_hash`，不裝新套件
5. **驗證函式獨立出來**（SRP，不要塞在 route handler 裡）：例如 `validate_username(s)`、`validate_password(s)`、`validate_title(s)`，各自回傳 (是否合法, 錯誤訊息)；`/status/<id>` 要檢查 todo 屬於當前使用者、且更新後的狀態落在三個合法值內
6. **Flash**：用 Flask 內建 `flash()` 回報註冊/登入/驗證錯誤

## Verification（closed loop）

```
/goal pytest test_app.py 全部通過（exit 0，沒有 assertion 失敗），stop after 5 tries
```

`test_app.py` 至少要覆蓋：註冊 → 登入 → 新增 todo → 連續切換狀態三次確認回到 pending → 登出；重複 username 註冊被拒；密碼太短被拒；未登入存取 `/` 被導向 `/login`；非 admin 存取 `/admin` 被拒；admin 能在 `/admin` 看到別人的 todo。

`/goal` 每次嘗試後由獨立的 evaluator model 檢查是否真的通過，不是自己判斷自己做完了。5 次還沒過就停下來，把失敗輸出寫進 Answer，不要無限重試。

回報給 main 之後，main 會**獨立重跑一次 `pytest test_app.py`**，不採信這裡的自我陳述——這是第二層驗證，跟 `/goal` 的 evaluator model 是不同的檢查者。

## Answer

（main session dispatch 後，由 backend lane 回報結果並在此記錄：pytest 實際輸出、遇到的問題）
