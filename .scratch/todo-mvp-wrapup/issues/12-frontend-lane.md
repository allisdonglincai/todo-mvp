Type: task
Mode: execution
Lane: frontend
Status: claimed

開工前先讀 [operating-principles.md](../operating-principles.md)（stop conditions/cost ceilings、切勿假設應該沒問題、worktree 隔離規則、SOLID/KISS）與 [v1-contract.md](../v1-contract.md)（路由/template 變數/驗證規則的權威定義）。開發時使用 `/frontend-design:frontend-design`；若這個 session 沒裝這個 plugin，退回用 `better-ui`/`better-layout`/`better-typography`/`better-accessibility`。

## Worktree

全部工作在 `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/frontend-lane`（分支 `frontend-lane`）下進行，不要碰 master 主 checkout。commit 到自己的分支即可，main 驗證通過後會負責合併回 master。

## Owned files

`templates/`、`static/`（新目錄，本 ticket 建立）。不可改 `app.py`、`Dockerfile`、`requirements.txt`；若需要這些檔案改動，用 `orca orchestration ask` 交給 main session 裁決。

## Task（見 [Ticket 20](20-v1-mvp-scope-reopen.md) 完整背景）

依 [v1-contract.md](../v1-contract.md) 建立/改寫樣板：

1. **`templates/base.html`**：共用 layout，放 loading 遮罩（vanilla JS：監聽全頁所有 `submit`/`click` 事件，觸發時立即顯示全螢幕遮罩+文字，`pageshow` 事件時隱藏，處理瀏覽器上一頁/下一頁的情況）、flash 訊息渲染區塊。其他頁面 `{% extends "base.html" %}`，不要四個頁面各自重複貼一樣的 script/style
2. **`templates/login.html`**：username/password 表單，導向 `/login`
3. **`templates/register.html`**：username/password 表單，前端驗證屬性照 contract（`pattern`/`minlength`），導向 `/register`
4. **`templates/index.html`**：改用 contract 的 `todos`/`username` 變數；原本的 checkbox 換成點擊循環三態的按鈕（表單 POST 到 `/status/<id>`）；新增 todo 輸入框加 `maxlength="200"`；加登出按鈕
5. **`templates/admin.html`**：依 contract 的 `users` 變數渲染帳號清單，每個帳號下面列出其 `todos`（含 `created_at`/`status`）

這個 MVP 沒有前端框架，所有互動（loading 遮罩、狀態循環按鈕）都是 vanilla JS + 表單 POST，不要引入任何新的 JS 套件或 build 工具。

## Verification（closed loop）

這個 lane 沒有自己的 pytest（`test_app.py` 屬於 backend），能做的是靜態檢查：

```
/goal 所有 templates/*.html 都能用 Jinja2 Environment 語法解析成功（不是渲染，只驗證語法沒錯）、且用 Python 內建 html.parser 逐一 feed 不拋例外，stop after 3 tries
```

backend lane 完成後（看 [Ticket 11](11-backend-lane.md) 的 Answer 是否已填），main 會請你再跑一次 `pytest test_app.py`（唯讀執行，不代表你擁有這個檔案）當作端對端確認；這個依賴關係寫在 `coordinator-protocol.md`，不用自己等，先把樣板做完回報。

回報給 main 之後，main 會**獨立重跑一次上面的靜態檢查**，不採信這裡的自我陳述。

## Answer

（main session dispatch 後，由 frontend lane 回報結果並在此記錄：完成的頁面、審查/驗證結論）
