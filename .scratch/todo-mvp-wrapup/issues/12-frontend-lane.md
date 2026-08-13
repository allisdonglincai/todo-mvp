Type: task
Mode: execution
Lane: frontend

## Owned files

`templates/`（含未來的 `static/`，目前不存在）。不可改 `app.py`、`Dockerfile`、`requirements.txt`；若需要這些檔案改動，用 `orca orchestration ask` 交給 main session 裁決。

## Task

審查 `templates/index.html`：語意是否正確（表單、checkbox、`{% for %}` 迴圈邏輯與後端欄位對得上）、有沒有殘留的除錯用標記或死程式碼、HTML 是否為合法標記。這個 MVP 沒有獨立前端框架，所以這裡的產出是「審查 + 就地修正」而不是新功能：若發現問題直接在 `templates/index.html` 內修好；若沒問題，在 Answer 記錄審查結論即可，不需要為了有事做而加東西。

## Answer

（main session dispatch 後，由 frontend lane 回報結果並在此記錄：審查結論、是否有修改）
