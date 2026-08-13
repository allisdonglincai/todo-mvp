Label: wayfinder:map

## Destination

一個可用 Docker 本地部署、前後端具備、資料持久化在 SQLite 的 Todo app **v1 MVP**（Flask，server-rendered，前後端同一 process），包含登入/註冊/驗證、per-user todo、admin 後台（看帳號清單與各帳號 todo）、三態狀態、loading 過渡、雙層輸入驗證。完整範圍見 [Ticket 20](issues/20-v1-mvp-scope-reopen.md) 與 [v1-contract.md](v1-contract.md)。這個 MVP 本身不是目的，真正的目的是練習「在時間盒內用結構化方式與 agent 協作交付」——Todo app 只是練習載體。

## Notes

- Tech stack（已定案，非本次 map 討論範圍）：Python + Flask（server-rendered）+ sqlite3（stdlib，無 ORM）— 已驗證：見 [Tech stack 驗證](issues/00-tech-stack-verification.md)
- 部署（已定案）：單一 Dockerfile，`docker build` + `docker run` 即可跑
- Phase 1 核心功能（已實作並驗證跑得動，v1 會在這之上重寫 schema/路由）：新增 Todo、查詢列表、標記完成（toggle）、SQLite 持久化
- 目前使用 Flask dev server，維持現狀不換 gunicorn（見 [MVP 是否需要收尾/加固到可展示程度](issues/01-mvp-hardening-scope.md)）
- **v1 MVP 範圍（取代原本「不擴充」的決議）**：見 [Ticket 20](issues/20-v1-mvp-scope-reopen.md) 完整決策記錄，路由/schema/驗證規則的權威定義在 [v1-contract.md](v1-contract.md)，三個 lane ticket（10/11/12）已依此重寫
- 練習重點是「結構化協作」本身，Todo app 只是載體 — 評估收尾/擴充決策時，優先考慮是否服務這個練習目的，而非把 Todo app 當成要打磨的產品
- 每個 session 遇到需要拍板的問題時使用 `/grilling` 和 `/domain-modeling`
- **執行覆寫（override "plan don't do"）**：這個 map 從 dispatch 階段開始，ticket 也承載實際執行（不只是決策）——三個 lane ticket（10/11/12）的產出是可執行的驗證腳本，由 main session 透過 orca-ide 直接 dispatch 並收斂結果，而非留給另一個 session 事後施工
- **Repo 狀態**：本目錄已 `git init`（root commit `1e355f8`）並 `orca repo add` 註冊進 Orca（repo id `7ddf919b-0818-4f43-bcc0-ff18b4f0f7a7`）。三個 lane 各自有獨立 git worktree（`backend-lane`/`frontend-lane`/`devops-lane` 分支），詳見 `coordinator-protocol.md` 的 handle/worktree 對應表——這是真正的檔案隔離，不只是約定
- **Lane 切分規則（by file，非 by role）**：這是 server-rendered 單一 process 的 monolith，沒有真的前後端分離，硬分角色只會讓兩個 lane 搶改同一個檔案。切分依現有檔案結構：backend lane 只碰 `app.py`；frontend lane 只碰 `templates/`、`static/`；devops lane 只碰 `Dockerfile`、`requirements.txt`。三個 lane 之間的介面（路由、session key、環境變數、template 變數、驗證規則）已經先在 [v1-contract.md](v1-contract.md) 定好，減少互相 ask 的來回；真的需要偏離 contract 才走 `orca orchestration ask`（必要時 `gate-create`）由 main session 裁決，不可越界直接改
- **獨立任務用 worktree，需要互相檢視進度的任務用 subagent**：backend/frontend/devops 檔案不重疊、只有零星跨 lane 需求，屬於獨立任務，各自開 worktree session；之後若出現需要頻繁互相看到對方進度的任務，改在 main session 內開 Task subagent 處理，不要開成獨立 worktree session（見 `operating-principles.md`）
- **Coordinator 協議與開工原則**：main session 的 dispatch → wait → verify → record 流程與 AFK 邊界寫在 `coordinator-protocol.md`；stop conditions/cost ceilings 與「切勿假設應該沒問題」寫在 `operating-principles.md`，四個 session（main + 三個 lane）開工前都要先讀後者

## Decisions so far

- [Tech stack 驗證](issues/00-tech-stack-verification.md) — 與程式碼實際核對相符：Flask + server-rendered 同 process + sqlite3 stdlib 無 ORM
- [MVP 是否需要收尾/加固到可展示程度](issues/01-mvp-hardening-scope.md) — 不加固（不換 gunicorn、不加錯誤處理），改以 4 項 deterministic 檢查作為 phase 1 stop condition
- ~~[是否繼續擴充範圍，或在目前 scope 結案](issues/02-continue-or-close-scope.md) — 原決議「在目前 scope 結案」，已被 Ticket 20 推翻~~
- [v1 MVP 範圍重新定義](issues/20-v1-mvp-scope-reopen.md) — 推翻 Ticket 02，正式納入登入/註冊/驗證 + admin 後台 + 三態狀態 + loading + 雙層輸入驗證 + SOLID/KISS 開發原則；細節見 [v1-contract.md](v1-contract.md)
- [Ticket 12 frontend lane](issues/12-frontend-lane.md) — resolved：五個 templates 依 v1-contract 建立/改寫（commit `f28084e`），main 獨立重跑 Jinja2/html.parser 靜態檢查 exit 0 確認通過，已合併回 master

## Not yet specified

（目前沒有未拆解的模糊區域；v1 MVP 的範圍已全數落成 ticket 10/11/12，細節在 v1-contract.md）

## Out of scope

- 刪除 todo 功能 — 使用者已明確排除於本次練習範圍外
- [下一步功能優先順序](issues/03-next-feature-priority.md) — 前提（在原 phase 1 範圍內繼續擴充）未成立；範圍後續改用 Ticket 20 的方式重新開啟，這個 ticket 本身仍然關閉不處理
