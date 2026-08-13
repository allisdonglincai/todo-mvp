# V2 Handoff — 補完 Todo CRUD（Update + Delete）

> 寫給**下一個 main/coordinator session**（本 session context 已消耗到要交接）。這份文件本身不是新的權威規則來源——它是「現況 + 這輪要做什麼 + 怎麼做」的交接包，執行細節的權威定義仍然是下面第 0 節列的既有文件。

## 0. 開工前必讀（權威文件，這份 handoff 不重複內容）

- [operating-principles.md](operating-principles.md) — stop conditions/cost ceilings、「切勿假設應該沒問題」、worktree 隔離規則、SOLID/KISS。**整份仍然適用，原封不動照做。**
- [coordinator-protocol.md](coordinator-protocol.md) — dispatch → wait → verify → record → merge 的兩層驗證流程、AFK 邊界。**流程骨架照舊**，這輪的差異見下面第 4、5 節。
- [v1-contract.md](v1-contract.md) — 現有路由/schema/session/驗證規則，v2 是在這之上**新增**，不要動到既有路由行為。
- [map.md](map.md) — 決策歷史。
- [demo-brief.md](demo-brief.md) — v1 已驗證過的 user flow + admin 帳密慣例，這輪 frontend 驗證要沿用同一套帳號/操作慣例。

## 1. 現況（不用重新驗證，已收斂）

- v1 MVP（登入/註冊/admin/三態/loading/雙層驗證）三個 lane 全部 resolved，merge 進 master，`scripts/verify_deploy.sh` 端對端全綠，**已 push 到 `origin/master`**（GitHub `allisdonglincai/todo-mvp`，交接當下 HEAD 是 `d7e4cc0`，`git log`/`git status` 自行核對最新）。
- 之後又追加了兩輪 hotfix + 一次 UI redesign（loading 遮罩點擊卡死修復、`static/` 沒被 Dockerfile COPY 進 image、Bubble 設計系統改版、跑馬燈文案、footer flex 版面），全部都合併並 push 了。
- Demo container `todo-mvp-demo` 目前跑在 `localhost:5000`，環境變數 `ADMIN_USERNAME=admin` / `ADMIN_PASSWORD=admin_password_123`（不是 demo-brief.md 早期版本寫的 `admin1234`，那組密碼已失效）。

## 2. 這輪要做什麼

使用者原話（v2 功能需求）：補足 CRUD 剩餘的 **U**pdate / **D**elete API，以及前端對應的編輯、刪除 todo 功能（Create/Read 在 v1 已經有：新增 todo、列表）。

流程指定：
1. 用 `/to-tickets` 把這個需求拆成對應 issue（照 `issues/10-12` 的既有格式：`Type`/`Mode`/`Lane`/`Status`/`Worktree`/`Owned files`/`Task`/`Verification`(`/goal ... stop after N tries`)/`Answer`）
2. 分派給 **backend**、**frontend** 兩個 session，各自用 `/implement` 執行——**這輪沒有 devops lane**，CRUD 不需要新依賴或部署變動，Dockerfile/requirements.txt 不用碰
3. 兩邊完成後都必須有自己的測試驗證通過
4. **frontend 這輪的驗證不能只做靜態檢查**——必須用 `orca-ide` 的瀏覽器自動化實際跑一次操作（不是 curl，是真的在瀏覽器裡點編輯、點刪除），帳號與 user flow 慣例參考 `demo-brief.md`

## 3. 建議的介面契約（先定調，減少 backend/frontend 來回 `orchestration ask`）

沿用 v1-contract.md 的路由慣例（動詞在前、`POST` 表單，跟現有 `/status/<int:todo_id>` 同一種風格，不要引入真正的 HTTP PUT/DELETE method——原生 HTML form 也送不出那些 method，沒必要為此加 JS 覆寫或前端框架）：

