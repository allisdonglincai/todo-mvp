Type: task
Mode: execution
Lane: backend
Status: resolved

## Worktree

沿用 `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/backend-lane-tags`（分支 `allisdonglincai/backend-lane-tags`）。開工前先 `git fetch origin && git merge --ff-only origin/master` 把分支快轉到最新 master（`e7df01f`），確認 ff 成功才動工；非 ff 就停下回報。

## Owned files

`app.py`、`test_app.py`。

## Task

登入成功後的 redirect 邏輯調整：**admin 帳號（`session['is_admin']` 為真）登入成功後導向 `/admin`**；一般帳號行為不變（導向 `/`）。只改 `/login` 成功分支這一處，其他路由（含登入失敗、`login_required` 的未登入導向）都不動。

## Verification（closed loop）

```
/goal pytest test_app.py 全部通過（exit 0），既有測項一個都不能壞，stop after 3 tries
```

新增測項：admin 帳密登入 → 302 Location 是 `/admin`；一般使用者登入 → 302 Location 是 `/`（既有行為回歸）。

環境沿用 `docker run --rm -v "$(pwd)":/app -w /app python:3.12-slim bash -c "pip install --quiet flask pytest && python -m pytest test_app.py -v"`。

結果寫回本檔 `## Answer`（master 路徑），`Status: resolved` 由 main 驗證後標記。

## Answer

完成，commit `854d34d`（分支 `allisdonglincai/backend-lane-tags`，開工前已 ff 到 master `e7df01f` 確認成功）。

**實作**：只改 `/login` 成功分支一行——`return redirect(url_for("admin" if session["is_admin"] else "index"))`。登入失敗分支、`login_required` 未登入導向、其他路由皆未動。

**驗證（真實執行）**：docker pytest → **29 passed, exit 0**（第 1 次嘗試即通過，3 次上限內）。新增 `test_admin_login_redirects_to_admin`（302 Location 以 `/admin` 結尾）與 `test_regular_login_redirects_to_index`（302 Location 以 `/` 結尾，回歸既有行為）；既有 27 測項全過。


### Main 第二層驗證

main 獨立重跑 pytest：**29 passed，EXIT=0**。diff 核對：app.py 僅 /login 成功分支一行，test_app.py +13。已 merge + push（master 見 merge commit）。
