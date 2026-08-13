Type: task
Mode: execution
Lane: devops

開工前先讀 [operating-principles.md](../operating-principles.md)（stop conditions/cost ceilings、切勿假設應該沒問題、worktree 隔離規則、SOLID/KISS）與 [v1-contract.md](../v1-contract.md)（環境變數、驗證流程的權威定義）。

## Worktree

全部工作在 `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/devops-lane`（分支 `devops-lane`）下進行，不要碰 master 主 checkout。commit 到自己的分支即可，main 驗證通過後會負責合併回 master。

## Owned files

`Dockerfile`、`requirements.txt`、`scripts/verify_deploy.sh`（新檔案，本 ticket 建立）。不可改 `app.py` 或 `templates/`；若驗證過程中發現需要改動這兩者，用 `orca orchestration ask` 交給 main session 裁決，不要越界直接改。

## Task（見 [Ticket 20](20-v1-mvp-scope-reopen.md) 完整背景）

把 [v1-contract.md](../v1-contract.md) 的「Verify 用的完整流程」寫成一支可重複執行、非 0 即失敗的腳本 `scripts/verify_deploy.sh`：

1. `docker build -t todo-mvp .` — 失敗就中止並回傳非 0
2. 啟動 container，帶上 `SECRET_KEY`/`ADMIN_USERNAME`/`ADMIN_PASSWORD`（腳本裡自訂測試用的值即可，別跟真的密碼混用），等待就緒
3. `curl` 流程：註冊一個測試帳號 → 登入 → 新增一筆 todo → 連續 POST `/status/<id>` 三次確認狀態回到 `pending` → 登出
4. 用 `ADMIN_USERNAME`/`ADMIN_PASSWORD` 登入 → `GET /admin` 確認測試帳號與其 todo 出現在回應內容裡
5. `docker restart` 該 container，重新登入確認資料仍在
6. 不論成功或失敗都要清掉自己建立的 container（`docker rm -f`），不留殘留資源

腳本全過 = v1 MVP 的端對端部署驗證通過。

## Verification（closed loop）

```
/goal scripts/verify_deploy.sh 可執行、跑起來 exit code 是 0，stop after 6 tries
```

這支腳本依賴 backend lane 的路由都已經存在——如果 backend 還沒完成，先把腳本寫好、用現有（舊版）路由跑通建置/啟動的部分，等 backend Answer 填好之後再補完整流程，不要因為等別人而閒著不動。

`/goal` 每次嘗試後由獨立的 evaluator model 檢查腳本是否真的 exit 0，不是自己說了算。6 次還沒過就停下來，把失敗輸出（哪一步、什麼錯誤）寫進 Answer；若卡在需要改 `app.py`（例如 admin seed 邏輯有 bug），走 `orca orchestration ask`，不要自己硬繞過。

回報給 main 之後，main 會**獨立重跑一次 `scripts/verify_deploy.sh`**，不採信這裡的自我陳述——這是第二層驗證，跟 `/goal` 的 evaluator model 是不同的檢查者。

## Answer

（main session dispatch 後，由 devops lane 回報結果並在此記錄：腳本路徑、實際執行輸出、是否全綠）
