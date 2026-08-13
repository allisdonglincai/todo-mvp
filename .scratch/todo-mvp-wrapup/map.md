Label: wayfinder:map

## Destination

一個可用 Docker 本地部署、前後端具備、資料持久化在 SQLite 的 Todo app MVP（Flask，server-rendered，前後端同一 process）。這個 MVP 本身不是目的，真正的目的是練習「在時間盒內用結構化方式與 agent 協作交付」——Todo app 只是練習載體。這張 map 要釐清的是：現有 MVP 是否需要收尾/加固，以及範圍要不要繼續擴充或就此結案。

## Notes

- Tech stack（已定案，非本次 map 討論範圍）：Python + Flask（server-rendered）+ sqlite3（stdlib，無 ORM）— 已驗證：見 [Tech stack 驗證](issues/00-tech-stack-verification.md)
- 部署（已定案）：單一 Dockerfile，`docker build` + `docker run` 即可跑
- 核心功能（已實作並驗證跑得動）：新增 Todo、查詢列表、標記完成（toggle）、SQLite 持久化
- 目前使用 Flask dev server，維持現狀不換 gunicorn（見 [MVP 是否需要收尾/加固到可展示程度](issues/01-mvp-hardening-scope.md)）
- 練習重點是「結構化協作」本身，Todo app 只是載體 — 評估收尾/擴充決策時，優先考慮是否服務這個練習目的，而非把 Todo app 當成要打磨的產品
- 每個 session 遇到需要拍板的問題時使用 `/grilling` 和 `/domain-modeling`
- **執行覆寫（override "plan don't do"）**：這個 map 從 dispatch 階段開始，ticket 也承載實際執行（不只是決策）——三個 lane ticket（10/11/12）的產出是可執行的驗證腳本，由 main session 透過 orca-ide 直接 dispatch 並收斂結果，而非留給另一個 session 事後施工
- **Repo 狀態**：本目錄已 `git init`（root commit `1e355f8`），純粹為了讓 orca-ide 的 worktree/repo 相關指令可運作；尚未 `orca repo add` 註冊進 Orca
- **Lane 切分規則（by file，非 by role）**：這是 server-rendered 單一 process 的 monolith，沒有真的前後端分離，硬分角色只會讓兩個 lane 搶改同一個檔案。切分依現有檔案結構：backend lane 只碰 `app.py`；frontend lane 只碰 `templates/`（含未來的 `static/`）；devops lane 只碰 `Dockerfile`、`requirements.txt`。任何 lane 需要另一個 lane 範圍內的改動，必須透過 `orca orchestration ask`（必要時 `gate-create`）由 main session 裁決，不可越界直接改
- **Coordinator 協議**：main session 的 dispatch → wait → verify → record 流程與 AFK 邊界寫在 `coordinator-protocol.md`，每個 session 開工前先讀

## Decisions so far

- [Tech stack 驗證](issues/00-tech-stack-verification.md) — 與程式碼實際核對相符：Flask + server-rendered 同 process + sqlite3 stdlib 無 ORM
- [MVP 是否需要收尾/加固到可展示程度](issues/01-mvp-hardening-scope.md) — 不加固（不換 gunicorn、不加錯誤處理），改以 4 項 deterministic 檢查作為 phase 1 stop condition
- [是否繼續擴充範圍，或在目前 scope 結案](issues/02-continue-or-close-scope.md) — 在目前 scope 結案，這一輪只練 main session 透過 orca-ide dispatch 三個 worker lane 的機制本身

## Not yet specified

（目前沒有未拆解的模糊區域；phase 1 的收尾工作已全數落成 ticket 10/11/12）

## Out of scope

- 刪除功能、多人帳號 — 使用者已明確排除於本次練習範圍外，非收尾/加固可重新討論的項目
- [下一步功能優先順序](issues/03-next-feature-priority.md) — 前提（繼續擴充）未成立，隨 ticket 02 收斂為「結案」而失效，關閉不處理
