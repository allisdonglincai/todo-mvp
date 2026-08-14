Type: task
Mode: execution
Lane: frontend
Status: resolved

開工前先讀 [operating-principles.md](../operating-principles.md) 與 [v1-contract.md](../v1-contract.md)。**本 ticket 的規格權威來源是 [v3-tags-return.md](../v3-tags-return.md)**（§1 user flow、§2 UI 規格、§7 coordinator 裁決）；視覺依據是使用者確認過的 artifact：https://claude.ai/code/artifact/3bc390da-22d0-47a5-9b06-e16032433b39 。UI 開發用 `/frontend-design:frontend-design`，沒裝就退回 better-* skills。

## Worktree

全部工作在 `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/frontend-lane-tags`（分支 `allisdonglincai/frontend-lane-tags`，從已含 backend tags 路由的 master HEAD 分出——確切 hash 見 dispatch 訊息）下進行，不要碰 master 主 checkout。

## Owned files

`templates/`、`static/`。不可改 `app.py`、`test_app.py`、`Dockerfile`、`requirements.txt`。**admin.html 這輪不動**（§7 裁決 4）。

## Task（細節與視覺以 v3-tags-return.md §1–2 + artifact 為準）

`index.html` + `static/`（Bubble 設計系統內，無新依賴/框架/build 工具）：

1. **標籤管理列**：虛線框，「我的標籤」+ chips（各有 ✕，POST `/tags/delete/<id>` 帶 `confirm()`）+ 新增小表單（`maxlength="30" required`，POST `/tags/add`）。
2. **新增 todo 表單**：多一個標籤 `<select>`（「無標籤」+ 使用者標籤），POST `/add` 帶 `tag_id`。
3. **todo 列**：狀態鈕、標題、`tag-chip` 徽章（有才顯示，可點連到 `/?tag_id=<id>`；class 命名避開既有 `status-tag`）、右側 ⋮ 鈕。
4. **⋮ dropdown menu**：「編輯」+ 分隔線 + coral「刪除」；點外面/Esc 關閉；JS dropdown 或原生 `<details>` 皆可。⋮ 與「編輯」是 `type="button"`，不得觸發 loading 遮罩；刪除沿用 `confirm()`（取消時 `stopPropagation` 防遮罩卡死，同 v2 做法）。
5. **編輯 inline 表單**：標題 input prefill + 標籤 select prefill（含「無標籤」）+ 儲存，POST `/edit/<id>` 一次送出。
6. **篩選列**：`active_tag` 存在時顯示「篩選中：X」+ ✕ 清除（連回 `/`）。

## Verification（closed loop）

```
/goal (1) 全部 templates/*.html 通過 Jinja2 解析 + html.parser feed；(2) orca-ide 真瀏覽器跑完 v3-tags-return.md §5 Frontend 全部 8 項（依 §7 裁決 3：⋮ 選單只斷言可見性開/關），stop after 3 tries
```

瀏覽器驗證操作細節（v2 驗證過的做法）：
- 在自己的 worktree 起 app：`docker run --rm -d --name todo-tags-fe-test -p 5001:5000 -v "$(pwd)":/app -w /app -e SECRET_KEY=test -e ADMIN_USERNAME=admin -e ADMIN_PASSWORD=admin_password_123 python:3.12-slim bash -c "pip install --quiet flask && python app.py"`，測完 `docker rm -f` 清掉。
- 瀏覽器只用 `tab create`/`goto`/`eval --page <browserPageId>`；**snapshot/screenshot/terminal wait 在這台機器都壞，不要用**。eval 的 JS 全用單引號（跳脫雙引號會被吃掉），回傳值在 `.result.result`。
- `confirm()` 用 `window.confirm=()=>true/false` 覆寫測兩種路徑。

3 次沒過或連續兩次同因失敗就停下回報 main。回報後 main 會獨立重驗。`## Answer`/`Status` 一律寫 master 路徑下這份檔案，`Status: resolved` 由 main 標記。

## Answer

**完成，/goal 第 1 次 try 全過。** Commit `66c2fac`（分支 `allisdonglincai/frontend-lane-tags`），改動僅 `templates/index.html` + `static/css/app.css`（+292/−17），無新依賴、admin.html 未動。

