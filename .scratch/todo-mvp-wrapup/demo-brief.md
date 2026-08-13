# Demo Brief — Todo App v1 MVP

> 這份文件邊做 demo 前準備邊更新。「開發進度」區塊每 2 分鐘自動巡一次 4 個 session 補充，其他區塊是靜態的簡報素材。

## 1. 專案架構

**Tech stack**：Python + Flask（server-rendered，前後端同一 process）+ sqlite3（stdlib，無 ORM）。密碼雜湊用 Werkzeug（Flask 本身依賴），登入狀態用 Flask 內建 session，沒有引入任何額外套件或前端框架。

**部署**：單一 Dockerfile，`docker build` + `docker run` 即可跑，帶三個環境變數 `SECRET_KEY`/`ADMIN_USERNAME`/`ADMIN_PASSWORD`。

**v1 MVP 功能範圍**：
- 驗證系統：開放自由註冊、登入、登出，未登入無法使用 Todo 功能
- Per-user Todo：新增、三態狀態（未處理/進行中/已完成，按鈕循環切換）、只看得到自己的項目
- Admin 後台：admin 帳號由環境變數在啟動時 seed，可看所有已註冊帳號與各自的 todo（含建立時間、狀態）
- Cross-cutting：每次頁面過渡都有 loading 遮罩（避免空白閃爍）；每個輸入欄位前端 HTML5 屬性 + 後端二次驗證雙層把關

**這次開發方式（本身也是 demo 的一部分）**：用 4 個獨立的 Claude Code session 平行協作——1 個 main/coordinator + backend/frontend/devops 三個 worker，各自在獨立的 git worktree（`backend-lane`/`frontend-lane`/`devops-lane` 分支）裡改各自負責的檔案（`app.py` / `templates`+`static` / `Dockerfile`+`requirements.txt`），透過 orca-ide 的 terminal 指令收發訊息、`/goal` 自我收斂、main 做第二層獨立驗證後才合併回 master。整個過程记录在 `.scratch/todo-mvp-wrapup/`（map、ticket、v1-contract、coordinator-protocol）。

## 2. Demo User Flow（一般使用者）✅ 目前可以完整走一次

| 步驟 | 操作 | 講稿 |
|---|---|---|
| 1 | 開瀏覽器進入網站首頁 | 「一進來如果還沒登入，系統會直接把你導向登入頁——這個 Todo 工具現在是每個人有自己獨立的帳號和資料，不是誰都能看誰的。」 |
| 2 | 點「註冊」，輸入帳號密碼 | 「註冊是開放式的，帳號 3 到 30 個字、密碼至少 8 碼，這些規則畫面上會直接提示，你打錯格式瀏覽器會先擋一次，送出後後端也會再驗一次——不能只靠前端，不然有心人繞過表單直接打 API 就沒用了。」 |
| 3 | 送出後導向登入頁，用剛註冊的帳密登入 | 「登入之後系統用 session 記住你是誰，接下來看到的 Todo 列表就只會是你自己的。」 |
| 4 | 新增一筆 todo | 「輸入框有長度限制，空白不會被當成有效項目送出。」 |
| 5 | 點狀態按鈕，連續點三次 | 「這是這一版新加的三態狀態——未處理、進行中、已完成，點一下循環到下一個狀態，不是原本簡單的打勾。」 |
| 6 | 點登出 | 「登出之後 session 被清掉。」 |
| 7 | 再次嘗試直接訪問首頁網址 | 「你會發現又被導回登入頁——這證明剛剛的登入保護不是裝飾，是真的擋住未登入的存取。」 |

## 3. Demo User Flow（Admin 後台）✅ 目前可以完整走一次

**登入資訊**：`http://localhost:5000/` → admin 帳號 `admin` / 密碼 `admin_password_123`（demo container 啟動時指定的環境變數，僅限這次 demo 用；container 已重建為乾淨狀態，沒有殘留的測試帳號/todo）

| 步驟 | 操作 | 講稿 |
|---|---|---|
| 1 | 用 admin 帳密登入（部署時透過環境變數指定，不是自助升級） | 「admin 帳號是部署時就決定好的，不是隨便一個使用者能把自己變成 admin，安全性上會比較踏實。」 |
| 2 | 進入 admin 後台頁面 | 「一般使用者登入後看不到這個頁面，只有 admin 帳號能進來。」 |
| 3 | 展示帳號清單 | 「這裡列出所有已註冊的帳號。」 |
| 4 | 展開剛剛示範帳號的 todo 清單 | 「可以看到剛剛示範帳號新增的那筆 todo，狀態也跟前面操作的一致——這代表 admin 看到的是即時、真實的資料，不是另外一份假資料。」 |

