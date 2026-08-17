Type: task
Mode: execution
Lane: frontend
Status: resolved

出處：[v3-design-audit-return.md](../v3-design-audit-return.md) §8.4 第 9/12/14 項（皆有量測）。

## Owned files

`templates/`、`static/`、`assets/`（logo 資產）。

## Task（三件小事，一次做完）

1. **Logo 資產**：現況 1024×1024 webp（23KB）渲染在 33×33 槽位，且 `width="24" height="24"` 屬性與 CSS 的 33px 不一致。出一張 66×66 WebP（2x）替換，並把 width/height 屬性改成與實際渲染一致。
2. **跑馬燈接縫**：track 位移週期與內容週期差 8px（`translateX(-50%)` 844.27px vs 內容 852.27px），每 30 秒可見跳動一次。修正位移或 gap 使兩者一致。
3. **死 CSS**：`.btn--cyan` / `.btn--mint` / `.bubble-mark` + `@keyframes bubble-breathe` 全樣板 0 使用，刪除。`.btn--coral` 同為 0 使用，一併刪除（刪除選單項已有 `menu-item--danger` 的 coral 樣式，不需要再接）。

## Verification（closed loop）

```
/goal (1) grep 確認被刪 class 在 templates/ 與 static/ 無殘留引用；(2) 真瀏覽器確認 logo 清晰渲染、無版面位移，跑馬燈循環 60 秒無可見跳動，stop after 3 tries
```

## Answer

**完成，/goal 第 1 次 try 全過。** Commit `e81589f`（與 ticket 26 同 commit，分支 `allisdonglincai/frontend-lane-tags`），改 `templates/base.html` + `static/css/app.css` + `static/img/logo.webp`（net −37 行）。

實作三件：
1. **Logo**：`assets/logo.webp`（1024×1024, 23KB）以 Pillow LANCZOS 出 66×66 WebP（quality 90，1.4KB）覆蓋 `static/img/logo.webp`；`base.html` 的 `width/height` 屬性 `24 → 33`，與 CSS 實際渲染槽位（1.5em of text-lg ≈ 33px）一致。`assets/logo.webp` 原檔保留未動。
2. **跑馬燈接縫**：`@keyframes marquee` 終點由 `translateX(-50%)` 改為 `translateX(calc(-50% - (var(--space-md) / 2)))`——內容週期 = span + 一個 flex gap，−50% 恰少半個 gap（8px），補回後位移與內容週期一致。
3. **死 CSS**：刪 `.btn--cyan`/`.btn--coral`/`.btn--mint`/`.bubble-mark` + `@keyframes bubble-breathe` + reduced-motion 區塊裡的 `.bubble-mark` 規則，共 −52 行。

驗證（皆真實執行；docker :5001 + orca-ide，測畢已清）：
1. grep `btn--cyan|btn--coral|btn--mint|bubble-mark|bubble-breathe` 於 `templates/` + `static/` → 零命中 ✅
2. 瀏覽器：logo `naturalWidth=66×66`、屬性 `33/33`、rendered `33×33`（屬性=渲染 ⇒ 無版面位移）、`complete=true` 清晰載入 ✅
3. 跑馬燈：亞像素量測內容週期 804.65px vs 位移終點 804.65px，mismatch **0.00px**（修正前差 8px）；再以 Web Animations API 把動畫推進到 30s 與 60s 兩個 wrap 邊界前後取樣（等效 60 秒兩次循環），邊界視覺位移 −0.54px/−0.28px = 恰為該取樣間隔的正常移動量，無任何跳動；恢復播放後 running ✅
- 另全 templates Jinja2 解析 + html.parser feed 通過。


### Main 第二層驗證（獨立重跑）

main 驗證：logo.webp 1454 bytes、naturalWidth 66×66、屬性 33/33=渲染 33（無位移）；dead CSS grep templates/+static/ 零命中（app.css −52 行）；marquee 終點 `translateX(calc(-50% - gap/2))` 修正在位。已 merge + push。
