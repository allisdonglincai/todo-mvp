Type: task
Mode: execution
Lane: frontend
Status: resolved

出處：[v3-design-audit-return.md](../v3-design-audit-return.md) §8.1 第 3 項（有量測）。

## Owned files

`templates/base.html`（狀態鈕動畫/送出 JS 所在）。不可改 `app.py`。

## Task

修「雙擊狀態鈕造成兩次 POST、狀態連跳兩格」：`base.html` 的 `dataset.popped` 守衛讓第二次點擊跳過 320ms 動畫路徑直接原生送出。送出後立即 `disabled` 該按鈕（或等效 debounce），確保一次互動只產生一次 `/status/<id>` POST。KISS：不引入任何依賴。

## Verification（closed loop）

```
/goal orca-ide 真瀏覽器驗證：對同一狀態鈕快速連點兩下（間隔 <320ms），頁面刷新後狀態只前進一格；單擊行為與動畫不回歸，stop after 3 tries
```

## Answer

**完成，/goal 第 1 次 try 全過。** 先 ff 快轉 `3585465 → e43493c` 再動工。Commit `e81589f`（與 ticket 27 同 commit，分支 `allisdonglincai/frontend-lane-tags`），只改 `templates/base.html`，無依賴。

實作（三處小改，全在既有 script 內）：
1. 全域 submit listener 加一條：status form 送出時立即 `disabled` 其 `.status-btn`——原生送出路徑（pending→in_progress、done→pending）的第二次點擊落在 disabled 鈕上，不產生第二次 POST。
2. bubble-pop 路徑（in_progress→done）：`preventDefault` 後隨 `dataset.popped` 一併 `btn.disabled = true`——第二次點擊不會走「守衛跳過→原生直接送出」的舊漏洞，320ms 後 `requestSubmit()` 照常送出（disabled submit 鈕不擋 requestSubmit）。
3. `pageshow` 時重新啟用 disabled 的狀態鈕（bfcache 返回不留死鈕）。

驗證（orca-ide 真瀏覽器，docker :5001，測畢已清）：
- pending 態同鈕連點兩下（同 tick，<320ms）：第一擊後鈕即 disabled=true，刷新後 `status-in_progress`——只前進一格 ✅
- in_progress 態（動畫路徑）連點兩下：disabled=true、`.bubble-pop` 節點僅 1 個、320ms 後正常送出，刷新後 `status-done`——只前進一格、動畫不回歸 ✅
- 單擊回歸：done→pending 正常，刷新後按鈕 disabled=false（可繼續操作）✅
- 全 templates Jinja2 解析 + html.parser feed 通過。


### Main 第二層驗證（獨立重跑）

main 自起 container 瀏覽器實測：pending 態同 tick 連點兩下→鈕即 disabled、刷新後「進行中」只進一格且鈕恢復可用；in_progress 動畫路徑連點→`.bubble-pop` 僅 1 個、落在「已完成」只進一格。已 merge + push（master 見 merge commit）。