## 4. 開發進度（每 2 分鐘自動更新，最新的在最上面）

<!-- monitor-log-start -->
- **T+12**：✅ **實際可以 demo 了，剛才 T+10 的「全綠」有漏洞已補上**。T+10 之後你在瀏覽器實測 `/login`，發現點帳號/密碼 input 就整個卡在全螢幕 loading 遮罩動不了——這個 bug 是 `templates/base.html` 的 `document.addEventListener("click", showOverlay)` 監聽了整個 document 的所有 click，沒篩選是不是真的會導頁的元素，點 input 純 focus 也會觸發顯示；遮罩只在 `pageshow`（實際導頁）才隱藏，沒導頁就卡死。`scripts/verify_deploy.sh` 是純 curl，不執行 JS，所以 T+10 那次全綠完全沒測到這個。已回派 frontend lane 修（commit `e3574a5`：click 監聽改成只在點到 `a[href]`/送出按鈕時才顯示遮罩），main 靜態檢查 + **這次改用真的瀏覽器自動化**（`orca-ide` 的 `tab create`/`goto`/`eval`，不是 curl）把第 2、3 節整個 user flow + admin flow 從頭到尾點過一次：點 input 不再卡遮罩、註冊→登入→新增 todo→連點狀態鈕 3 次回到待處理→登出→未登入訪問首頁被導回登入、admin 登入看得到剛示範帳號與其 todo，全部通過。已合併回 master，`todo-mvp-demo` container 也重建成乾淨狀態（測試帳號/todo 都清掉了）。**admin 密碼改了**，第 3 節登入資訊已更新成 `admin_password_123`（不是 T+10 寫的 `admin1234`，那組密碼在這個 container 上登不進去，demo 前務必看新的）。
- **T+10**：🎉🎉 **全部完成，v1 MVP 已經在 master 上收斂**。main 完成最後一步：在 master 上重新跑一次 `scripts/verify_deploy.sh`（完整流程：register→login→新增 todo→連續切換三態→登出→admin 登入→`/admin` 看到測試帳號與其 todo→`docker restart`→資料仍在），main 自己的 log 顯示「已確認全綠」；我自己也**獨立又重跑了一次 `scripts/verify_deploy.sh`**（不採信 main 的自我陳述，第三層再確認）——`EXIT CODE: 0`，`PASS: full deploy verification flow succeeded`。三個 ticket 都是 `Status: resolved`，map.md 的 Decisions so far 也更新了。你現在瀏覽器開著的 `http://localhost:5000/`（container `todo-mvp-demo`）程式碼跟這次驗證的版本完全一致（devops 只改了 Dockerfile 內容不變的部分和 repo 外的 scripts/，沒動 app.py/templates），**不用重開就能直接開始 demo**，admin 帳密是 `admin` / `admin1234`。上面第 2、3 節的 demo flow 表格已標記「✅ 目前可以完整走一次」。main 的 log 額外提到兩件事：這台機器上 `orca-ide terminal wait` 有 bug（改用輪詢 terminal title 繞過）、以及 backend/frontend 兩個 worker 在自評時就直接把 Status 設 resolved（跳過「main 驗證後才標記」的協議，devops 有照協議走），不影響結果但是個流程小偏差，值得之後修 ticket 範本時處理。監控 loop 到此結束。
- **T+8**：🎉 **三個 lane 全部 resolved 且合併回 master**：frontend（`4f9e3d2`）、backend（`647337b`）、devops（`b5be3f1`，中間還有一版 `6c606d6` 把 verify_deploy.sh 的狀態判斷改成直接查 DB、拿掉 dead-code 錯誤路徑）。devops 剛剛自己醒過來收斂完，不需要人工戳。main 目前**正在積極工作中**（token 持續在跳，不是閒置），正在寫 `map.md` 的 Decisions so far 做最終收尾；todo list 顯示的「Merge all 3 lane branches」「Final full verify on master」兩項介面上還沒打勾，但可能只是畫面還沒刷新（git log 已經看得到三個 merge commit）。**還不算完全確認**——main 自己在 master 上重新跑一次 v1-contract.md 完整驗證流程（`scripts/verify_deploy.sh`）這一步還沒看到結果，等它跑完、明確全綠，才會在這裡標記 demo flow 為可展示。目前你手上能點的是我剛才手動 build 的 `todo-mvp-demo` container（不是走 devops 正式驗證路徑，但功能應該是完整的，因為程式碼已經是三個 lane 合併後的版本）。
- **T+6**：✅ backend 已經合併回 master 了（commit `647337b`，main 獨立重跑 pytest 過了才合併）——抽查 `app.py` 確認 7 個路由都在（`/register`/`/login`/`/logout`/`/`/`/add`/`/status/<id>`/`/admin`），T+4b 那個「master 會 500」的問題已解除。frontend（Ticket 12）也早就合併了。⚠️ **devops（Ticket 10）還是 `claimed`，terminal 畫面跟兩輪前幾乎一樣（同一句「check on backend lane progress」，token 數沒變），看起來也卡住了**——backend 已經收斂，devops 該回去重跑 `scripts/verify_deploy.sh` 了，但沒有動作。main 的 to-do 顯示接下來是「Merge all 3 lane branches」「Final full verify」兩項待辦，卡在等 devops。跟 T+4 主 session 卡住的情況一樣，這輪只讀不寫沒有介入，需要你決定要不要戳一下 devops。
- **T+4b**：⚠️ **重要：master 現在如果重新 build 會 500，先別重 build**。另一個在同資料夾工作的 session 核對後回報並經我抽查確認：frontend-lane（Ticket 12）已合併（commit `4f9e3d2`），但 backend-lane 還沒合併，`app.py` 還停在最原始版本（3 個路由 `/`、`/add`、`/toggle/<id>`，`todos` 表只有 boolean `done`，沒有 `users` 表），跟已合併的 template（要 `/register`/`/login`/`/status/<id>`/`/admin`、`username`/`todo.status`/`todo.created_at` 等變數）對不上——`GET /` 若剛好 todos 表有資料會直接 500（Jinja2 對 `sqlite3.Row` 取不存在的屬性會拋 `IndexError`）。**目前你瀏覽器開著的 `localhost:5000` 是更早、frontend 合併前 build 的 image，不受影響，還能繼續看**；只是先不要重新 `docker build` 現在的 master，等 backend 也合併進來再重 build。已回報 main（正在做 backend 的獨立驗證與 merge），這個問題會隨 backend 合併自動解決。
- **T+4**：⚠️ **main 疑似卡住**——terminal 顯示 todo list 還有「◻ Independently verify backend lane (rerun pytest test_app.py)」「◻ Record Answers, set Status: resolved, update map.md Decisions」兩項待辦，但游標是閒置的空 prompt（不是執行中），跟 T+2 那次讀到的畫面幾乎一樣，代表這兩分鐘內 main **沒有繼續動作**。backend/frontend/devops 三個 worker 都已經是「做完自己的、等別人」的狀態（backend 自評已過、devops 明確寫「no further action until backend lane converges」）。這不是 worker 卡住，是 **main 這個 agentic turn 本身跑完就停了，沒有東西再把它叫醒去做第二層驗證**——這份 monitor 依指示只讀不寫，沒有介入，需要你決定要不要手動戳一下 main（例如切到那個分頁按一下 Enter，或請我送一句「continue」進去）。
- **T+2**：**backend 也完成了**（Ticket 11 Status 變成 resolved，自己回報 `/goal` 收斂），但 main 還沒做第二層獨立驗證、也還沒 merge `backend-lane` 回 master（git log 還沒看到 merge commit）。devops 仍在等 backend、目前正主動去確認 backend 進度（idle 中，看到 devops terminal 顯示「check on backend lane progress」）。frontend 已合併（同 T+0）。main terminal 顯示「1 monitor」，看起來也在盯著什麼。**還不能跑 demo**——backend 的 Answer 是 worker 自我回報，main 還沒重跑驗證確認是真的過，等 main 完成 merge 才算數。
- **T+0**：main 目前 idle（等待 worker 回報）；backend 執行中（7m40s，改 `app.py` schema/路由）；frontend **已完成並合併回 master**（Ticket 12 resolved，commit `4f9e3d2`）；devops 執行中（7m39s，卡在等 backend 的完整流程，先把腳本建置/啟動的部分寫好）。目前**還不能完整跑 demo**——需要等 backend 完成登入/註冊/三態/admin 路由才有東西可以操作。
<!-- monitor-log-end -->
