Type: task
Mode: execution
Lane: frontend
Status: open

**規格權威來源：[v4-container-return.md](../v4-container-return.md)**（§2 最終規格、§4 驗收、§7 coordinator 裁決——斷言 3 已改寫、overflow scope 已釘死，與 §2/§4 原文不一致處以 §7 為準）。視覺依據 artifact：https://claude.ai/code/artifact/8902ea72-871e-47f4-85b8-3d353fbeca1d

## Worktree

沿用 `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/frontend-lane-tags`（分支 `allisdonglincai/frontend-lane-tags`）。開工前 `git fetch origin && git merge --ff-only origin/master` 快轉到最新 master，ff 成功才動工；非 ff 停下回報。

## Owned files

`templates/base.html`、`static/css/app.css`、`design.md`（§2.3 契約增補）。不可改 `app.py`。

## Task

方案 B（inner 錨定）照 v4-container-return.md §2 實作：

1. `base.html`：header 的 `.bubble-field` 移進 `.site-header__inner` 第一個子元素。
2. `app.css`：`.site-header .bubble-field` 限定 selector 給 overflow:visible + §2.2 草案座標（cyan 右溢、coral 中央空檔、mint 左溢）；共用 `.bubble-field span` 只改 `opacity: 0.08`；`.wordmark`/`.site-nav` 加 relative + z-raised；auth-wrap 組座標/overflow 不動；`.site-header` overflow:hidden 保留。
3. **座標微調（§7 裁決 1）**：§2.2 座標是草案——必須調到「含 bubble-drift 動畫極值（±14px/±8px）」時，任一泡泡的**圓**都不與 wordmark 矩形相交（mint 已知在草案座標的 drift 極值會碰到 logo 左下角，需再外移/下移）。
4. `design.md`：寫入 §2.3 三條契約（禁止視窗座標定位裝飾、0.08 單一值、零新裝飾斷點），並把「0.5 vs 6–10% 已知缺口」段落改寫為已收斂。

## Verification（closed loop）

```
/goal 在自己的 worktree 起 app（docker -p 5001，方式同 ticket 24），orca-ide 真瀏覽器跑 v4-container-return.md §4 全部 7 項——其中斷言 3 依 §7 裁決 1 的圓形幾何版本（全部泡泡、含動畫中 + reduced-motion 靜態各一次取樣，寬度 320/375/768/893 登入後 + 320/375/640 /login），stop after 3 tries
```

窄寬模擬：瀏覽器視窗不可調時，沿用 coordinator 慣例——同源 iframe 指定 width 載入頁面後讀 `contentDocument` 量測。eval JS 全用單引號；snapshot/screenshot/terminal wait 壞，勿用。測完 `docker rm -f` 清掉。

3 次沒過或連續兩次同因失敗停下回報 main。回報後 main 獨立重驗。`## Answer`/`Status` 寫 master 路徑下本檔，`Status: resolved` 由 main 標記。

## Answer

（未填）
