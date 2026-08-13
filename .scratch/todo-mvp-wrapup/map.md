Label: wayfinder:map

## Destination

一個可用 Docker 本地部署、前後端具備、資料持久化在 SQLite 的 Todo app MVP（Flask，server-rendered，前後端同一 process）。這個 MVP 本身不是目的，真正的目的是練習「在時間盒內用結構化方式與 agent 協作交付」——Todo app 只是練習載體。這張 map 要釐清的是：現有 MVP 是否需要收尾/加固，以及範圍要不要繼續擴充或就此結案。

## Notes

- Tech stack（已定案，非本次 map 討論範圍）：Python + Flask（server-rendered）+ sqlite3（stdlib，無 ORM）
- 部署（已定案）：單一 Dockerfile，`docker build` + `docker run` 即可跑
- 核心功能（已實作並驗證跑得動）：新增 Todo、查詢列表、標記完成（toggle）、SQLite 持久化
- 目前使用 Flask dev server（尚未換成正式 WSGI server）— 是否要換，交由 [MVP 是否需要收尾/加固到可展示程度](issues/01-mvp-hardening-scope.md) 決定，不視為已定案
- 練習重點是「結構化協作」本身，Todo app 只是載體 — 評估收尾/擴充決策時，優先考慮是否服務這個練習目的，而非把 Todo app 當成要打磨的產品
- 每個 session 遇到需要拍板的問題時使用 `/grilling` 和 `/domain-modeling`

## Decisions so far

（尚無已關閉的 ticket）

## Not yet specified

- 若決定繼續擴充（見 [是否繼續擴充範圍，或在目前 scope 結案](issues/02-continue-or-close-scope.md)），實際要新增的功能清單與交付方式細節，待該 ticket 與 [下一步功能優先順序](issues/03-next-feature-priority.md) 解決後才會明朗

## Out of scope

- 刪除功能、多人帳號 — 使用者已明確排除於本次練習範圍外，非收尾/加固可重新討論的項目
