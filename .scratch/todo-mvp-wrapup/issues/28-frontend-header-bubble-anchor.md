Type: task
Mode: execution
Lane: frontend
Status: resolved

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

**完成，/goal 第 1 次 try 全過。** 先 `git fetch && git merge --ff-only origin/master` 快轉 `66c2fac → 17fed74`（ff 成功）後動工。Commit `3585465`（分支 `allisdonglincai/frontend-lane-tags`），改動 `templates/base.html` + `static/css/app.css` + `design.md`（+50/−9），app.py 未動。

實作對照 Task：
1. `base.html`：`.bubble-field` 移為 `.site-header__inner` 第一個子元素，其餘結構與 shell 修飾詞 Jinja 判斷不動。
2. `app.css`（依 §7 裁決 2 scope）：新增 `.site-header .bubble-field { overflow: visible }` + header 專屬 `span:nth-child(1..3)` 座標（cyan `calc(100%−16px)/−22px`、coral `46%/10px`、mint 見下）；共用 `.bubble-field span` 只改 `opacity: 0.08`；`.wordmark, .site-nav { position:relative; z-index: var(--z-raised) }`；auth-wrap 組座標/overflow:hidden 不動、`.site-header` overflow:hidden 保留。
3. **座標微調（裁決 1）**：mint 由草案 `-104px` 外移至 **`left:-140px`**（top:38% 不變）。幾何保證：圓心 x = −140+65 = −75，含 drift 極值 +8px 後 −67 < −65(=r)，圓右緣恆在 inner 內容盒左緣外，任何寬度/高度下都不可能與 wordmark 矩形相交；寬螢幕時 mint 完整浮在 shell 左側留白（左外溢氛圍保留），窄螢幕由 `.site-header` overflow:hidden 裁切。cyan/coral 沿用草案（實測餘裕足夠，見下）。
4. `design.md`：Enrichment 段改寫——「0.5 vs 6–10% 已知缺口」段落移除，寫入三條契約（shell 內容盒錨定＋禁止視窗座標定位裝飾、0.08 全站單一值、零新裝飾斷點）。

驗證（§4 七項，皆真實執行；docker :5001 + orca-ide eval，測畢已清）：
1. 結構：`.site-header__inner > .bubble-field` 非 null、`.site-header > .bubble-field` 為 null ✅
2. 透明度：header 3 顆 + /login 兩組共 6 顆 span computed opacity 全 `0.08` ✅
3. 無碰撞（圓形幾何，rect 反算圓心/半徑，圓-矩形最近點距離判定）：登入後 320/375/768/893 + 登出 /login（`shell--narrow` 確認為 true）320/375/640，共 7 寬度 × 動畫運行中取樣一次 + animation:none 靜態取樣一次 = 14 組、每組 3 顆泡泡全部 `d−r ≥ +22px`（最小餘裕 mint 動畫中 +22，cyan 最大 +515）✅（寬度用同源 iframe 指定 width 量 contentDocument，沿用 coordinator 慣例）
4. 零新斷點：app.css 無 `56rem`，media query 僅既有 7 個（40/30/26/24rem、hover、min-40rem、reduced-motion），本輪未新增任何 ✅
5. z 軸：wordmark 中心 `elementFromPoint` 回傳 wordmark 本身 ✅
6. auth-wrap 不回歸：`/login` 的 `.auth-wrap > .bubble-field` 存在、overflow:hidden、三顆座標仍為共用百分比規則（computed 35.5/497/414px = 6%/84%/70%），僅 opacity 改 0.08 ✅
7. design.md 對帳：三條契約已寫入、缺口段落已改寫為已收斂 ✅

另：merge 後全部 templates 重跑 Jinja2 解析 + html.parser feed 通過（含 v3 之後他人改動的 index.html/_flash.html）。


### Main 第二層驗證（獨立重跑，非採信自我陳述）

main 自起 container（:5001）獨立驗證：結構（inner 錨定、header 直下無 bubble-field）、6 顆 span opacity 全 0.08、auth-wrap 組保留 overflow:hidden 與原座標、wordmark 中心 elementFromPoint 命中 wordmark；核心斷言 3 以圓-矩形最近點距離獨立實作，7 寬度（/ 320/375/768/893 + /login 320/375/640）× 動畫中/靜態各一次共 14 組，最小餘裕 +29px 全過；app.css 無 56rem、design.md 三條契約在。diff 只動 base.html/app.css/design.md。已 merge + push（master `e61df0b`）。
