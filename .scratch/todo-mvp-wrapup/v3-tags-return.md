# V3 Return — 標籤（Tags）最終設計規格

> 設計討論 session 的 return mode 文件，交回 main/coordinator 審核後開 ticket。
> 使用者已透過互動 artifact 實際操作確認：**https://claude.ai/code/artifact/3bc390da-22d0-47a5-9b06-e16032433b39**（最終版 label: `edit-with-tag-select`）。
> 本文件是 v3 標籤功能的規格權威來源；與 v1-contract.md 的關係見第 4 節（純新增 + 一處既有路由擴充，不破壞既有行為）。

## 1. 最終方案（方案 B 收斂版）

**一句話**：per-user 受管理的標籤清單（`tags` 表），todo 單選指派（`todos.tag_id`），列表可按標籤篩選；每列 todo 的動作收進 ⋮ dropdown menu（編輯/刪除），編輯表單內含標籤下拉，一次送出標題 + 標籤。

### 範圍定義

- 標籤是 **per-user 實體**：使用者自行建立/刪除，同名不可重複（`UNIQUE(user_id, name)`）。無預設標籤、無顏色自訂、無階層（皆已明確排除，見第 6 節）。
- 一個 todo 最多一個標籤（`tag_id` 可 NULL = 無標籤）。
- 標籤名稱驗證：trim 後非空、上限 30 字（前端 `maxlength="30" required` + 後端二次驗證，慣例同 `validate_title`）。
- 刪除標籤：該標籤下所有 todo 的 `tag_id` 置 NULL（todo 本身不動），需 `confirm()` 二次確認。
- 篩選：單一標籤篩選，走 `GET /?tag_id=<id>` query param，無 client state。第一版**不保留跨操作的篩選狀態**（篩選頁做完任何操作 redirect 回 `/` 即回到全部）——使用者已同意此 KISS 取捨。

### User flow（登入後從 `/` 開始）

1. **建立標籤**：列表上方「我的標籤」管理列（虛線框）：現有標籤 chips + 「新標籤」input + ＋鈕 → POST `/tags/add` → flash「已建立標籤「X」」。
2. **新增 todo 附標籤**：新增表單 = 標題 input + 標籤 `<select>`（「無標籤」+ 自己的標籤）+ 新增鈕 → POST `/add`（多收 `tag_id`）。
3. **todo 列呈現**：狀態鈕、標題、標籤徽章（黃底 pill，有才顯示）、右側 ⋮ 鈕。常駐控件僅此 3+1 個。
4. **⋮ 選單**：點開浮出 menu——「編輯」（鉛筆 icon）、分隔線、紅色「刪除」（垃圾桶 icon）。點外面或 Esc 關閉。
5. **編輯**：選單點「編輯」→ 該列下方展開 inline 表單：標題 input（prefill）+ 標籤 select（prefill 現值，含「無標籤」）+ 儲存鈕 → POST `/edit/<id>`（既有路由擴充收 `tag_id`）→ flash「已更新」。
6. **刪除 todo**：選單點「刪除」→ 原生 `confirm()` → POST `/delete/<id>`（既有路由不變）。
7. **篩選**：點任何標籤徽章（todo 列上的或管理列的）→ `GET /?tag_id=n` → 只列該標籤 todo，頂部顯示「篩選中：X ✕」，✕ 連回 `/`。
8. **刪除標籤**：管理列 chip 上的 ✕ → `confirm()`（提示其下 todo 會變回無標籤）→ POST `/tags/delete/<id>` → flash。

### Statechart（與既有狀態的關聯）

