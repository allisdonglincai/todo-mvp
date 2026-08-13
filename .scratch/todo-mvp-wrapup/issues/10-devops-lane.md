Type: task
Mode: execution
Lane: devops
Status: claimed

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

**腳本路徑**：`scripts/verify_deploy.sh`（devops-lane worktree，已 commit：`ad3417e`）

**內容**：依 v1-contract.md 完整流程實作 6 步驟——`docker build` → 帶 `SECRET_KEY`/`ADMIN_USERNAME`/`ADMIN_PASSWORD` 啟動 container 並等待就緒（用連線是否建立判斷，不綁定特定路由，讓建置/啟動這段不依賴 backend 進度）→ curl 流程（register → login → add → 連續切換狀態三次確認回到 pending，中間也檢查有經過 in_progress/done → logout）→ admin 登入 + `GET /admin` 內容檢查測試帳號與 todo 都出現 → `docker restart` 後重新登入確認資料仍在 → trap 確保不論成敗都 `docker rm -f` 清掉 container。全程用獨立 cookie jar 區分一般使用者與 admin 的 session。

**實際執行輸出**（在 devops-lane worktree、對目前分支上的 `app.py` 執行）：

```
==> 1/6 docker build -t todo-mvp .
...（build 全部 cached/成功）
==> 2/6 start container, wait for readiness
==> 3/6 curl flow: register -> login -> add todo -> cycle status x3 -> logout
FAIL: POST /register — expected HTTP 302, got 404
EXIT CODE: 1
```

**是否全綠**：否，`exit 1`。**Build 與啟動（步驟 1–2）已驗證通過**——這是目前 devops-lane 這份舊版 `app.py`（還沒有 `/register` 等 v1 路由）能驗證到的極限，符合 ticket 裡「backend 還沒完成，先把腳本寫好、跑通建置/啟動」的預期，不是腳本本身的 bug。卡在 [Ticket 11 backend lane](11-backend-lane.md) 還沒收斂（目前 `backend-lane` 分支上 `app.py` 仍是舊版，`Status: claimed`，無 Answer）——`/register` 等路由尚未存在，curl 流程從第一步就 404。

失敗後容器已被 trap 正確清掉（`docker ps -a` 確認無殘留）。

**下一步**：不需要重新 dispatch devops——腳本已依 v1-contract 的最終路由/欄位契約寫好，backend lane 完成後不用改腳本，直接重跑 `scripts/verify_deploy.sh` 即可驗證完整流程。因為卡住原因是跨 lane 依賴（非 devops 自身重試能解決的失敗），依 operating-principles 的 cost ceiling 原則沒有繼續耗用 `/goal` 的 6 次嘗試去撞同一個因 backend 未完成而必然出現的 404。

Status 維持 `claimed`（未達成 exit 0 的目標，不能標 resolved）；等 backend lane 的 Answer 填好、`app.py` 換成 v1 路由後，重跑本腳本即可轉 `resolved`。
