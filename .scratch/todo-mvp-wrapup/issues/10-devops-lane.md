Type: task
Mode: execution
Lane: devops
Status: resolved

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

**腳本路徑**：`scripts/verify_deploy.sh`（devops-lane worktree，已 commit：`ad3417e`、`6c606d6`）

**內容**：依 v1-contract.md 完整流程實作 6 步驟——`docker build` → 帶 `SECRET_KEY`/`ADMIN_USERNAME`/`ADMIN_PASSWORD` 啟動 container 並等待就緒（用連線是否建立判斷，不綁定特定路由，讓建置/啟動這段不依賴 backend 進度）→ curl 流程（register → login → add → 連續切換狀態三次確認回到 pending → logout）→ admin 登入 + `GET /admin` 內容檢查測試帳號與 todo 都出現 → `docker restart` 後重新登入確認資料仍在 → trap 確保不論成敗都 `docker rm -f` 清掉 container。全程用獨立 cookie jar 區分一般使用者與 admin 的 session。

**兩處硬化（`6c606d6`，寫完後自我 review 抓到的）**：
1. 狀態切換的驗證改成直接查 container 裡的 sqlite（`docker exec ... python -c "..."` 讀 `todos.status`），不再 grep HTML body 找 `pending`/`in_progress`/`done` 字串——因為 `templates/` 是別的 lane 的檔案，UI 上按鈕文字/CSS class/圖例都可能合法地包含這些字，會導致明明 backend 邏輯正確卻被腳本誤判 FAIL，main 也無法區分是腳本的鍋還是 backend 的鍋。POST 仍然照常打 `/status/<id>`（還是在測真正的路由行為），只是拿 ground truth 驗證換成資料庫而不是不受控的 markup。
2. `post`/`get_code`/`get_body`/todo_id 查詢原本在 `set -e` + `pipefail` 下，curl 連線失敗或 grep 找不到東西時會讓腳本在賦值那行直接被殺掉，跳過原本設計要印出來的 `FAIL: ...` 標籤，main 會看到不帶原因的中止。已改成 helper 內部自己 `|| code="000"` / `|| true` 接住失敗，讓後面的 `require_code`/`require_eq` 一定有機會印出清楚的失敗原因再 exit 1。

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

**Status 說明**：dispatch 訊息原本要求完成後設 `Status: resolved`，但這裡刻意沒有照做——ticket 本身的 `/goal` 目標是「腳本跑起來 exit code 0」，目前是 `exit 1`（原因如上，卡在 backend），不算達成。且依 `coordinator-protocol.md`「兩層驗證」，`Status: resolved` 應該是 main 自己重跑腳本驗證通過後才標記，devops 自己標 resolved 等於球員兼裁判。Status 維持 `claimed`；等 backend lane 的 Answer 填好、`app.py` 換成 v1 路由後，重跑本腳本（不用改腳本本身）即可轉 `resolved`。

### Main 第二層驗證（獨立重跑，非採信自我陳述）

三個 lane 都合併回 master 後（backend `647337b`、frontend `4f9e3d2`、devops `b5be3f1`），main 在 master 主 checkout 直接執行 `bash scripts/verify_deploy.sh`（未經任何修改，沿用 devops 寫的原始腳本）：

```
==> 1/6 docker build -t todo-mvp .
...
==> 2/6 start container, wait for readiness
==> 3/6 curl flow: register -> login -> add todo -> cycle status x3 -> logout
==> 4/6 admin login -> GET /admin shows test user + todo
==> 5/6 docker restart -> re-login -> confirm data persisted
==> 6/6 cleanup (handled by trap on exit)
PASS: full deploy verification flow succeeded
EXIT_CODE=0
```

6 個步驟全綠，`docker ps -a` 確認 trap 已清掉 `todo-mvp-verify` container，無殘留。這次執行用的是三個 lane 合併後的真實 `app.py` + `templates/`（不是 devops 自己 worktree 裡的舊版），也是這一輪唯一一次端對端跑通完整流程——順便驗證了 [Ticket 11](11-backend-lane.md) pytest 用 `DictLoader` stub 沒覆蓋到的「backend context 變數與 frontend 真實樣板實際搭配」這塊，沒有出現落差。

確認通過，`Status: resolved`。這也是 [v1-contract.md](../v1-contract.md) 最後一節「Verify 用的完整流程」在 master 上的最終確認——三個 lane 合併 + 這次全綠，這一輪 v1 MVP dispatch 正式結束。
