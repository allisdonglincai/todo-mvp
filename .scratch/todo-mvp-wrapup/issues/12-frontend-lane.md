Type: task
Mode: execution
Lane: frontend

## Owned files

`templates/`（含未來的 `static/`，目前不存在）。不可改 `app.py`、`Dockerfile`、`requirements.txt`；若需要這些檔案改動，用 `orca orchestration ask` 交給 main session 裁決。

## Task

審查 `templates/index.html`：語意是否正確（表單、checkbox、`{% for %}` 迴圈邏輯與後端欄位對得上）、有沒有殘留的除錯用標記或死程式碼、HTML 是否為合法標記。這個 MVP 沒有獨立前端框架，所以這裡的產出是「審查 + 就地修正」而不是新功能：若發現問題直接在 `templates/index.html` 內修好；若沒問題，在 Answer 記錄審查結論即可，不需要為了有事做而加東西。

## Verification（closed loop）

這個 lane 的任務本質是審查，沒有天生的機器可判斷通過條件，所以借用 backend 既有的迴歸測試當硬指標（唯讀執行 `test_app.py`，不代表擁有它）：

```
/goal 修改（或未修改）templates/index.html 後，pytest test_app.py 仍全部通過，且 python3 -c "from html.parser import HTMLParser; HTMLParser().feed(open('templates/index.html').read())" 不拋例外，stop after 3 tries
```

`pytest test_app.py` 會間接驗證渲染出來的 HTML 結構（`<li` 數量、`class="done"` 是否出現）沒有被你的修改破壞；`html.parser`（Python 內建，不用裝東西）抓明顯的標記錯誤。若審查後沒改東西，這兩項本來就會過，不用為了跑 `/goal` 硬改。

回報給 main 之後，main 會**獨立重跑一次上面兩個指令**，不採信這裡的自我陳述——這是第二層驗證，跟 `/goal` 的 evaluator model 是不同的檢查者。

## Answer

（main session dispatch 後，由 frontend lane 回報結果並在此記錄：審查結論、是否有修改）
