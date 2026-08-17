Type: task
Mode: execution
Lane: frontend
Status: resolved

出處：shell 寬度響應式討論（artifact https://claude.ai/code/artifact/ec3c0d8b-8e82-4e94-9292-e1fc12fcd6ae ，使用者拍板方案二）+ header 寬度裁決。

## Worktree

沿用 `/mnt/c/Users/1141201/orca/workspaces/allis0813-claude-code-basic/frontend-lane-tags`（分支 `allisdonglincai/frontend-lane-tags`）。開工前 `git fetch origin && git merge --ff-only origin/master` 快轉到最新 master，ff 成功才動工。

## Owned files

`static/css/`、`design.md`。不可改 `templates/`、`app.py`。

## Task（兩項裁決，一項有 code、一項只記文件）

1. **方案二落地**：加一條 media query——`@media (min-width: 80rem) { :root { --shell-wide: 66rem; } }`（放 tokens.css 或 app.css 既有 media query 區，與現有 token 寫法一致即可）。其餘 shell 檔位（26/40rem）與 gutter 全部不動。
2. **header 寬度裁決記進 design.md**：新增一條容器契約——「site-header 內容容器在登入後全站恆定（`--shell` 40rem），**不**跟隨頁面 shell 變體（admin 的 `--shell-wide` 只作用於 page-main）。理由：跨頁導航時 wordmark/nav 不跳位、泡泡錨點穩定；頁內邊緣不對齊由滿版 header 色帶吸收。」同時把方案二的斷點契約寫入（`≥80rem` 時 `--shell-wide: 66rem`，語意：roster 密度型內容的桌機收益；此為 max-width 調整非裝置階梯，其他 shell 檔位禁止仿照加裝置斷點——沿用既有「斷點必須有語意」規則）。**不改任何 header 相關 code**。

## Verification（closed loop）

```
/goal 在自己的 worktree 起 app（docker :5001，方式同前），orca-ide 真瀏覽器 + 同源 iframe 驗證：(1) /admin 於 iframe 寬 1279px 時 roster shell 內容寬 ≈ 58rem 檔（928px−gutter×2 以內）、1280px 與 1536px 時 ≈ 66rem 檔（上限 1056px−gutter×2），跨界差值約 128px；(2) `/`（todo 頁）在 1279/1280/1536px 內容寬完全不變（40rem 檔）；(3) header 的 .site-header__inner 在 / 與 /admin 兩頁、同寬度下 getBoundingClientRect 寬度相等（恆定不隨頁面變體）；(4) design.md 兩條契約已寫入；(5) 全 templates Jinja2 解析 + html.parser 通過（回歸），stop after 3 tries
```

驗收帳號照 demo-brief（admin / admin_password_123）。eval JS 全用單引號；snapshot/screenshot/terminal wait 壞勿用。測完 docker rm -f 清掉。

3 次沒過或連續兩次同因失敗停下回報 main。回報後 main 獨立重驗。`## Answer`/`Status` 寫 master 路徑本檔，`Status: resolved` 由 main 標記。

## Answer

**完成，/goal 第 1 次 try 全過。** 先 ff 快轉 `e81589f → e76156d` 再動工。Commit `f97d7c3`（分支 `allisdonglincai/frontend-lane-tags`），改 `static/css/tokens.css` + `design.md`（+14 行），templates/app.py 未動。

實作兩項：
1. **方案二落地（唯一 code 改動）**：`tokens.css` 末尾加 `@media (min-width: 80rem) { :root { --shell-wide: 66rem; } }`，附一行語意註解。26/40rem 檔位與 gutter 全部不動。
2. **design.md 容器契約**：Anti-patterns 清單新增兩條——「Header 寬度恆定」（site-header 內容容器登入後全站恆定 `--shell` 40rem，不跟隨頁面 shell 變體，admin 的 `--shell-wide` 只作用於 page-main；理由：跨頁導航 wordmark/nav 不跳位、泡泡錨點穩定，邊緣不對齊由滿版 header 色帶吸收）與「斷點必須有語意」（`≥80rem` → `--shell-wide: 66rem` 是 roster 密度的桌機收益、max-width 調整非裝置階梯，其他 shell 檔位禁止仿照）。header code 零改動。

驗證（/goal 五項，皆真實執行；docker :5001 + orca-ide 同源 iframe（`border:0`，media query 以 iframe 視口計），admin / admin_password_123 登入，測畢已清）：
1. `/admin`：iframe 寬 1279px → `.page-main` 內容寬 **928.0px**（58rem 檔）；1280px 與 1536px → **1056.0px**（66rem 檔）；跨界差 **128px** ✅
2. `/`（todo 頁）：1279/1280/1536px 內容寬皆 **640.0px**（40rem 檔）完全不變 ✅
3. header 恆定：`.site-header__inner` 於 `/` 與 `/admin`、全部三個寬度下 getBoundingClientRect 寬度皆 **640.0px** 相等 ✅
4. design.md 兩條契約已寫入（L167「Header 寬度恆定」、L171「斷點必須有語意」）✅
5. 全 templates Jinja2 解析 + html.parser feed 通過 ✅

備註：初測 1280px 未命中 66rem 檔是 iframe 預設 border 吃掉 4px 視口的測量假象（`border:0` 後即命中），非實作問題。


### Main 第二層驗證（獨立重跑）

main 自起 container、自建同源 iframe（border:0）獨立量測六組：/admin 1279→928px、1280/1536→1056px（跨界 +128）；/ 三寬度皆 640px 不變；`.site-header__inner` 六組全 640px 恆定。tokens.css 僅 +7 行 media query、design.md 兩條契約在位（L167/L171）。已 merge + push。
