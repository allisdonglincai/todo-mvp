Type: task
Mode: execution
Lane: devops

## Owned files

`Dockerfile`、`requirements.txt`、`scripts/verify_deploy.sh`（新檔案，本 ticket 建立）。不可改 `app.py` 或 `templates/`；若驗證過程中發現需要改動這兩者（例如缺 health endpoint、SQLite 沒有正確持久化），用 `orca orchestration ask` 交給 main session 裁決，不要越界直接改。

## Task

把 [phase 1 指標](../01-mvp-hardening-scope.md) 中的第 2、3、4 項，寫成一支可重複執行、非 0 即失敗的腳本 `scripts/verify_deploy.sh`：

1. `docker build -t todo-mvp .` — 失敗就中止並回傳非 0
2. 啟動 container（背景模式，映射一個乾淨的 port），等待就緒後 `curl` `GET /` 確認回 200
3. 透過 `curl` POST `/add` 新增一筆、POST `/toggle/<id>` 切換完成狀態
4. `docker restart` 該 container，再次 `curl` `GET /` 確認剛剛新增的項目仍在（驗證 SQLite 持久化跨重啟）
5. 不論成功或失敗都要清掉自己建立的 container（`docker rm -f`），不留殘留資源

腳本全過 = phase 1 指標 2/3/4 通過。

## Verification（closed loop）

這個 lane 自己開工時用：

```
/goal scripts/verify_deploy.sh 可執行、跑起來 exit code 是 0，stop after 5 tries
```

`/goal` 每次嘗試後由獨立的 evaluator model 檢查腳本是否真的 exit 0，不是自己說了算。5 次還沒過就停下來，把失敗輸出（哪一步、什麼錯誤）寫進 Answer；若卡在需要改 `app.py`（例如缺 health endpoint 或持久化有 bug），走 `orca orchestration ask`，不要自己硬繞過。

回報給 main 之後，main 會**獨立重跑一次 `scripts/verify_deploy.sh`**，不採信這裡的自我陳述——這是第二層驗證，跟 `/goal` 的 evaluator model 是不同的檢查者。

## Answer

（main session dispatch 後，由 devops lane 回報結果並在此記錄：腳本路徑、實際執行輸出、是否全綠）
