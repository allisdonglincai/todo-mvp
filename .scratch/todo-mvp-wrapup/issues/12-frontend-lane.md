Type: task
Mode: execution
Lane: frontend
Status: resolved

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

完成，commit `f28084e`（分支 `frontend-lane`，worktree `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/frontend-lane`）。

### 完成的頁面

- `templates/base.html`（新）：共用 layout。loading 遮罩用 vanilla JS 監聽全頁 `submit`/`click` 事件立即顯示全螢幕遮罩，`pageshow` 事件時隱藏（涵蓋瀏覽器上一頁/下一頁、bfcache 情境）；flash 訊息渲染區塊（`role="status" aria-live="polite"`，依 category 上色）；其他四個頁面共用的 CSS（表單、按鈕、todo 列表、admin 區塊樣式）也集中放這裡，避免四頁各自重複。
- `templates/login.html`（新）：username/password 表單，POST `/login`，`autocomplete` 屬性齊全。
- `templates/register.html`（新）：username/password 表單，POST `/register`；username 有 `pattern="[A-Za-z0-9_]{3,30}"` + `minlength="3"` + `maxlength="30"`；password 有 `minlength="8"`，皆照 contract。
- `templates/index.html`（改寫）：改用 contract 的 `todos`（`id`/`title`/`status`/`created_at`）與 `username` 變數；checkbox 換成點擊循環按鈕（表單 POST `/status/<id>`，按鈕文字顯示中文狀態標籤，不開放自由輸入）；新增 todo 輸入框加 `maxlength="200"`；加登出按鈕（POST `/logout`）。
- `templates/admin.html`（新）：依 `users` 變數列出帳號與其 `todos`（含 `created_at`/`status`），非 admin/未登入的擋檢查是 backend 責任，此頁只負責渲染。

表單 `action` 一律用 contract 定義的**硬編路徑**（`/login`、`/register`、`/logout`、`/add`、`/status/<id>`），沒有用 `url_for`——因為這個 lane 不擁有 `app.py`，且該檔案目前仍是重構前的舊版（backend lane ticket 11 尚未 resolved），無法保證 Flask view function 的 endpoint 名稱，用路徑字串可以跟 backend 的實作細節解耦，只依賴 contract 保證的路徑本身。

沒有新增 `static/` 內容：loading 遮罩與共用樣式依 ticket 原文「放在 base.html 供其他頁面 extends」的說法直接內嵌在 `base.html`，沒有額外 JS 套件或 build 工具，符合 KISS。

Accessibility：套用 `better-accessibility` skill 的原則——每個 input 都有對應 `<label for>`、`autocomplete`，flash 訊息用 `role="status"`，focus ring 用 `:focus-visible`，按鈕 `min-height: 40px` 符合最小 hit area，loading spinner 加 `prefers-reduced-motion` 降階。因未安裝 `frontend-design` plugin，依 ticket 指示 fallback 到 `better-accessibility`（其餘三個 better-* skill 因這個頁面規模小、無額外版面/字型/排版決策需要，沒有逐一呼叫，判斷用內建知識已足夠覆蓋）。

### 驗證結論

自行執行 ticket 指定的靜態檢查（Jinja2 `Environment`/`FileSystemLoader` 逐一 `get_template()` 解析語法 + Python 內建 `html.parser.HTMLParser` 逐一 `feed()` 整份檔案內容），五個 `templates/*.html` 全數通過，無例外：

```
[jinja OK] admin.html      [html.parser OK] admin.html
[jinja OK] base.html       [html.parser OK] base.html
[jinja OK] index.html      [html.parser OK] index.html
[jinja OK] login.html      [html.parser OK] login.html
[jinja OK] register.html   [html.parser OK] register.html
```

（第 1 次嘗試即通過，未觸及 3 次上限。）

`pytest test_app.py` 端對端確認待 backend lane（ticket 11）resolved 後再跑，目前 ticket 11 仍是 `claimed`，未觸發這個依賴步驟。

main 請獨立重跑上面的靜態檢查指令，不要採信這裡的自我陳述。

### Main 第二層驗證（獨立重跑，非採信自我陳述）

在 `frontend-lane` worktree 下獨立重寫並執行 Jinja2 `Environment.get_template()` + `html.parser.HTMLParser().feed()` 檢查（未沿用 worker 的腳本），五個 `templates/*.html` 全數 `[OK]`，exit code 0。確認通過，維持 `Status: resolved`。

`pytest test_app.py` 端對端確認待 backend lane（ticket 11）resolved 後再由 main 補跑。

### 追加修復：loading 遮罩卡死（合併後使用者實測發現）

三個 lane 全部合併回 master、v1-contract 端對端驗證通過後，使用者實測 `http://localhost:5000/login` 發現：點擊帳號/密碼 input 就整個卡在全螢幕 loading 遮罩。

**Root cause**：`templates/base.html` 的 `document.addEventListener("click", showOverlay)` 監聽整個 document 的所有 click，沒有篩選是否為真的會導頁的元素，點 input 純 focus 也觸發顯示；遮罩只在 `pageshow`（實際導頁完成）時隱藏，沒有導頁就永遠卡住。

**修復**（frontend-lane commit `e3574a5`）：click 監聽改成只在 `event.target.closest("a[href], button[type=submit], input[type=submit]")` 命中時才 `showOverlay()`；`submit` 監聽不變。修改前已用 `grep -n "<button" templates/*.html` 確認五個 template 的按鈕都明確寫 `type="submit"`，不會漏判。

**Main 第二層驗證**：
1. 靜態檢查：獨立在 `frontend-lane` worktree 重跑 Jinja2/html.parser 檢查，五個 template 全數 `[OK]`，exit 0
2. 合併回 master（commit）後，用 `orca-ide` 內建瀏覽器自動化（`tab create`/`goto`/`eval`）對 `localhost:5000` 實際跑一次 `demo-brief.md` 的完整 user flow + admin flow：
   - 點擊 `/login` 的 username input（純 focus，不送出）→ `overlay.classList.contains('active')` 為 `false`，確認 bug 已修好
   - 註冊 `demo_user` → 導向 `/login` 並 flash「註冊成功，請登入」→ 登入 → 落地 `/`
   - 新增 todo「示範待辦事項」→ 顯示「待處理」
   - 連續點狀態按鈕 3 次 → 待處理 → 進行中 → 已完成 → 待處理（三態循環正確）
   - 登出 → 導向 `/login`；未登入重新造訪 `/` → 正確導回 `/login`
   - 以 admin 帳密登入 → `/admin` 正常載入（非 403）→ 頁面內容包含 `demo_user`、其 todo 標題與狀態文字

全數通過，確認合併後的 master 是可以正確跑完整個 demo 流程的。驗證完後把 `todo-mvp-demo` container 用乾淨的環境變數重新起一份（清掉測試帳號/todo），交還一個乾淨狀態給使用者做正式 demo。
