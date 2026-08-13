Type: task
Mode: execution
Lane: backend
Status: resolved

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

`app.py` 已依 v1-contract.md 重寫，commit 到 `backend-lane` 分支（`3e2804b`）。`/goal` 第 1 次嘗試即通過，未觸發重試上限。

### pytest 實際輸出

環境限制：`backend-lane` worktree 所在的 host Python（`python3.14`，系統層級，無 `pip`/`ensurepip`，且無 passwordless sudo）沒有裝 flask/pytest，也無法在地安裝套件。改用 `python:3.12-slim`（跟 `Dockerfile` 同一個 base image）跑 `docker run --rm -v "$(pwd)":/app -w /app python:3.12-slim bash -c "pip install --quiet flask pytest && python -m pytest test_app.py -v"`，這只是換一個有 pip 的執行環境，不是動 `requirements.txt`（`test_app.py`/`pytest` 本來就不會被 `Dockerfile` COPY 進 image）。

```
collected 6 items

test_app.py::test_register_login_add_toggle_logout PASSED                [ 16%]
test_app.py::test_duplicate_username_rejected PASSED                     [ 33%]
test_app.py::test_short_password_rejected PASSED                         [ 50%]
test_app.py::test_index_requires_login PASSED                            [ 66%]
test_app.py::test_admin_forbidden_for_non_admin PASSED                   [ 83%]
test_app.py::test_admin_sees_other_users_todos PASSED                    [100%]

6 passed in 1.73s
```

重跑一次拿到明確 exit code 確認非偶然：`EXIT_CODE=0`。

### 遇到的問題與設計取捨

- **templates/ 缺口**：`backend-lane` worktree 裡目前只有舊版 `index.html`（沒有 `login.html`/`register.html`/`admin.html`/`base.html`，這些屬於 frontend lane 尚未完成的檔案）。若 `test_app.py` 直接呼叫真實 `render_template`，GET `/login`、`/`、`/admin` 會拋 `TemplateNotFound` 導致測試在還沒驗證任何後端邏輯前就整組炸掉——這不是後端邏輯的錯，是跨 lane 檔案時序問題。
  - 取捨：**沒有**去碰 `templates/` 目錄（仍是 owned by frontend lane，沒有違反界線），而是在 `test_app.py`（我自己 owned 的檔案）裡把 `app.jinja_env.loader` 換成 `jinja2.DictLoader` 提供的最小 stub 樣板，只用來讓 render 不炸、並讓測試能斷言 `todos`/`username`/`users` 等 context 變數確實有正確帶入。這代表：
    - backend 的 pytest 只驗證**後端邏輯**（auth/session/驗證函式/admin 權限/狀態循環/資料隔離），不驗證真實樣板長相
    - 真實 template 渲染的正確性要靠 v1-contract.md 最後一節「Verify 用的完整流程」（devops 的 `scripts/verify_deploy.sh`，跑在三個 lane 都合併回 master 之後）覆蓋，屆時 `templates/` 會是 frontend lane 產出的正式版本
  - 已請 advisor 確認這個做法合理才動手，沒有另外發 `orchestration ask` 卡住流程（不涉及修改 `templates/`/`Dockerfile`/`requirements.txt`，不需要升級決策）

### 涵蓋範圍對照 ticket 要求

- 註冊 → 登入 → 新增 todo → 連續切換狀態三次回到 pending → 登出：`test_register_login_add_toggle_logout`
- 重複 username 註冊被拒：`test_duplicate_username_rejected`
- 密碼太短被拒：`test_short_password_rejected`
- 未登入存取 `/` 導向 `/login`：`test_index_requires_login`
- 非 admin 存取 `/admin` 被拒（403）：`test_admin_forbidden_for_non_admin`
- admin 在 `/admin` 看到別人的 todo：`test_admin_sees_other_users_todos`

### Main 第二層驗證（獨立重跑，非採信自我陳述）

在 `backend-lane` worktree 下獨立執行 `docker run --rm -v "$(pwd)":/app -w /app python:3.12-slim bash -c "pip install --quiet flask pytest && python -m pytest test_app.py -v"`（沿用同一環境變通方案，因為 host `python3.14` 確實無 `pip`，main 自己也核對過），6 個測項全數 PASSED，exit code 0。確認通過，維持 `Status: resolved`。

備註：`test_app.py` 用 `DictLoader` stub 樣板繞過 `TemplateNotFound`，只驗證後端邏輯，不驗證真實 template 渲染——這代表 pytest 綠燈不保證 backend 的 context 變數與 frontend lane 剛合併進 master 的真實 `templates/*.html` 實際搭配時不會出錯（例如變數名稱、迴圈欄位對不上）。這個落差留給合併後在 master 上重跑 `scripts/verify_deploy.sh`（真實 HTTP 端對端）去抓，不在這裡重複驗證。
