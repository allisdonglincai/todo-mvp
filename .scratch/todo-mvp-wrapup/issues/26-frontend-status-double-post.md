Type: task
Mode: execution
Lane: frontend
Status: open

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

（未填）
