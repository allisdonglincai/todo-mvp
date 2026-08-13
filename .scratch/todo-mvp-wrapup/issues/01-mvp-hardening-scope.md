Type: grilling
Status: resolved

## Question

目前 Todo app MVP（新增 / 查詢列表 / 標記完成 toggle / SQLite 持久化）已經用 Docker 實際跑起來驗證過，基本功能可動。是否需要進一步收尾/加固到「可以展示」的程度？具體候選項目：

- 是否要把目前的 Flask dev server 換成正式 WSGI server（例如 gunicorn）
- 是否要加上基本錯誤處理（例如空白輸入、資料庫連線失敗）

還是維持現狀，視為此次「時間盒內結構化協作」練習的目的已達成、不需要再加固？

## Answer

不換 gunicorn、不加額外錯誤處理。改用 4 項可直接執行的 deterministic 檢查作為 phase 1 的完成指標（stop condition），全部通過即視為 phase 1 完成：

1. `pytest test_app.py` — 全綠
2. `docker build -t todo-mvp .` — exit 0
3. container 啟動後 `curl` `GET /` 回 200
4. 新增 → toggle → `docker restart` container → 資料仍在（驗證 SQLite 持久化跨重啟）

這 4 項由 `.scratch/todo-mvp-wrapup/issues/10-devops-lane.md`、`11-backend-lane.md`、`12-frontend-lane.md` 分工落地為可執行腳本。
