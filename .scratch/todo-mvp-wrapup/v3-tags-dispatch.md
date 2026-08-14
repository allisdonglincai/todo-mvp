# V3 Dispatch — 【標籤（Tags）】議題設計討論

> 寫給**負責標籤議題的新 session**（design/discussion session，不是 implement session）。這是 dispatch mode 文件：你的任務是理解現況 → 提三個設計提案 → 與使用者討論收斂 → 用 Artifacts 做互動畫面確認 → 產出 return mode 文件交回 main/coordinator 審核。**你不寫任何程式碼進 repo、不開 worktree、不碰 git**——implement 是收斂後由 coordinator 開 ticket 另派 session 做的事。

## 0. 開工前必讀（權威文件）

- [operating-principles.md](operating-principles.md) — KISS/SRP、切勿假設應該沒問題。設計提案也適用：不提沒人要的彈性。
- [v1-contract.md](v1-contract.md) — 現有路由/schema/session/驗證規則的權威定義（含 v2 的 `/edit`/`/delete`）。你的提案必須明確說明與這份契約的關係（新增哪些路由/欄位，動不動得到既有行為）。
- [map.md](map.md) — 決策歷史。特別注意：標籤曾在 [issues/02](issues/02-continue-or-close-scope.md) 被決議「不做」，這次是重新開題，不是延續舊決議。
- `README.md`（repo 根目錄）— Features 區塊有各頁截圖與說明。
- [demo-brief.md](demo-brief.md) — user flow 慣例與 demo 帳號（admin 密碼是 `admin_password_123`）。

## 1. 專案現況（截至 master `016abb1`，2026-08-14）

### 架構

- **Tech stack**：Python + Flask（server-rendered，單一 process）+ sqlite3（stdlib，無 ORM）。無前端框架、無 build 工具，互動全是 vanilla JS + 表單 POST。密碼雜湊 Werkzeug、登入態 Flask session。
- **部署**：單一 Dockerfile；demo container `todo-mvp-demo` 跑在 `localhost:5000`。
- **設計系統**：`design.md` 定義的 Bubble 主題（鎖定），樣式集中在 `static/css/app.css`，共用 layout 在 `templates/base.html`（含 loading 遮罩 + flash 訊息區）。

### 資料模型（`todos` 表）

`id / user_id / title / status('pending'|'in_progress'|'done') / created_at`——**沒有任何標籤相關欄位**。

### 路由（v1-contract.md 為準，全部是動詞在前的 POST 表單風格，無 PUT/DELETE method）

`/register`、`/login`、`/logout`（POST）、`/`（列表）、`/add`、`/status/<id>`（三態循環）、`/edit/<id>`（v2）、`/delete/<id>`（v2）、`/admin`。

## 2. 畫面元素與操作互動流程（設計提案要對接的現實）

### `templates/index.html`（主畫面，登入後）

每筆 todo 是一個 `.todo-item`（flex row，`flex-wrap: wrap`），由左到右：

1. **狀態按鈕**（`.status-*` 配色）：顯示中文狀態文字（待處理/進行中/已完成），點一下 POST `/status/<id>` 循環到下一態，整頁刷新。
2. **`.todo-title`**：標題文字。
3. **「編輯」按鈕**（`type="button"`）：onclick 展開同列隱藏的 `.edit-form`（inline 表單，input prefill 現有 title、`maxlength="200" required`），「儲存」送出 POST `/edit/<id>`。
4. **「刪除」按鈕**：表單 POST `/delete/<id>`，`onsubmit` 用原生 `confirm()` 二次確認；取消時 `event.stopPropagation()` 防止 loading 遮罩誤觸。

列表上方是新增表單（input `maxlength="200"` + 送出鈕 POST `/add`）；空列表顯示「還沒有待辦事項」。頁面頂部有 flash 訊息區（`role="status"`）。

### `templates/admin.html`

每個帳號一個區塊，其下列出該帳號所有 todo；每筆右側有 `.status-tag` 徽章顯示三態狀態。**注意：`status-tag` 這個 class 名稱跟「標籤功能」無關**，它只是狀態徽章——你的提案若引入真正的 tag UI，命名要避開這個既有 class 的混淆。

