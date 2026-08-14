Type: task
Mode: execution
Lane: frontend
Status: resolved

開工前先讀 [operating-principles.md](../operating-principles.md)（stop conditions/cost ceilings、切勿假設應該沒問題、worktree 隔離規則、SOLID/KISS）與 [v1-contract.md](../v1-contract.md)。UI 開發用 `/frontend-design:frontend-design`；沒裝就退回 `better-ui`/`better-layout`/`better-typography`/`better-accessibility`。

## Worktree

全部工作在 `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/frontend-lane-crud`（分支 `allisdonglincai/frontend-lane-crud`，從已含 backend `/edit`/`/delete` 路由的 master HEAD `31fb744` 分出）下進行，不要碰 master 主 checkout、也不要用舊的 `frontend-lane` 分支（已與 master 嚴重分岔）。commit 到自己的分支即可，main 驗證通過後會負責合併。

## Owned files

`templates/`、`static/`。不可改 `app.py`、`test_app.py`、`Dockerfile`、`requirements.txt`；若需要這些檔案改動，用 `orca orchestration ask` 交給 main session 裁決。

## Task

在 `templates/index.html`（沿用現有 Bubble 設計系統風格）為每筆 todo 加上編輯與刪除功能，對接 backend 已存在的路由：

- **編輯**：todo 那一列放 inline 表單，文字輸入框 prefill 現有 `title`（`maxlength="200"`、必填），送出 POST 到 `/edit/<id>`
- **刪除**：「刪除」按鈕，POST 到 `/delete/<id>`，用瀏覽器原生 `confirm()` 二次確認（不要做 modal 元件）

vanilla JS + 表單 POST，不引入任何新 JS 套件、框架或 build 工具。注意既有 loading 遮罩的 click 篩選邏輯（`base.html`，v1 曾因監聽過寬卡死過）：新按鈕若是 `type="submit"` 就會被涵蓋；`confirm()` 取消時不能讓遮罩卡住畫面。

## Verification（closed loop）

```
/goal (1) 所有 templates/*.html 通過 Jinja2 語法解析 + html.parser feed 無例外；(2) 用 orca-ide 瀏覽器自動化在真瀏覽器實際跑一次：登入 → 新增一筆 todo → 編輯它（title 真的變了、畫面刷新後顯示新值）→ 刪除它（confirm 後該筆從列表消失）→ 過程中 loading 遮罩沒有卡死（含按「取消」confirm 的情況），stop after 3 tries
```

瀏覽器驗證操作細節：
- 在自己的 worktree 起 app：`docker run --rm -d --name todo-crud-fe-test -p 5001:5000 -v "$(pwd)":/app -w /app -e SECRET_KEY=test-secret -e ADMIN_USERNAME=admin -e ADMIN_PASSWORD=admin_password_123 python:3.12-slim bash -c "pip install --quiet flask && python app.py"`（host python 沒有 pip/flask；若 app.py 不是 `app.run(host='0.0.0.0', port=5000)` 啟動就照實際情況調整啟動指令，或改用 repo 的 Dockerfile build）。測完 `docker rm -f todo-crud-fe-test` 清掉。
- 瀏覽器用 `orca-ide tab create` / `goto` / `eval`（讀 DOM 斷言）。**這台機器 `orca-ide snapshot`/`screenshot` 會 `runtime_unavailable`，不要用**；`terminal wait` 也是壞的。
- 帳號/user flow 慣例照 `demo-brief.md`（可自己註冊一個測試帳號來操作；admin 密碼是 `admin_password_123`，不是舊版寫的 `admin1234`）。
- `confirm()` 在自動化裡用 `eval` 預先覆寫 `window.confirm = () => true`（以及一次 `() => false` 驗證取消時遮罩不卡）。

`/goal` 每次嘗試由獨立 evaluator 檢查，3 次沒過就停，把失敗輸出寫進 Answer 回報 main；連續兩次失敗原因相同也立刻停下升級給 main。回報後 main 會獨立重跑驗證，不採信自我陳述。ticket 的 `## Answer`/`Status` 一律寫 master 路徑下這份檔案（`/mnt/c/Users/1141201/Documents/allis0813-claude-code-basic/.scratch/todo-mvp-wrapup/issues/22-frontend-lane-crud.md`），不要改 worktree 裡的舊拷貝。`Status: resolved` 由 main 驗證後標記，worker 不要自己標。

## Answer

**完成，`/goal` 第 1 次嘗試即通過。** Commit：`9fee092e2056bfe5aa24bb30d4bd8930670d163f`（分支 `allisdonglincai/frontend-lane-crud`，改動 `templates/index.html` + `static/css/app.css`，共 2 檔 +42/-1）。

**實作**：每筆 todo 列加「編輯」按鈕（`type="button"`，onclick 切換同列隱藏的 `.edit-form` 並 focus）；`.edit-form` 是 inline 表單，input prefill 現有 title、`maxlength="200"` + `required`，POST `/edit/<id>`。「刪除」是 POST `/delete/<id>` 的表單，`onsubmit` 用原生 `confirm()`，取消時 `event.stopPropagation()` + `return false`——stopPropagation 是關鍵，否則 base.html 的 document-level submit 監聽仍會顯示 loading 遮罩導致卡死。CSS 只加 `.todo-item{flex-wrap:wrap}` 與 `.edit-form:not([hidden]){display:flex;width:100%}`（用 `:not([hidden])` 避免 `display:flex` 蓋掉 `hidden` 屬性）。無新增 JS 套件/框架/build 工具。

**Verification (1)** — Jinja2 + html.parser（在 python:3.12-slim container 內跑，host 無 flask）：
```
OK admin.html / base.html / index.html / login.html / register.html
ALL TEMPLATES PASS
```

**Verification (2)** — orca-ide 真瀏覽器自動化（`goto`/`eval`，未用 snapshot/screenshot/terminal wait）。app 以 ticket 指令跑在 `todo-crud-fe-test` container、port 5001；註冊測試帳號 `fetest22` 登入操作：
- 註冊 → 登入 → 落在 `/`，overlay-active:false
- 新增 todo「CRUD 驗證項目」→ 列表出現，overlay:false
- 點「編輯」→ `edit-form-visible:true`，改成「CRUD 已編輯」送出 → 頁面刷新後 `.todo-title` 顯示 `CRUD 已編輯`，overlay:false
- `window.confirm=()=>false` 點「刪除」→ `todos:1 | overlay:false`（項目仍在、遮罩沒卡）
- `window.confirm=()=>true` 點「刪除」→ `todos:0 | empty-msg:true | overlay:false | flash:已刪除`

測試 container 已 `docker rm -f` 清除。等待 main 獨立重跑驗證後合併。


### Main 第二層驗證（獨立重跑，非採信自我陳述）

1. 靜態檢查：main 獨立在 `frontend-lane-crud` worktree 以 python:3.12-slim 重跑 Jinja2 `get_template()` + `html.parser.feed()`，五個 template 全 OK。
2. 瀏覽器實測：main 自己起 container（port 5001）、用 orca-ide tab/eval 以新帳號 `mainv2check` 跑完整流程——登入 → 新增 todo → 點「編輯」（表單展開 hidden:false）→ 改 title 送出後顯示「main 已編輯確認」→ `confirm=()=>false` 點刪除：todo 仍在、`#loading-overlay` display:none 沒卡 → `confirm=()=>true` 點刪除：todos:0。全數通過。
3. 抽查 diff：只動 `templates/index.html` + `static/css/app.css`，無新依賴。

已 merge 進 coordinator 分支並 push（master `178a31a`）。
