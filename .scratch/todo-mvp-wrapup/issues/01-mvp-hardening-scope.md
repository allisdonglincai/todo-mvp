Type: grilling

## Question

目前 Todo app MVP（新增 / 查詢列表 / 標記完成 toggle / SQLite 持久化）已經用 Docker 實際跑起來驗證過，基本功能可動。是否需要進一步收尾/加固到「可以展示」的程度？具體候選項目：

- 是否要把目前的 Flask dev server 換成正式 WSGI server（例如 gunicorn）
- 是否要加上基本錯誤處理（例如空白輸入、資料庫連線失敗）

還是維持現狀，視為此次「時間盒內結構化協作」練習的目的已達成、不需要再加固？
