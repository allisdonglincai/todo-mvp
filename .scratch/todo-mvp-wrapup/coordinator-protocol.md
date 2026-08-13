# Main session（coordinator）操作協議

給負責這一輪 dispatch 的 main session 讀。**開工前先讀 `operating-principles.md`**（stop conditions/cost ceilings、「切勿假設應該沒問題」、獨立任務用 worktree、SOLID/KISS）與 `v1-contract.md`（三個 lane 共用的路由/schema/驗證規則契約，main 不用逐一裁決介面細節，照契約就好）。目標：把 [Ticket 10](issues/10-devops-lane.md)、[Ticket 11](issues/11-backend-lane.md)、[Ticket 12](issues/12-frontend-lane.md)（範圍見 [Ticket 20](issues/20-v1-mvp-scope-reopen.md)）分派給三個 worker session 各自在自己的 worktree 裡完成、驗證、收斂，main session 自己不寫 `app.py` / `templates/` / `Dockerfile`。

## Terminal handle 對應（已確認，不用重找）

- backend: `term_47efc46a-2cd3-4244-8e7f-294026a4af88` — worktree `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/backend-lane`（分支 `backend-lane`）
- frontend: `term_ab6d2123-1d07-4dd5-b4a7-b3da663f0c0a` — worktree `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/frontend-lane`（分支 `frontend-lane`）
- devops: `term_14769cdd-745f-4e49-be17-b54635d36fcf` — worktree `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/devops-lane`（分支 `devops-lane`）
- main（就是你自己）: `term_3c510b33-4c33-4664-840c-bebec88dc15f` — 留在 master 的主 checkout

三個 tab 標題已經 rename 成 `✳ backend` / `✳ frontend` / `✳ devops`，`orca-ide terminal list --json` 隨時可以重新核對。三個 worktree 已經用 `orca-ide worktree create --repo id:7ddf919b-0818-4f43-bcc0-ff18b4f0f7a7` 建好，各自是 master 的獨立分支，正常情況下不需要再猜路徑或重建。

## 開工前必查（before you start）

1. 上面的 handle/worktree 對應如果因為使用者重開視窗而失效，才需要重跑 `orca-ide terminal list --json` / `orca-ide worktree list --json` 重新核對
2. dispatch 給每個 lane 時，**要求對方在自己的 worktree 絕對路徑下工作**（見上面對應表），不要讓它在 master 的主 checkout 裡改東西——三個 worktree 是各自獨立的 git checkout，這才是真正的檔案隔離，不是只靠約定
3. `orca-ide worktree create` 偶爾會回報 `runtime_unavailable` 但實際上已經建立成功（本輪就發生過，多建出兩個重複的 frontend worktree，已用 `worktree rm --force` 清掉）——建立 worktree 後一定要 `worktree list --json` 核對實際狀態，不要只看單次呼叫的回傳值判斷成功與否

## Stop condition（goal-based，非人工判斷）

三個 lane ticket 的 `## Answer` 都填好、且 [v1-contract.md](v1-contract.md) 最後一節「Verify 用的完整流程」（devops lane 的 `scripts/verify_deploy.sh`）在 master 分支上實際跑過一遍全部通過，才算這一輪結束。不要因為某個 lane「說」它做完了就採信——見下一節。

devops lane 的驗證依賴 backend lane 的路由存在，所以三個 lane 可以同時 dispatch，但**最後的「全部通過」判斷要等 backend 也收斂**——devops 自己回報的中途結果（只測到建置/啟動）不算數。

## 兩層驗證，不是一層

每個 lane ticket（[10](issues/10-devops-lane.md)/[11](issues/11-backend-lane.md)/[12](issues/12-frontend-lane.md)）的 `## Verification` 都已經寫好各自的 `/goal ... stop after N tries`——dispatch 的時候把那段 `/goal` 指令一起送過去，讓 worker session 自己用一個獨立的 evaluator model 收斂到通過，而不是自己邊做邊自己說「應該可以了」。

但這只是第一層。`/goal` 的 evaluator 看到的只有 worker 給它看的東西，本質上還是同一個 session 內部的自我檢查。第二層是 main（你）在下一節「Verify」步驟裡，**在自己的 terminal 上獨立重跑同一支檢查指令**，拿到的是全新一次執行的 exit code，不是轉述。兩層都過，這個 lane 才算真的收斂。

## Dispatch → wait → verify → record

對每個 lane（devops → backend → frontend，順序不重要，三個可以同時發）：

1. **Claim**：在對應 ticket 檔案加一行 `Status: claimed`
2. **Dispatch**：`orca-ide terminal send --terminal <handle> --text "<ticket內容 + 你的 worktree 絕對路徑 + 該 ticket 的 /goal 指令 + 記得先讀 operating-principles.md>" --enter`
3. **Wait**：`orca-ide terminal wait --terminal <handle> --for tui-idle --timeout-ms 600000`（10 分鐘上限，對應 operating-principles.md 的 cost ceiling）。逾時視同這個 lane 卡住，不要無限等，照下一節「邊界」處理
4. **Verify（maker/checker 分離，第二層）**：worker 回報「`/goal` 通過了」不算數。main session 自己切到該 lane 的 worktree 路徑（或另開一個 verify-only 的 subagent），實際重跑一次該 lane 對應的檢查指令（例如 devops lane 就在 `devops-lane` worktree 下執行 `scripts/verify_deploy.sh`），拿到的是指令的 exit code / 實際輸出，不是 worker 的自我陳述
5. **Record**：驗證通過才把該 ticket 的 `## Answer` 填上實際結果、`Status: resolved`，並把一行 gist 加進 `map.md` 的 Decisions so far；驗證沒過就把失敗原因寫回 ticket，重新 dispatch 或視情況用 `orca-ide orchestration ask` 把問題丟回對應 lane
6. **Merge back**：驗證通過後，回到 master 的主 checkout（`/mnt/c/Users/1141201/Documents/allis0813-claude-code-basic`），`git merge --no-ff <lane>-lane` 把該 lane 的 commit 併回 master。三個 lane 都合併、且 [v1-contract.md](v1-contract.md) 的完整 verify 流程在 master 上重新跑過一次全部通過，這一輪才算真的結束

## 邊界（AFK 期間不能違反）

- main session 自己不改 `app.py` / `templates/` / `Dockerfile` / `requirements.txt`——這些都屬於某個 lane，越界改等於自己身兼球員兼裁判
- 任何跨 lane 的需求（例如 frontend 想要 backend 開新路由）一律經過 main session 裁決，不放行 lane 之間互相直接改對方的檔案
- 三個 lane 都卡住、或驗證連續失敗到你判斷不該再自動重試時，停下來回報使用者，不要無限重試燒 token