```
標籤生命週期：   (不存在) --POST /tags/add--> [存在]
                 [存在] --POST /tags/delete/<id>--> (不存在；所屬 todos.tag_id 置 NULL)

頁面篩選狀態：   [全部 /] --點徽章--> [篩選 /?tag_id=n] --點✕ 或任何操作後 redirect /--> [全部]
                 （狀態只存在於 URL，無 client state）

todo 列 UI 狀態（新增，vanilla JS）：
                 [收合] --點⋮--> [選單開] --點編輯--> [edit-form 展開（標題+標籤）]
                 [選單開] --點外面/Esc/點刪除--> [收合]
                 [edit-form 展開] --儲存 submit--> 整頁刷新回 [收合]

與既有 statechart 的交互：
  - 三態循環（/status）：完全不變，狀態鈕仍常駐列上，不進選單。
  - v2 的 edit-form 展開/收合：入口從常駐「編輯」鈕改為 ⋮ 選單項，表單本體多一個 tag select，其餘不變。
  - v2 的 confirm() 刪除：不變，入口改為選單項；tags 刪除沿用同一 confirm() 模式。
  - loading 遮罩：⋮ 鈕與選單的「編輯」是 type="button"（不觸發導頁），不得觸發遮罩；
    選單的「刪除」與各表單 submit 照既有遮罩規則走。
```

## 2. UI 規格（Bubble 設計系統內，見 artifact 實際效果）

- **標籤管理列**：`1.5px dashed var(--color-rule)` 圓角框，內含小標「我的標籤」、chips、新增小表單。
- **標籤徽章**：pear 色系 pill（淡黃底 `oklch(92% .09 95)` + 邊框），可點（連結到篩選）。**class 命名避開既有 `status-tag`**，建議 `tag-chip`。
- **⋮ 鈕**：透明底、hover 淺色圓角方塊，三點 SVG icon。
- **Dropdown menu**：白底圓角卡 + 浮起陰影，項目 = stroke icon + 文字；「刪除」coral 色、上方分隔線；`role="menu"`/`aria-expanded`；點外面與 Esc 關閉。實作用少量 vanilla JS（或原生 `<details>` 零 JS 版，frontend lane 自行判斷，禁止引入依賴）。
- **編輯 inline 表單**：`flex-basis:100%` 換到列內下一行：標題 input（flex:1）+ tag select + pear「儲存」。
- 篩選列：淺色底圓角條「篩選中：<b>X</b>」+「✕ 清除」outline 小鈕。

## 3. 資料模型 delta

```sql
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, name)
);
-- todos 加欄（既有表用 ALTER TABLE ADD COLUMN，init_db 對新舊 DB 都要能跑）
ALTER TABLE todos ADD COLUMN tag_id INTEGER REFERENCES tags(id);
```

注意：demo container 的 `todo.db` 是既有資料庫，`init_db()` 必須容忍 `tag_id` 欄已存在/不存在兩種情況（例如 `PRAGMA table_info` 檢查後才 ALTER）。

## 4. 路由 delta（v1-contract.md 的增補）

| Method | Path | 需要登入 | 說明 |
|---|---|---|---|
| POST | `/tags/add` | 是 | 新增：收 `name`，trim 非空、≤30 字、該 user 下不重複（違反則 flash 錯誤）；成功 flash、redirect `/` |
| POST | `/tags/delete/<int:tag_id>` | 是 | 必須是自己的 tag 否則 404；先把該 user 所有 `tag_id` 等於它的 todo 置 NULL，再刪 tag；flash、redirect `/` |
| GET | `/` | 是 | **擴充**：支援 `?tag_id=<int>` 篩選（僅限自己的 tag；無效值視同無篩選）；template 多傳 `tags`（該 user 全部標籤）與 `active_tag` |
| POST | `/add` | 是 | **擴充**：多收選填 `tag_id`，非空時必須是自己的 tag（否則忽略或 flash 錯誤，擇一但要有測試） |
| POST | `/edit/<int:todo_id>` | 是 | **擴充**：多收 `tag_id`（空字串 = 設回 NULL），驗證同上；標題驗證沿用 `validate_title()` 不變 |

既有 `/status`、`/delete`、auth、admin 路由**行為不變**。admin 頁可順帶在 todo 旁顯示標籤名（LEFT JOIN），非必要項。

Template 變數 delta：`index.html` 的 `todos` 每筆多 `tag_id`/`tag_name`（LEFT JOIN 取得）；新增 `tags`（list of {id,name}）、`active_tag`（篩選中的 tag row 或 None）。

## 5. 給 coordinator 的 ticket 驗收條件建議

### Backend（pytest，接續 `test_app.py` 既有風格）