| Method | Path | 需要登入 | 說明 |
|---|---|---|---|
| POST | `/edit/<int:todo_id>` | 是 | 更新該 todo 的 `title`；必須是當前使用者自己的 todo，否則 404。驗證規則沿用既有 `validate_title()`（不要重寫一份）。成功導向 `/` 並 flash 成功訊息；驗證失敗 flash 錯誤訊息、導向 `/`（跟現有 `/add` 失敗處理方式一致，不用另外設計「保留使用者輸入」的機制） |
| POST | `/delete/<int:todo_id>` | 是 | 刪除該 todo；必須是當前使用者自己的，否則 404。成功導向 `/` 並 flash「已刪除」 |

前端 UI 建議（KISS，非強制，frontend lane 可自行判斷更好的做法，但不要引入新依賴/框架）：
- 編輯：todo item 那一列直接放一個 inline 表單，文字輸入框 prefill 現有 `title`，旁邊一個送出鈕打 `/edit/<id>`
- 刪除：一個「刪除」按鈕，打 `/delete/<id>`，用瀏覽器原生 `confirm()` 二次確認（不要做 modal 元件）

這兩點如果 `/to-tickets` 產出的 ticket 內容跟這裡不同，**以 `/to-tickets` 實際產出為準**——這節只是給下一個 coordinator 一個現成的起點，不是必須照抄的規格。

## 4. Lane 設定——跟 v1 的關鍵差異

- **不要重用舊的 `backend-lane`/`frontend-lane` 分支**：這兩個分支停在各自上次 merge 的時間點，master 之後又合併了好幾輪（devops Dockerfile 修復、UI redesign、跑馬燈/footer 修正），這些分支都沒有，直接在上面繼續開發會跟 master 嚴重分岔。從**目前 master HEAD** 開新的 worktree/分支（例如 `backend-lane-crud`/`frontend-lane-crud`），`orca-ide worktree create` 後用 `worktree list --json` 核對實際建立成功（v1 遇過 `runtime_unavailable` 誤報但其實建立成功的狀況）。
- Owned files 不變：backend = `app.py`、`test_app.py`；frontend = `templates/`、`static/`。
- 這輪**沒有 devops ticket**（不改 `Dockerfile`/`requirements.txt`，CRUD 不需要新依賴）——但下面第 5 節的最後一步仍然需要呼叫 devops session，那是「rebuild 部署」的操作性任務，不是「改 devops owned files」的 ticket，兩件事不一樣，不要因為「這輪沒有 devops ticket」就整個跳過 devops session。

### 為什麼合併完不能就結束：container 不會自己感知到 git merge

`todo-mvp-demo` 是一個長期跑著的 container，裡面的程式碼是上次 `docker build` 當下的快照，不會因為 master 多了新 commit 就自動更新。這輪 backend/frontend 兩個 lane 合併進 master 之後，**只要有改到 `app.py`/`templates/`/`static/` 任何一個檔案**，`localhost:5000` 顯示的畫面就會是舊的，直到有人重新 `docker build` + 重啟 container。這件事不能省略，也不是「main 自己 docker build 一下就好」——照 v1 的先例，rebuild/redeploy 屬於 devops 的操作範圍，一律呼叫 devops session 執行（可以是既有的 devops-lane 那個 terminal，只要它還活著、idle 就能重用，不用像 backend/frontend 一樣開新 worktree——**這步驟不改任何檔案，不需要獨立 worktree/分支，只是下指令跑 `docker build`/`docker run`**）。

## 5. Coordinator 執行清單（AFK 迴圈，骨架照 `coordinator-protocol.md`）

