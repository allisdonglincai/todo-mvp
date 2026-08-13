Type: grilling
Status: resolved

## Question

[是否繼續擴充範圍，或在目前 scope 結案](02-continue-or-close-scope.md) 已決議在原本的 scope（新增/查詢/toggle/持久化）結案。但使用者後續要求加入登入/驗證/註冊 + admin 後台，這是否要正式推翻 Ticket 02 的收斂決議，重新定義「第一版 MVP」的範圍？

## Answer

推翻 Ticket 02。「第一版 MVP」正式重新定義為包含驗證系統與 admin 後台的版本，取代原本「不擴充」的決議。以下是這一輪 grilling 逐項確認過的決策，細節與後端/前端契約見 [v1-contract.md](../v1-contract.md)：

### 驗證系統
- 開放自由註冊（username + password，不含 email）
- 登入後才能用 Todo 功能；未登入導向登入頁；有登出
- 密碼雜湊用 `werkzeug.security`（Flask 既有依賴，不裝新套件）；登入狀態用 Flask 內建 `session`

### Admin 後台
- 第一個 admin 帳號透過 Docker 環境變數（`ADMIN_USERNAME`/`ADMIN_PASSWORD`）在 app 啟動時 seed，不做自助升級 admin
- Admin 可看：所有註冊帳號清單、各帳號的 todo（含建立時間、狀態）
- 非 admin 擋在 admin 路由外

### 資料模型
- 直接重建 schema，現有 demo 資料不保留
- `users`：username、password_hash、is_admin、created_at
- `todos`：加 user_id、created_at、status 三態（未處理 `pending`/進行中 `in_progress`/已完成 `done`，取代 boolean `done` 欄位）

### UI
- 新增登入頁、註冊頁、admin 儀表板頁面
- Todo 列表只顯示當前登入者自己的項目
- 狀態改成點擊循環三態的按鈕（取代原本的 checkbox）

### Cross-cutting 非功能需求（套用到所有頁面/表單）
- **Loading 過渡**：每個表單送出、每個連結點擊立即顯示 loading 遮罩，避免瀏覽器渲染新頁面前出現空白閃爍。純 vanilla JS/CSS，不用框架、不裝新套件
- **輸入驗證雙層把關**：每個表單欄位都要「HTML5 原生屬性做前端提示 + 後端二次驗證」，不能只靠前端。username/password/todo 標題都有各自的長度與格式限制；status 只能是三個合法值之一，後端要擋非法值
- **Design pattern**：四個 session 寫的程式碼都要照 KISS（預設模式，能簡單就不複雜）+ SOLID 裡實際適用的部分（主要是 SRP：route handler 只管接請求/呼叫邏輯/回應，驗證、密碼雜湊、DB 存取各自獨立成小函式），不要為了套用 pattern 而加沒人要用的彈性
- **Frontend lane 開發 UI 時使用 `/frontend-design:frontend-design`**（若該 session 沒裝這個 plugin，退回用 `better-ui`/`better-layout`/`better-typography`/`better-accessibility`）

### 維持 phase 1 既有決議不變
- Flask + sqlite3 stdlib、無 ORM；單一 Dockerfile 部署；server-rendered 同一 process
- 仍然不做刪除 todo 功能

三個 lane ticket（[10](10-devops-lane.md)/[11](11-backend-lane.md)/[12](12-frontend-lane.md)）已依這個範圍重寫，仍然是「檔案切分」而非「角色切分」，`app.py`/`templates/`/`Dockerfile`+`requirements.txt` 的界線不變，只是各自的工作內容大幅擴大。
