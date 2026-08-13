Type: task
Mode: execution
Lane: backend

## Owned files

`app.py`、`test_app.py`。不可改 `templates/`、`Dockerfile`、`requirements.txt`；若需要這些檔案改動，用 `orca orchestration ask` 交給 main session 裁決。

## Task

確認 [phase 1 指標](../01-mvp-hardening-scope.md) 第 1 項：`pytest test_app.py` 在目前 `app.py` 上是否全綠（跑一次並回報實際輸出，不要只憑印象回答）。

待命項目：若 [devops lane](10-devops-lane.md) 的 `scripts/verify_deploy.sh` 在第 4 步（跨 container 重啟持久化）失敗，且原因指向 `app.py` 的邏輯（不是 devops 腳本本身的問題），由這個 lane 修 `app.py`，修完重新確認 `pytest test_app.py` 仍全綠，再請 devops lane 重跑驗證腳本。

## Answer

（main session dispatch 後，由 backend lane 回報結果並在此記錄：pytest 實際輸出、是否有介入修 app.py）
