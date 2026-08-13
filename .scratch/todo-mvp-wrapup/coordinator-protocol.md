# Main session（coordinator）操作協議

給負責這一輪 dispatch 的 main session 讀。目標：把 [Ticket 10](issues/10-devops-lane.md)、[Ticket 11](issues/11-backend-lane.md)、[Ticket 12](issues/12-frontend-lane.md) 分派給三個 worker session 各自完成、驗證、收斂，main session 自己不寫 `app.py` / `templates/` / `Dockerfile`。

## 開工前必查（before you start）

1. `orca-ide terminal list --json` 確認要 dispatch 的三個 terminal handle，並用 `orca-ide terminal rename` 標上 lane 名字，避免之後認錯視窗
2. 這個 repo 尚未 `orca repo add` 註冊進 Orca，也沒有建立 orca-managed worktree/branch。目前規劃是靠「檔案切分（見 map Notes 的 Lane 切分規則）」而非 git worktree 隔離三個 lane，因為範圍小、檔案本來就不重疊。如果之後想要真正的 worktree 隔離，要先 `orca-ide repo add --path <this-repo>`，再用 `orca-ide worktree create --agent claude` 幫每個 lane 開獨立 checkout——這是額外的基礎建設，不是這一輪 dispatch 的前提

## Stop condition（goal-based，非人工判斷）

三個 lane ticket 的 `## Answer` 都填好、且 [Ticket 01](issues/01-mvp-hardening-scope.md) 的 4 項 phase 1 指標實際跑過一遍全部通過，才算這一輪結束。不要因為某個 lane「說」它做完了就採信——見下一節。

## Dispatch → wait → verify → record

對每個 lane（devops → backend → frontend，順序不重要，三個可以同時發）：

1. **Claim**：在對應 ticket 檔案加一行 `Status: claimed`
2. **Dispatch**：`orca-ide terminal send --terminal <handle> --text "<ticket 內容 + 檔案路徑>" --enter`，或用 `orca-ide orchestration dispatch`（如果已經有 `run-create` 綁定的 Run）
3. **Wait**：`orca-ide terminal wait --terminal <handle> --for tui-idle`，不要用 sleep 迴圈用猜的
4. **Verify（maker/checker 分離）**：worker 回報「做完了」不算數。main session 自己（或另開一個 verify-only 的 subagent）實際跑一次該 lane 對應的檢查指令（例如 devops lane 就自己執行 `scripts/verify_deploy.sh`），拿到的是指令的 exit code / 實際輸出，不是 worker 的自我陳述
5. **Record**：驗證通過才把該 ticket 的 `## Answer` 填上實際結果、`Status: resolved`，並把一行 gist 加進 `map.md` 的 Decisions so far；驗證沒過就把失敗原因寫回 ticket，重新 dispatch 或視情況用 `orca-ide orchestration ask` 把問題丟回對應 lane

## 邊界（AFK 期間不能違反）

- main session 自己不改 `app.py` / `templates/` / `Dockerfile` / `requirements.txt`——這些都屬於某個 lane，越界改等於自己身兼球員兼裁判
- 任何跨 lane 的需求（例如 frontend 想要 backend 開新路由）一律經過 main session 裁決，不放行 lane 之間互相直接改對方的檔案
- 三個 lane 都卡住、或驗證連續失敗到你判斷不該再自動重試時，停下來回報使用者，不要無限重試燒 token