實作對照 Task 六項：
1. 標籤管理列：`.tag-manager` 1.5px dashed 虛線框，「我的標籤」+ chips（每個含 ✕ 表單 POST `/tags/delete/<id>` 帶 `confirm()`）+ 新增小表單（`maxlength="30" required`，POST `/tags/add`）。
2. 新增表單多 `<select name="tag_id">`（「無標籤」+ 使用者標籤）。
3. todo 列：狀態鈕、標題、`tag-chip` 徽章（pear 淡黃 pill `oklch(92% .09 95)`，有 tag_name 才顯示，連到 `/?tag_id=<id>`；未動既有 `status-tag`）、右側 ⋮ 鈕。
4. ⋮ dropdown：vanilla JS（delegation，約 30 行，放 index.html 底部）；「編輯」stroke 鉛筆 icon + 分隔線 + coral「刪除」垃圾桶 icon；點外面/Esc 關閉；⋮ 與「編輯」皆 `type="button"` 不觸發遮罩；刪除沿用 `confirm()` + `stopPropagation`。
5. 編輯 inline 表單：標題 prefill + 標籤 select prefill（`todo.tag_id == tag.id` selected，含「無標籤」）+ 儲存，一次 POST `/edit/<id>`。
6. 篩選列：`active_tag` 時顯示「篩選中：X」+「✕ 清除」連回 `/`；篩選下空列表另有文案。

驗證（皆真實執行）：
- 靜態：5 個 templates 全數通過 Jinja2 `get_template` 解析 + `html.parser` feed，無錯誤。
- 瀏覽器（orca-ide eval，docker 起 app 於 :5001，測畢已清）§5 Frontend 8 項全過：
  1. 登入見「我的標籤」；新增「工作」→ chip 出現、flash「已建立標籤「工作」」✅
  2. 新增 todo 選標籤 → 列上 `tag-chip`「工作」✅
  3. 點 ⋮ → menu 可見 open=true；點頁面他處 → closed=true（依裁決 3 只斷言可見性）✅
  4. 選單「編輯」→ 表單展開、title/tag 皆 prefill 正確、overlay 未觸發；改「買豆漿」+ 換「生活」→ 儲存後兩者皆更新、flash「已更新」✅
  5. 點徽章 → `?tag_id=2`、items=1、「篩選中：生活」；✕ → 回全部 items=2、篩選列消失 ✅
  6. 刪標籤「生活」（confirm 接受）→ chip 消失、原掛該標籤 todo 徽章消失但 todo 仍在 ✅
  7. 選單刪除 confirm 取消 → todo 仍在且 overlay 未卡（overlayStuck=false）；接受 → todo 消失 ✅
  8. 回歸：三態 pending→in_progress→done→pending 循環正常（含 bubble-pop 路徑）、⋮ 點擊不觸發遮罩 ✅

備註：`/frontend-design:frontend-design` 未安裝，依 operating-principles 退回 better-ui skill；設計全數沿用既有 tokens（無新色票，僅徽章底色照 §2 指定值）。


### Main 第二層驗證（獨立重跑，非採信自我陳述）

1. 靜態：python:3.12-slim 重跑 Jinja2 + html.parser，5 template 全 OK。
2. 瀏覽器：main 自起 container（:5001）以新帳號 `tagsmain` 獨立跑完 §5 全 8 項——管理列/建標籤 chip、新增 todo 掛標籤、⋮ 選單開（block）/點外面關（none）、編輯 prefill（title+tag）且改 title/清 tag 生效、`?tag_id=` 篩選 items:1 + ✕ 回全部、刪標籤後 chip 與列上徽章消失但 todo 保留、刪 todo confirm 取消保留/接受消失且遮罩全程 none、三態循環回歸正常。全過。
3. diff 只動 `templates/index.html` + `static/css/app.css`，admin.html 未動，無新依賴。

已 merge + push（master `01198e6`）。備註：驗證過程兩次斷言失敗均為 main 測試腳本問題（同 tick 讀選單狀態、選單 toggle 狀態未重置），非實作 bug。
