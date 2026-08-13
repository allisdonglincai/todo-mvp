# 開工前每個 session（main / backend / frontend / devops）都要先讀

## Stop Conditions and Cost Ceilings（停止條件與成本上限）

- **Stop condition 是各自 ticket「Verification」章節裡的 `/goal` 指令**，不是「感覺應該做完了」。沒有寫在 ticket 裡的完成標準不算數。
- **Turn ceiling**：`/goal ... stop after N tries` 的 N 是硬上限（backend/frontend 是 3，devops 是 5）。到了就停，把失敗輸出寫回 Answer 並回報 main，不要自己加碼重試。
- **Cost ceiling**：每次 `/goal` 嘗試之間，如果發現連續兩次失敗原因完全一樣（代表在原地打轉、不是在收斂），立刻停下來升級給 main，不要繼續燒 token 硬闖。main 用 `orca-ide terminal wait --timeout-ms` 幫每個 lane 設等待上限（建議 10 分鐘 = 600000），逾時視同該 lane 卡住，回報使用者，不要無限期等。

## 切勿假設「應該沒問題」

- 任何驗證步驟都要**真的執行**、拿到 exit code 或實際輸出，才能寫進 Answer。「這應該可以」「邏輯上沒問題」這類沒有實際跑過的陳述，不能當完成依據。
- 這條對每一層都適用，不只是 worker 自己：
  - **Worker 自己的 `/goal`**：evaluator model 要看真實執行結果，不是 worker 嘴上說已經處理好了
  - **Main 的第二層驗證**（見 `coordinator-protocol.md`）：一定要在 main 自己的 terminal 重新跑一次同一支檢查指令，不能只採信 worker 回報的文字
  - **跨 lane 的假設也一樣**：例如 backend 不能假設「devops 的 container 應該跑得起來」就跳過自己那邊的 `pytest`，每個 lane 只對自己 ticket 裡明列的檢查負責，各自都要真的跑

## 獨立任務 → 各自 worktree；需要互相檢視進度的任務 → coordinator session 內的 subagent

這一輪的 backend / frontend / devops 三個 lane 彼此檔案不重疊、只有零星的跨 lane 需求（走 `orchestration ask`），屬於**獨立任務**，所以各自在自己的 git worktree 裡開獨立 session 工作：

- backend-lane: `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/backend-lane`
- frontend-lane: `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/frontend-lane`
- devops-lane: `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/devops-lane`

每個 lane 的所有檔案操作（讀/改/新增/跑指令）都要在**自己的 worktree 絕對路徑**下進行，commit 到自己的分支（`backend-lane`/`frontend-lane`/`devops-lane`），不要動 master、也不要跑到別的 worktree 目錄裡改東西。main 驗證通過後才會把分支合併回 master（見 `coordinator-protocol.md`）。

如果之後這個 map 出現「需要互相即時檢視進度」的任務（例如两个 lane 要邊做邊對同一個介面達成共識），那種任務改用 main session 內部開 Task subagent 處理，不要開成獨立 worktree session——因為需要頻繁互相看到對方進度時，同一個 session 裡的 subagent 比跨 session 協調便宜也快。

## 狀態檔案只有一份，不要跟著 worktree 分裂

`.scratch/todo-mvp-wrapup/`（map、ticket、這份文件、`coordinator-protocol.md`）的權威版本永遠在 **master 主 checkout**：`/mnt/c/Users/1141201/Documents/allis0813-claude-code-basic/.scratch/todo-mvp-wrapup/`。三個 lane worktree 是從建立當下的 master snapshot 分出來的，裡面那份 `.scratch/` 只會越來越舊。

規則：**程式碼在自己的 worktree 路徑下改，但讀 ticket、寫 `## Answer`、更新 `Status`，一律直接讀寫 master 路徑下的檔案**，不要改自己 worktree 裡那份過期拷貝。這樣狀態只有一個真相來源，不會出現三個 lane 各自回報到不同版本的 ticket 上。
