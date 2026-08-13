Type: grilling
Status: resolved

## Question

練習的核心目的是「在時間盒內用結構化方式與 agent 協作交付」，Todo app 只是載體。目前 MVP 已具備新增 / 查詢 / toggle / SQLite 持久化，且已驗證跑得動。

是否要繼續擴充功能範圍（例如：刪除、期限、標籤）？還是練習重點已經達成，可以在目前的 scope 就結案？

## Answer

在目前 scope 結案，不擴充 Todo 功能（不做刪除、期限、標籤）。這一輪要練的是 main session 透過 orca-ide 對三個 worker session（frontend/backend/devops）dispatch → verify → 收斂的流程本身，Todo app 功能維持現狀不變。三個 lane 的交付物是 [Ticket 01](01-mvp-hardening-scope.md) 定義的 phase 1 指標對應的驗證腳本，不是新功能。