### 互動邏輯的共通約束

- 所有互動 = 表單 POST → redirect `/` → 整頁刷新 + flash 訊息。**沒有 AJAX、沒有 client-side state**。
- `base.html` 的 loading 遮罩監聽 `a[href]`/submit 按鈕的 click 才顯示（v1 曾因監聽過寬卡死，修過一次）；任何新互動元素要嘛走這個模式，要嘛明確處理遮罩。
- 前端 HTML5 屬性 + 後端二次驗證雙層把關，是既有慣例。

## 3. 你的任務（依序，不要跳步）

1. **理解**：讀完第 0 節文件 + 實際看 `app.py`/`templates/`/`static/css/app.css`，必要時開 `localhost:5000` 實際操作一輪（帳號自己註冊；admin 帳密見上）。
2. **三個設計提案**：針對【標籤】提出三個**彼此有真實取捨差異**的方案（不是同一方案的三種皮）。每個提案必須包含：
   - **範圍定義**：標籤能做什麼（建立/指派/篩選/刪除？預設標籤還是自由輸入？per-user 還是全域？）
   - **User flow**:從登入後進 `/` 開始，逐步描述使用者怎麼建立、指派、使用標籤，怎麼跟既有的新增/編輯/刪除/三態流程交織
   - **Statechart**：標籤生命週期與頁面狀態轉移圖（文字或 mermaid 皆可），**必須標明與現有 statechart 的關聯**——三態循環、edit-form 展開/收合、confirm 刪除這些既有狀態如何與標籤狀態互動
   - **與 v1-contract 的 delta**：新增哪些表/欄位、哪些路由、哪些 template 變數，動不動得到既有介面
   - **取捨聲明**：這個方案犧牲了什麼、為什麼值得
   - 全部提案都要守專案既有約束：server-rendered、表單 POST、無新依賴、Bubble 設計系統
3. **討論**：把三案攤給使用者，聽取回饋、來回調整，收斂成一案（可以是混合案）。
4. **Artifacts 互動稿**：收斂後，用 Artifacts（HTML artifact，模擬 Bubble 主題的樣式與現有頁面結構）做出**可互動的畫面 demo**讓使用者實際點看看標籤的操作效果（指派、篩選等核心流程要能點）。這是設計驗證，不是實作——artifact 裡可以用 client-side JS 模擬 server 行為。依使用者回饋迭代到確認沒問題。
5. **Return mode 文件**：使用者確認後，撰寫 return 文件（建議放 `.scratch/todo-mvp-wrapup/v3-tags-return.md`），內容至少：最終方案完整規格（範圍、user flow、statechart、contract delta、UI 規格與 artifact 連結）、討論中被否決的方向與原因、給 coordinator 開 ticket 用的驗收條件建議（backend 可 pytest 驗證的行為清單、frontend 可瀏覽器自動化驗證的操作清單）。交回給 main/coordinator 審核。

## 4. 邊界（不能違反）

- 這個 session **只做設計與討論**：不改 `app.py`/`templates/`/`static/`/`Dockerfile`，不 commit、不 push、不開 worktree。
- Return 文件與任何筆記寫在 master 主 checkout 的 `.scratch/todo-mvp-wrapup/` 下（唯一真相來源），不要另開散落的檔案。
- 提案守 KISS：這個專案曾明確拒絕過為了未來彈性加抽象層；標籤方案的第一版不需要「以後可能要的」東西（例如標籤顏色自訂、階層標籤），除非使用者主動要求。
- 卡住或需要 coordinator 裁決（例如想動 v1-contract 既有行為）就停下來標明問題，不要自行假設。

## 5. 後續流程（你不用做，但要知道你的產出會被怎麼用）

Return 文件交回後：coordinator 審核 → 照 `issues/` 既有格式（參考 [21](issues/21-backend-lane-crud.md)/[22](issues/22-frontend-lane-crud.md)）開 backend/frontend ticket → 開新 worktree 派給 implement session 用 `/implement` + `/goal` 執行 → 兩層獨立驗證 → merge → devops rebuild container → coordinator 瀏覽器最終驗證。你的驗收條件建議寫得越可執行，ticket 就開得越準。
