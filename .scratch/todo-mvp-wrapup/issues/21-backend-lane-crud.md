Type: task
Mode: execution
Lane: backend
Status: resolved

開工前先讀 [operating-principles.md](../operating-principles.md)（stop conditions/cost ceilings、切勿假設應該沒問題、worktree 隔離規則、SOLID/KISS）與 [v1-contract.md](../v1-contract.md)（既有路由/session/schema/驗證規則的權威定義，v2 是在其上**新增**，不要改動既有路由行為）。

## Worktree

全部工作在 `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/backend-lane-crud`（分支 `allisdonglincai/backend-lane-crud`，從目前 master HEAD `43674fb` 分出）下進行，不要碰 master 主 checkout、也不要用舊的 `backend-lane` 分支（已與 master 嚴重分岔）。commit 到自己的分支即可，main 驗證通過後會負責合併。

## Owned files

`app.py`、`test_app.py`。不可改 `templates/`、`static/`、`Dockerfile`、`requirements.txt`；若需要這些檔案改動，用 `orca orchestration ask` 交給 main session 裁決。

## Task

補足 CRUD 的 Update / Delete API，新增兩條路由（風格沿用既有 `/status/<int:todo_id>`：動詞在前、POST 表單，不引入 HTTP PUT/DELETE method）：

| Method | Path | 需要登入 | 說明 |
|---|---|---|---|
| POST | `/edit/<int:todo_id>` | 是 | 更新該 todo 的 `title`；必須是當前使用者自己的 todo，否則 404。驗證沿用既有 `validate_title()`（不要重寫一份）。成功導向 `/` 並 flash 成功訊息；驗證失敗 flash 錯誤訊息、導向 `/`（跟現有 `/add` 失敗處理一致，不用做「保留使用者輸入」機制） |
| POST | `/delete/<int:todo_id>` | 是 | 刪除該 todo；必須是當前使用者自己的，否則 404。成功導向 `/` 並 flash「已刪除」 |

未登入存取這兩條路由的行為跟既有受保護路由一致（導向 `/login`）。KISS：不加任何 ticket 沒要求的欄位、抽象層或新依賴。

## Verification（closed loop）

```
/goal pytest test_app.py 全部通過（exit 0，沒有 assertion 失敗），且既有測項一個都不能壞，stop after 5 tries
```

`test_app.py` 新增測項至少覆蓋：edit 自己的 todo 成功（DB 內 title 真的變了）；edit 空白/超長 title 被拒且原值不變；edit 別人的 todo 回 404；delete 自己的 todo 成功（DB 內該筆真的消失）；delete 別人的 todo 回 404 且該筆仍在；未登入打 `/edit`/`/delete` 被導向 `/login`。

環境提示：host python 沒有 pip/flask，v1 的做法是 `docker run --rm -v "$(pwd)":/app -w /app python:3.12-slim bash -c "pip install --quiet flask pytest && python -m pytest test_app.py -v"`，可沿用。

`/goal` 每次嘗試由獨立 evaluator 檢查，5 次沒過就停，把失敗輸出寫進 Answer 回報 main，不要無限重試。連續兩次失敗原因相同也要立刻停下升級給 main。回報後 main 會獨立重跑 pytest，不採信自我陳述。ticket 的 `## Answer`/`Status` 一律寫 master 路徑下這份檔案（`/mnt/c/Users/1141201/Documents/allis0813-claude-code-basic/.scratch/todo-mvp-wrapup/issues/21-backend-lane-crud.md`），不要改 worktree 裡的舊拷貝。`Status: resolved` 由 main 驗證後標記，worker 不要自己標。

## Answer

完成。分支 `allisdonglincai/backend-lane-crud`，commit `90a6547db379a2da473bb7ad0d3a492117cab7d4`（基於 master `43674fb`）。

實作：`app.py` 新增 `POST /edit/<int:todo_id>` 與 `POST /delete/<int:todo_id>`，風格沿用 `/status/<int:todo_id>`（`@login_required`、以 `id + user_id` 查詢、查無回 404）。edit 驗證沿用既有 `validate_title()`，失敗 flash 錯誤導向 `/`；成功各 flash「已更新」/「已刪除」並導向 `/`。只動 `app.py`、`test_app.py`。

`test_app.py` 新增 7 個測項，覆蓋 ticket 要求全部六項（edit 成功且 DB title 變更、空白/超長 title 被拒且原值不變、edit 他人 todo 404、delete 成功且 DB 該筆消失、delete 他人 todo 404 且仍在、未登入打 /edit 與 /delete 導向 /login）。

Verification：`/goal` 第 1 次嘗試即通過（5 次上限內）。指令：`docker run --rm -v "$(pwd)":/app -w /app python:3.12-slim bash -c "pip install --quiet flask pytest && python -m pytest test_app.py -v"`，exit 0。實際輸出（節錄）：

```
test_app.py::test_register_login_add_toggle_logout PASSED                [  8%]
test_app.py::test_duplicate_username_rejected PASSED                     [ 16%]
test_app.py::test_short_password_rejected PASSED                         [ 25%]
test_app.py::test_index_requires_login PASSED                            [ 33%]
test_app.py::test_edit_own_todo PASSED                                   [ 41%]
test_app.py::test_edit_invalid_title_rejected PASSED                     [ 50%]
test_app.py::test_edit_others_todo_404 PASSED                            [ 58%]
test_app.py::test_delete_own_todo PASSED                                 [ 66%]
test_app.py::test_delete_others_todo_404 PASSED                          [ 75%]
test_app.py::test_edit_delete_require_login PASSED                       [ 83%]
test_app.py::test_admin_forbidden_for_non_admin PASSED                   [ 91%]
test_app.py::test_admin_sees_other_users_todos PASSED                    [100%]

============================== 12 passed in 4.11s ==============================
```

既有 5 個測項全數保持通過。Status 留待 main 驗證後標記。

### Main 第二層驗證（獨立重跑，非採信自我陳述）

main 在 `backend-lane-crud` worktree 獨立重跑 `docker run --rm -v "$(pwd)":/app -w /app python:3.12-slim ... pytest test_app.py`：12 passed，EXIT=0。抽查 diff：只新增 `/edit`/`/delete` 兩條路由與 7 個測項，沿用 `validate_title()`/`login_required`/ownership 查詢模式，既有路由未動。已 merge 進 coordinator 分支並 push（master `31fb744`）。