1. `/tags/add`：成功新增；空白/純空格 400 流程（flash + redirect）；>30 字拒絕；同 user 重名拒絕；不同 user 可同名。
2. `/tags/delete/<id>`：刪自己的成功且其下 todo 的 `tag_id` 變 NULL、todo 仍在；刪別人的 404；未登入 redirect login。
3. `/add` 帶 `tag_id`：todo 正確關聯；帶別人的 `tag_id` 不得關聯成功。
4. `/edit/<id>` 帶 `tag_id`：標題與標籤同時更新；`tag_id` 空字串設回 NULL；帶別人的 `tag_id` 不得生效；既有「非本人 todo 404」「標題驗證」測試不回歸。
5. `GET /?tag_id=`：只回該標籤的 todo；帶別人的/不存在的 `tag_id` 視同無篩選；既有全部列表行為不變。
6. `init_db()` 對「已有 todos 表但無 `tag_id` 欄」的既有 DB 能升級、對全新 DB 能建立（migration 測試）。

### Frontend（orca-ide 瀏覽器自動化，`eval` 讀 DOM，不用 snapshot/screenshot）

1. 登入後可見「我的標籤」管理列；輸入新標籤送出後 chip 出現、flash 顯示。
2. 新增 todo 時下拉選標籤，列上出現對應 `tag-chip` 徽章。
3. 點 ⋮ 開啟選單（`aria-expanded` 變 true、menu 可見）；點頁面其他處選單關閉。
4. 選單點「編輯」→ inline 表單展開且標題 input 與 tag select 都 prefill 正確 → 改標題+換標籤 → 儲存 → 刷新後兩者皆更新、flash「已更新」。
5. 點標籤徽章 → URL 含 `?tag_id=`、列表只剩該標籤 todo、「篩選中」列出現；點 ✕ 回全部。
6. 管理列刪除標籤（confirm 接受）→ chip 消失、原掛該標籤的 todo 徽章消失但 todo 仍在。
7. 選單「刪除」confirm 取消 → todo 仍在；接受 → todo 消失。
8. 回歸：三態循環按鈕、loading 遮罩（⋮ 與「編輯」不觸發遮罩、不卡死）。

### Lane 劃分

沿用既有 owned files：backend = `app.py`/`test_app.py`；frontend = `templates/`/`static/`。dropdown 的 CSS/JS 放 `static/`（或 `base.html`/`index.html` 內），屬 frontend。無 devops ticket（無新依賴），但 merge 後照 v2-handoff §4-5 慣例呼叫 devops session rebuild/redeploy container，main 再用瀏覽器自動化做最終驗證。

## 6. 討論中被否決的方向與原因

- **方案 A（todos 直接加 text 欄、自由輸入）**：delta 最小，但無集中管理、拼字易不一致。使用者選 B。
- **方案 C（many-to-many 多標籤）**：功能最完整，但兩張新表 + 四路由、每掛/移一標籤一次整頁刷新、todo 列控件密度過高。否決（YAGNI）。
- **三動作鈕（標籤/編輯/刪除）一字排開**：視覺過於複雜，改為 ⋮ dropdown menu（參照 claude.ai 的列表選單慣例）。
- **選單內獨立「標籤」動作**：後改為併入編輯表單（標題 + 標籤一次儲存），少一條路由、少一個 UI 狀態。
- **篩選狀態跨操作保留（表單帶 `?tag_id=`）**：第一版不做，KISS；使用者同意，日後在意再加。
- 標籤顏色自訂、階層標籤、預設標籤：未被要求，不做。

## 7. Coordinator 審核（對抗式，已通過，含 4 項裁決）

規格可執行，開 ticket 23（backend）/24（frontend）。模糊點裁決如下，ticket 以此為準：

1. `/add`、`/edit` 收到非法/非本人 `tag_id`（含非數字）：**靜默忽略，視同無標籤（NULL）**，主要操作（新增/改標題）照常完成。不 flash 錯誤。
2. 標籤名驗證失敗走既有慣例：**302 redirect `/` + flash 錯誤**，不是 HTTP 400。
3. Frontend 驗收對 ⋮ 選單只斷言**可見性開/關**，不斷言 `aria-expanded`（讓 JS dropdown 與 `<details>` 兩種實作都合法）。
4. Admin 頁標籤顯示**排除出 v3 範圍**，backend/frontend 都不動 admin 相關程式。
