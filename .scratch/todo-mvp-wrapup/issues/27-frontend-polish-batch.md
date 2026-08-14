Type: task
Mode: execution
Lane: frontend
Status: open

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

（未填）
