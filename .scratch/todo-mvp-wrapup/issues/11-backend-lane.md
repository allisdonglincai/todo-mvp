Type: task
Mode: execution
Lane: backend

## Owned files

`app.py`、`test_app.py`。不可改 `templates/`、`Dockerfile`、`requirements.txt`；若需要這些檔案改動，用 `orca orchestration ask` 交給 main session 裁決。

## Task

確認 [phase 1 指標](../01-mvp-hardening-scope.md) 第 1 項：`pytest test_app.py` 在目前 `app.py` 上是否全綠（跑一次並回報實際輸出，不要只憑印象回答）。

待命項目：若 [devops lane](10-devops-lane.md) 的 `scripts/verify_deploy.sh` 在第 4 步（跨 container 重啟持久化）失敗，且原因指向 `app.py` 的邏輯（不是 devops 腳本本身的問題），由這個 lane 修 `app.py`，修完重新確認 `pytest test_app.py` 仍全綠，再請 devops lane 重跑驗證腳本。

## Verification（closed loop）

這個 lane 自己開工時用：

```
/goal pytest test_app.py 全部通過（exit 0，沒有 assertion 失敗），stop after 3 tries
```

`/goal` 每次嘗試後由一個獨立的 evaluator model 檢查是否真的通過，不是自己判斷自己做完了。3 次還沒過就停下來，把失敗輸出寫進 Answer，不要無限重試。

回報給 main 之後，main 會**獨立重跑一次 `pytest test_app.py`**，不採信這裡的自我陳述——這是第二層驗證，跟 `/goal` 的 evaluator model 是不同的檢查者。

## Answer

（main session dispatch 後，由 backend lane 回報結果並在此記錄：pytest 實際輸出、是否有介入修 app.py）