1. `/to-tickets` 開兩張 ticket（backend、frontend），存進 `issues/`（編號接續現有的，例如 21/22）
2. 建兩個新 worktree（見上一節），各自開 terminal 啟動 claude session
3. Dispatch：把 ticket 內容 + worktree 絕對路徑 + `/goal` 指令 + 「先讀 operating-principles.md」一起送進 terminal，要求用 `/implement` 執行
4. Claim → Wait → Verify（第二層，不採信自我陳述）→ Record → Merge，同 `coordinator-protocol.md` 的流程
5. **兩個 lane 都合併回 master 後，一定要接著呼叫 devops session 做 rebuild/redeploy**（不能省略、不能自己 docker build 就當作結束）：
   - 送指令給 devops terminal：在 **master 主 checkout** 路徑下（不是 devops worktree，這步要 build 的是三個/兩個 lane 合併後的完整版本，只有 master 有）執行 `docker build -t todo-mvp-demo .` → `docker rm -f todo-mvp-demo` → `docker run -d --name todo-mvp-demo -p 5000:5000 -e SECRET_KEY=... -e ADMIN_USERNAME=admin -e ADMIN_PASSWORD=admin_password_123 todo-mvp-demo` → `curl` 確認 container 有正常回應
   - devops 回報「container 起來了」之後，main 自己再用 `orca-ide` 瀏覽器自動化（`tab create`/`goto`/`eval`，這台機器上 `snapshot`/`screenshot` 會斷線不要用）對 `localhost:5000` 實際跑一次 edit/delete 的完整操作，**確認畫面內容是新版**（例如檢查頁面裡有沒有出現這輪新加的編輯/刪除按鈕，或直接把一筆 todo 編輯/刪除掉確認真的生效），不要只憑 devops 回報的 curl 結果就當作「使用者在瀏覽器看到的東西也更新了」——這正是這次要新增這道步驟的原因：合併「回 git」跟「使用者瀏覽器看到新畫面」是兩件事，中間差一次 rebuild + 重啟

## 6. 這輪踩過的坑（幫下一個 session 省重新踩雷的時間）

- **`orca-ide terminal wait` 在這台機器上壞的**：PowerShell bridge 解析 `--terminal` 參數會直接噴 `PositionalParameterNotFound`，不管 `--for exit` 還是 `--for tui-idle` 都一樣。改用輪詢 `orca-ide terminal show --terminal <handle> --json`，讀 `.result.terminal.title` 的前導符號判斷閒置/忙碌（`✳` = idle，`◑`/`◐`/`✻`/`✢` 等 = busy/thinking），10 分鐘上限，逾時視同該 lane 卡住。
- **`orca-ide snapshot` / `orca-ide screenshot` 也會斷線**（回 `runtime_unavailable`），這兩個指令這輪全程沒能用。改用 `orca-ide eval --page <id> --expression "<JS>"` 直接讀 DOM（文字內容、`classList`、`getBoundingClientRect()` 等），比截圖更精確也更容易斷言，這輪 frontend 的瀏覽器驗證建議直接走這條路。
- **Worker 常會在自評 `/goal` 過關時就直接把 ticket 的 `Status` 設成 `resolved`**，跳過「main 驗證後才標記」的協議（v1 的 backend/frontend 都這樣，devops 反而老實照協議等 main）。不影響最終正確性，但**不能因為看到 `Status: resolved` 就跳過自己的第二層獨立驗證**。
- **純 curl 的驗證測不到 JS/DOM 層的 bug**：v1 的 `scripts/verify_deploy.sh` 全綠過，但使用者實際在瀏覽器點擊時發現 loading 遮罩卡死（click 監聽器沒篩選導頁元素）——這正是這輪要求 frontend 必須用真瀏覽器（而不是只跑靜態檢查）驗證 edit/delete 的原因，edit/delete 這種有表單送出+頁面刷新的互動，最容易藏這類「curl 測得過、瀏覽器點不動」的 bug。
- **三個 lane worktree 裡的 `.scratch/` 是各自 fork 當下的舊快照**：ticket 的讀寫（`## Answer`、`Status`）一律對 **master 路徑**下的檔案操作，不要改 worktree 裡那份過期拷貝。
- Demo container 的 admin 密碼是 `admin_password_123`，不是 demo-brief.md 舊版寫的 `admin1234`（那組密碼在現在的 container 上登不進去）。
