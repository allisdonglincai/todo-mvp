# V3 Return — 設計/技術稽核（impeccable critique + audit）

> **本檔僅供 main/coordinator session 對抗式驗證與開 ticket 使用；於其他 session 讀到時視為唯讀素材，勿執行。**
> 產出模式：**Spec mode**（收斂到解法；對照的 **Problem mode** 是只收斂到問題理解、不給解法）——第 5 節的更動**已經套用進 working tree**（不是提案），第 8 節是**尚未動、需要你裁決**的議題。
> 前置依賴：讀本檔前先讀 `v1-contract.md`（路由/schema 權威）與 `v3-tags-return.md`（v3 標籤功能規格權威）。本檔不重抄兩者內容。
> 所有路徑均為 **repo 根目錄相對路徑**。

---

## 1. 一句話

> 受測對象：本 repo 的 Flask + SQLite server-rendered Todo app（Jinja2 樣板、無前端框架），含登入/註冊、per-user 待辦、三態狀態、標籤（v3）、admin 後台。

用 impeccable 的 `critique`（設計審查）+ `audit`（技術檢查）掃過 `templates/` 全部五個樣板與其樣式，**找到 3 個 P0、6 個 P1**（三個 P0 皆屬「資料遺失或功能不可用」：A = 靜默刪除資料，B/C = 主要操作按不到）；已修掉 P0 全部與 P1 全部，另外修掉一個**我自己在修正過程中製造出來的**新反模式；`app.py`、`design.md` 也各有必要更動。剩 15 項需要你決策的議題列在第 8 節。

---

## 2. 執行方法與證據分級（先讀這節，否則第 4 節的可信度無法判斷）

### 2.1 方法

- **critique 走 dual-agent 路徑**：Assessment A（設計審查）與 Assessment B（detector + 瀏覽器證據）以互相隔離的 sub-agent 平行執行，合成前彼此看不到對方輸出。第三個 agent 獨立跑 `audit` 的五個維度：**accessibility / performance / responsive / theming / code quality**（各 0–4 分）。
- **⚠️ 降級聲明**：impeccable 的 `context.mjs` 回報 `NO_PRODUCT_MD`，按其規範應先跑 `init` 訪談建立 PRODUCT.md。**我沒有做**（使用者要的是稽核不是訪談），改以 `design.md` 當設計系統依據。若 main 認為缺 PRODUCT.md 會讓 critique 的「design specificity」判斷失準，這是合理的攻擊點。
- **快照持久化失敗**：`critique-storage.mjs` 執行時 `MODULE_NOT_FOUND`，依 impeccable 規範「slug 解析失敗則跳過不阻斷」，故**沒有**寫入 `.impeccable/critique/` 快照，也沒有趨勢線。

### 2.2 兩個中途修正的方法學問題（影響前後結論一致性，main 需知道）

1. **Jinja2 autoescape**：最初的離線 render fixture **沒有開 autoescape**，因此**重現不出** P0-A。是稽核 agent 自建 autoescape fixture 才抓到。Flask 的 `render_template` 一律 autoescape，所以**開了 autoescape 的 fixture 才是真實行為**。最終驗證全數使用 `select_autoescape(['html'])`。
2. **detector 自我汙染**：把 detector 用 `addScriptTag({path})` 注入時，Playwright 會把其 ~220KB 原始碼當文字塞進 DOM，detector 掃 `documentElement.outerHTML` 就掃到自己的規則說明字串，產生 `gradient-text`、`theater-slop-phrase` 等假陽性。**最終驗證改用 HTTP 載入**（`addScriptTag({url})`），原始碼不進 DOM，該類假陽性歸零。

### 2.3 工具版本變動

稽核期間 impeccable 從 **synced skill**（帳號層級同步、單一 skill 目錄）**中途消失**，後改以 **plugin**（含 skill + agents + scripts 的整包安裝）重新裝為 **v4.0.4**。兩者對本次的實質差別只有一個：plugin 版帶完整 `scripts/detector/`，synced 版消失後那些腳本一併不可用。因此：

- 第 4 節「第一輪」的 detector 結果來自舊版 synced skill。
- 第 6 節「最終」結果來自 v4.0.4，且**已補裝 `htmlparser2` / `css-select` / `css-tree` / `domutils`**——未補裝前 CLI detector 自我聲明為 `DEGRADED ... findings are an undercount, not a clean bill of health`，結果不可用。
- 兩版的 border 規則邏輯我逐行比對過，判定條件相同。

### 2.4 證據分級（第 4 節每條 finding 都標示）

| 標記 | 意義 |
|---|---|
| `[量測]` | 我或 sub-agent 實際執行並讀到數值／瀏覽器行為（可重跑） |
| `[detector]` | impeccable detector 輸出，規則 id 可查 |
| `[Inferred]` | 我的推論，**沒有**直接量測支撐 |

---

## 3. 已定案清單（**請勿重新審議**）

這三項是與使用者當面確認過的決定，不是我的判斷：

1. **保留 Plus Jakarta Sans**。detector 的 `overused-font` 命中屬實，但換字體是品牌識別決策；`design.md` 第 24 / 58 / 59 行把它寫進系統（行號為本次更動**後**的位置），identity-preservation 優先。
2. **只移除 Google Fonts 請求中的 Noto Sans TC**（CJK 家族，體積最大），fallback stack 內既有的 `PingFang TC` / `Microsoft JhengHei` 接手。純效能收益、零識別風險。
3. **`single-font` 判定為假陽性**——JetBrains Mono 確實有渲染（`.marquee__track` / `.footer-line` / `.status-tag` 使用 `--font-mono`）。我在稽核過程中曾一度誤報它為真，後被 detector 證據推翻。**不要再據此改字體。**

處理順序（1 harden → 2 responsive → 3 polish → 4 design.md 對帳）也是使用者核准的，第 5 節依此編排。

---

## 4. 偵測到的問題

### 4.1 P0（會造成資料遺失或功能不可用）

#### P0-A｜標題含單引號 → 刪除**完全沒有確認就執行**

- **位置**：修改前的 `templates/index.html`，todo 刪除表單與 tag 刪除表單各一處 inline handler：
  `onsubmit="if(!confirm('確定要刪除「{{ todo.title }}」嗎？')){...}"`
- **機制**：Jinja autoescape 把 `'` 轉成 `&#39;` 以保護 HTML 屬性，但**瀏覽器先解碼 HTML 實體、才把屬性值交給 JS parser**，於是引號提前關閉字串字面值，handler 編譯失敗。
- `[量測]` 兩個 sub-agent 以不同方法各自重現。實測輸出 verbatim：
  - `typeof form.onsubmit` = `"object"`（非 `"function"`）
  - pageerror：`Failed to read the 'onsubmit' property from 'HTMLElement': missing ) after argument list`
  - `confirm` dialogs shown: `[]`（空陣列）
  - 實際送出：`POST /delete/1`，並導向 `/delete/1`
  - 對照組（標題不含引號）：對話框正常跳出，取消後**無任何 request**
- **嚴重性依據**：`app.py` 的刪除是硬刪、無 undo，`confirm()` 是唯一安全網。「Ken's plan」「Don't forget」這種日常標題即可觸發。反斜線另有一個吞字元的變體。

#### P0-B｜桌機上 ⋯ 選單的「刪除」被下一張卡片蓋住，點不到

- **位置**：`static/css/app.css` 的 `@media (hover:hover) and (pointer:fine) { .todo-item:hover { transform: translateY(-3px) } }` 與 `.menu { position:absolute; z-index:20 }`。
- **機制**：`transform` 建立 stacking context，`.menu` 的 `z-index:20` 被侷限在該 context 內；後面的 `.todo-item`（`position:relative`、`z-index:auto`、DOM 順序在後）於是畫在選單上面。
- `[量測]` verbatim：
  - `elementFromPoint`（刪除項中心）回傳 `LI.todo-item`
  - Playwright 真實點擊 **timeout after 30s**，錯誤：`<li class="todo-item"> intercepts pointer events`
  - **觸控環境正常**（無 hover transform）、**最後一列正常**（後面沒有卡片）——所以手動測試極易漏掉

#### P0-C｜「新增」與「儲存」按鈕在部分寬度被推出畫面且無法捲到

- **位置**：`.add-form` 的 `<select>` 未設 `flex-shrink`；`.edit-form select { flex-shrink: 0 }` 更是明確關閉收縮；`html, body { overflow-x: clip }` 讓使用者連捲都捲不過去。
- `[量測]` 以 29 字標籤名（`app.py` 上限 30）掃描 11 個寬度：

  | 視窗寬 | flex 方向 | 標題輸入框 | 新增鈕 x 範圍 | 可及 |
  |---|---|---|---|---|
  | 320 / 375 | column | 288–343px | 16..359 | 是 |
  | **390 / 414 / 480 / 560** | row | **34px** | **518..590** | **否** |
  | 640 → 1280 | row | 53px | 545..936 | 是 |

  `.edit-form` 同樣失敗於 320/375/414——可開啟編輯但按不到儲存。

### 4.2 P1

| # | 問題 | 證據 |
|---|---|---|
| P1-1 | **所有錯誤訊息被畫成成功樣式** | `[量測]` `app.py` 全部 10 處 `flash()` 均未帶 category，Flask 預設 `"message"`；`app.css` 把 `.flash-message` 與 `.flash-success` 綁在同一條規則 → 「帳號或密碼錯誤」渲染成薄荷綠成功膠囊。`.flash-error`（coral）是永遠碰不到的死 CSS。`design.md` 原文寫「errors in coral」。 |
| P1-2 | 每個動作都摧毀當前標籤篩選 | `[量測]` `app.py` 四處 redirect 不帶 `tag_id`。**未修**，見第 8 節。 |
| P1-3 | 每個 input / select 的 focus indicator 被移除 | `[量測]` `input[type=text]:focus { outline: none }`（specificity 0,2,1）壓過 `:focus-visible`（0,1,0）。僅存的邊框變色 = **2.03:1**（需 3:1，WCAG 2.4.11）。 |
| P1-4 | focus ring 顏色算成綠色 | `[量測]` `outline: 3px solid color-mix(in oklch, var(--btn-edge) 70%, var(--color-focus))`：pear(hue 92) 與 blue(hue 235) 走短路徑插值成 **`oklch(0.684 0.187 134.9)`（綠）**，對紙色 **2.45:1**。`.btn--soft` 的 `--btn-edge: transparent` 使環變成 30% alpha = **1.40:1**。 |
| P1-5 | 觸控目標全面低於系統自訂標準 | `[量測]` `.tag-chip__delete` **18×18px**（且與 chip `gap: 0`）、`.menu-btn` 32×32、`.menu-item` 26px 高；而 `.btn` token 自訂 `min-height: 44px`。 |
| P1-6 | 連結對比不足 | `[量測]` `--color-accent-2-deep` `#0079c6` on `#f7f5ec` = **4.23:1**（需 4.5:1）；hover 變更亮到 **2.67:1**。 |

### 4.3 Detector findings：真 vs 假陽性

`[detector]` + `[量測]` 驗證。**這張表是本次稽核方法學價值最高的部分，假陽性率約六成。**

> **計數口徑（讀第 6 節的「48 → 16」前必看）**：本表的數字**混合了兩次不同的 run**——`gradient-text` / `theater-slop-phrase` / `numbered-section-markers` / `single-font` 來自**舊版 synced skill 且受自我汙染影響**的第一輪，`cramped-padding` 來自 **CLI** detector，其餘來自 **v4.0.4 瀏覽器** detector。三者的母體不同，**本表的數字不可相加**。
> 第 6 節的「48」有明確且單一的來源：**v4.0.4 瀏覽器 detector、HTTP 載入、修正前的第一次完整 run**，其組成為 `all-caps-body` 14 + `text-occlusion` 10 + `gpt-thin-border-wide-shadow` 9 + `cream-palette` 9 + `overused-font` 5 + `monotonous-spacing` 1 = **48**。
> 「16」為同一條件下的最終 run：`cream-palette` 9 + `overused-font` 5 + `text-occlusion` 2 = **16**。

| 規則 | 判定 | 依據 |
|---|---|---|
| `border-accent-on-rounded` ×2 | **真** | `.user-card` 的 `border-top: 3px + border-radius: 20px`。與使用者用 **kill-ai-slop**（github.com/yetone/kill-ai-slop，一份列舉 23 種「AI 生成 UI 特徵」的檢測清單）**Entry 17「Rounded Card, Colored Left Border」**獨立指出的是同一處——該條判的是行為（把 docs 提示框的強調條當成重複列表的通用裝飾）而非幾何方向，故上邊框同樣命中。 |
| `overused-font` | **真** | Plus Jakarta Sans。已定案保留，見第 3 節。 |
| `wide-tracking` | **真** | `.footer-line` / `.marquee__track` 的 letter-spacing 在 CJK 上有實際視覺影響（與 uppercase 不同）。 |
| `cream-palette` | **真** | impeccable SKILL.md 明文把奶油/米色底稱為「the saturated AI default of 2026」，並指 `--paper` 這類命名本身即 tell。屬品牌識別議題，見第 8 節。 |
| `marquee` / `pulsing-dot` | **真** | 但兩者都是 `design.md` 明載的刻意設計（`design.md` 以 `Ft8 Marquee scroll` 這個頁尾原型代號記載的緩速跑馬燈、以及 loading 三顆泡泡）。 |
| `single-font` | **假陽性** | JetBrains Mono 確實渲染。詳見第 3 節第 3 點。 |
| `gradient-text` ×7 | **假陽性** | detector 自我汙染。`[量測]` 注入前 `/background-clip/gi` → 0 個；注入後 → 9 個，全在 detector 自己的規則表字串裡。改 HTTP 載入後歸零。 |
| `theater-slop-phrase` ×7 | **假陽性** | 同上機制。 |
| `numbered-section-markers` ×3 | **假陽性** | 時間戳 `2026-08-13 09:15:10` 被讀成序列「08, 09, 10」。 |
| `all-caps-body` ×10 | **宣告為真、渲染無效** | `.marquee__track` 確有 `text-transform: uppercase`，但內容全 CJK，`toUpperCase()` 前後相同。當作死 CSS 刪除。 |
| `cramped-padding` ×14 | **假陽性** | `[量測]` computed style：`.tag-manager` = `12px 16px`、`.todo-item` = `16px 24px`。padding 確實存在；CLI 靜態引擎解不開跨檔案的 `var(--space-*)`（token 在 `tokens.css`）。 |
| `text-occlusion` 的多數 | **假陽性** | detector 注入的 overlay 標籤文字被它自己讀到。`[量測]` 注入前含該類字串的 span：**0 個**。 |
| `side-tab` | **從未命中（0）** | 列出僅為對照：這是 detector 判 Left/Right 彩色粗邊框的規則，與 `border-accent-on-rounded`（Top/Bottom + 圓角）是同一段 `checkBorders()` 的兩個分支。本專案是 `border-top`，故走後者。第 6 節把兩者並列確認為 0，是為了證明修正沒有把問題從一個分支推到另一個分支。 |

---

## 5. 已套用的更動與更動邏輯

**六個檔案已寫入 working tree**：`templates/index.html`、`templates/base.html`、`static/css/app.css`、`static/css/tokens.css`、`app.py`、`design.md`。

### Step 1 — harden（對應 P0-A/B/C）

| 更動 | 邏輯 |
|---|---|
| `index.html` 兩處 inline `onsubmit` → `data-confirm` 屬性 + 一個 **capture 階段**的委派 submit listener，用 `form.dataset.confirm` 讀值 | `dataset` 拿到的是**已解碼**的純字串，不再經過 JS parser，引號與反斜線失去逃逸能力。用 capture 是為了先於 `base.html` 的 `showOverlay`（bubble 階段）執行；取消時 `preventDefault()` + `stopPropagation()`，遮罩不會亮起 |
| `.todo-item:has(.menu:not([hidden]))` 給 `z-index: var(--z-raised)`；並在選單開啟 / 編輯中時 `transform: none` | 直接消滅 P0-B 的成因（transform 造出的 stacking context）。同時取消位移可讓選單錨定不跳動 |
| `.menu` 的 `z-index: 20` → `var(--z-raised)` | 該專案有 z-index scale（`--z-base/raised/sticky/modal`），字面值 20 是繞過系統 |
| `.add-form select` / `.edit-form select` 改 `flex: 0 1 auto; min-width: 0; max-width: 12rem`；刪掉 `.edit-form select { flex-shrink: 0 }`；≤40rem 時兩個表單 `flex-wrap: wrap`、input `flex: 1 1 100%` | select 不再以 intrinsic 寬度霸佔空間 |

### Step 2 — responsive

| 更動 | 邏輯 |
|---|---|
| `.tag-chip` 加 `max-width: 100%; overflow: hidden; text-overflow: ellipsis`；`.tag-chip-wrap` 加 `gap` 與 `min-width: 0` | 長標籤不再把 ✕ 推出畫面 |
| `.todo-title` 在 ≤30rem 改 `flex: 1 1 100%; order: -1` | 該列其他子元素全是 `white-space: nowrap`，標題是唯一可壓縮者，320px 下會被壓成一行 1–3 字的直排。改成自成一行 |
| `.tag-add-form input` 由固定 `width: 9rem` 改 `flex: 1 1 9rem; min-width: 0; max-width: 12rem` | 固定 rem 寬會隨 root font-size 放大，200% 字級時撐破版面 |
| **移除 `html, body { overflow-x: clip }`** | 它把「使用者可以捲到按鈕」變成「按鈕不存在」。底層溢出修好後 `[量測]` 7 頁 × 10 寬度（320–1280）強制 `overflow-x: visible` 仍 **0 筆溢出**，證明此 clip 已無必要。移除後未來的版面 bug 會誠實地變成捲軸 |

### Step 3 — polish

| 更動 | 邏輯 |
|---|---|
| `app.py` 10 處 `flash()` 全數補上 `"error"` / `"success"` category；`app.css` 把 `.flash-message` 從 `.flash-success` 拆開，改為中性灰 | 兩層防禦：呼叫端明示分類，且未分類的預設**不可能**再把錯誤畫成成功 |
| 移除 `input[type=text]:focus` / `select:focus` 的 `outline: none`，改只變 border-color | 讓 `:focus-visible` 的 3px outline 生效 |
| `.btn:focus-visible` 的 `color-mix(in oklch, ...)` → `var(--color-focus)` | 消除跨色相插值變綠的問題 |
| **新增 3 個 token**：`--color-rule-strong: oklch(64% 0.020 95)`（3.08:1）、`--color-link: oklch(50% 0.18 235)`（4.98:1）、`--color-link-hover: oklch(40% 0.16 235)` | 數值是以 OKLCH→linear sRGB→WCAG 相對亮度反推出來的最小可行值，不是憑感覺挑的。hover **往深走**而非往亮走 |
| 表單/虛線框的 `1.5px solid|dashed var(--color-rule)` → `var(--color-rule-strong)` | `--color-rule` 對紙色僅 1.32:1，不符 WCAG 1.4.11 的 3:1 非文字對比 |
| `.menu-btn` 32→44px、`.menu-item` 加 `min-height: 2.75rem`、`.tag-chip__delete` 改 44×44 **透明命中區**（`width/height` + 負 `margin`） | 觸控目標達標但視覺尺寸不變 |
| **`.user-card` 的 `border-top: 3px solid var(--color-accent-2)` 移除** | 三方獨立指認：使用者以 kill-ai-slop Entry 17（定義見 4.3 節）、impeccable `border-accent-on-rounded`、設計審查的一致性問題。該色線無語意（不分 admin/一般、不表狀態），且 cyan 在此系統已代表「進行中」，裝飾用途會稀釋語意 |
| `base.html` 的 Google Fonts 移除 `Noto+Sans+TC` | 見第 3 節第 2 點 |

### Step 4 — design.md 對帳

修正 `--color-ink-3` 的數值漂移（文件 56% vs 實作 50%）、補入 3 個新 token、把 flash category 寫成硬性契約、把 `.bubble-mark` 描述改為實際的 `logo.webp` wordmark、**把 bubble 透明度 0.5 vs 文件 6–10% 的落差誠實記為已知缺口（沒有偷改視覺）**，並新增「Hard floors」章節把本次踩到的六個坑寫成規則。

### Step 5 — 修掉我自己製造的反模式（重跑 detector 才發現）

`[detector]` v4.0.4 命中 **`gpt-thin-border-wide-shadow` ×9**，位置 `.menu`。成因：我在 Step 1 為了解決「`.menu` 與 `.todo-item` 邊界對比 1.00:1」而加了 `border: 1px`，但它原本就帶 `--shadow-card-hover`（blur 40px）。規則條件 `visibleThinBorders.length >= 2 && blur >= 16`，說明原文：

> A hairline border paired with a wide, diffuse shadow is a recurring generated-UI signature. Commit to one — a defined edge or a soft elevation — rather than both at once.

**修一個問題製造了另一個。** 依規則建議選一邊：popover 需要明確邊界（原本 paper on paper 是 1.00:1），故留邊框加粗至 1.5px，陰影收成 `0 6px 12px -6px`（blur 12 < 16 門檻）。同時刪除 `.marquee__track` 的死 `text-transform: uppercase`，並把其 letter-spacing 由 0.08em 降到 0.02em 與 `.footer-line` 一致。

### 順帶更動（超出四步驟清單，需你確認是否保留）

- **移除 `role="menu"` / `role="menuitem"`**，改用單純的 `aria-expanded` popover。理由：`[量測]` 原實作沒有實作 APG 鍵盤契約（ArrowDown 無作用、Tab 會走出選單但選單仍開），且 `<form>` 包住「刪除」使其不被 menu 擁有（AX tree 顯示 `menu → generic → menuitem`，違反 ARIA 1.2 required-owned-elements）。宣告 role 卻不履行契約，比不宣告更糟。
- kebab 的 `aria-label` 由統一的「更多動作」改為 `{{ todo.title }} 的更多動作`；`<ul class="todo-list">` 補 `role="list"`（`list-style: none` 會使 Safari/VoiceOver 移除 list 語意）。
- 編輯表單加「取消」鈕、Esc 可關閉、關閉時焦點歸還觸發按鈕；新增 `.is-editing` 狀態隱藏重複顯示的標題/標籤/時間。
- 篩選中的標籤 chip 加 `is-active` 視覺狀態 + `aria-current="true"`（純樣板一行。回應 critique 的 Design Health Score 中 Nielsen 第 1 條 Visibility of System Status 得 **1/4** 的問題——篩選中與未篩選的 chip 當時像素完全相同）。

---

## 6. 驗證結果（量測輸出，可重跑）

```
P0-A  row title      : "Ken's plan — 別忘了 \"quoted\""
P0-A  dialogs shown  : 1 "確定要刪除「Ken's plan — 別忘了 \"quoted\"」嗎？此動作無法復"
P0-A  page errors    : 0
P0-A  navigated away : false
P0-A  VERDICT        : PASS

P0-B  hit test at 刪除 centre: BUTTON.menu-item menu-item--danger | isTheButton: true
P0-B  menu-item height    : 44px (need >=44)
P0-B  real click          : succeeded
P0-B  VERDICT             : PASS
```

- **responsive**：7 頁 × 10 寬度（320/360/375/390/414/480/560/768/1024/1280），移除 `overflow-x: clip` 後 **0 筆水平溢出**。新增鈕在 390px 的 x 由 590（畫面外）變為 183。
- **對比**：連結 4.23 → **4.98:1**；`.menu-item--danger` 5.63:1；`.flash-error` 4.93:1；`.todo-time` 5.50:1；`.marquee__track` 5.03:1。
- **focus / 觸控**：`#title` `#new-tag-name` `#add-tag` `.menu-btn` `.tag-chip__delete` `.btn--pear` 全部 `outline: solid 3px`；`.menu-btn` 與 `.tag-chip__delete` 命中區 44×44。
- **detector（v4.0.4，HTTP 載入）**：總數 **48 → 16**。`side-tab` / `border-accent-on-rounded` / `gradient-text` / `theater-slop-phrase` 皆 **0**。剩下 16 筆為 `cream-palette` ×9、`overused-font` ×5、`text-occlusion` ×2（下拉選單蓋住其下時間戳，即 popover 應有行為）。

---

## 7. 自我點名弱點（**main 的進攻點，請優先打這裡**）

1. **從未啟動過真實 Flask app**。`app.py` 需要 `SECRET_KEY` / `ADMIN_USERNAME` / `ADMIN_PASSWORD` 與 SQLite DB，全程未跑。所有樣板驗證都靠離線 Jinja2 render + Playwright。**`app.py` 的 10 處 flash category 更動只做過 `ast.parse` 語法檢查，沒有執行過。** 建議 main 起 server 實跑一次註冊失敗 / 登入失敗 / 新增 / 刪除，確認 flash 顏色與文案。
2. **`data-confirm` 方案把確認完全押在 JS 上**。若 JS 未載入或報錯，刪除將**毫無確認**直接送出。原本的 inline handler 在同情境下也一樣失效，所以**不是回歸**，但這代表：**這個 app 至今沒有伺服器端的刪除確認，也沒有 undo**。這是產品層級的風險，不是樣式問題。見第 8 節第 8 項。
3. **P0-B 的修法依賴 `:has()`**。僅在 Chromium 驗證過。Safari 15.4+ / Firefox 121+ 支援，但在不支援的瀏覽器上 **bug 會靜默回歸**（沒有 fallback）。若你要保守，應改用 JS 在開啟選單時加 class。
4. **移除 `overflow-x: clip` 的驗證只涵蓋我的 fixture 資料**。極端真實資料（超長不可斷字串、大量標籤同時存在、使用者自訂 200 字標題配長標籤）可能仍溢出。這是我最不放心的一項。
5. **`.tag-chip__delete` 用負 margin 做 44px 命中區**。`[Inferred]` 我**沒有測試相鄰兩個 chip 的命中區是否重疊**——若重疊，點 A 的 ✕ 可能刪到 B。這是可實測的，我沒做。
6. **`.is-editing` 的隱藏規則用直接子選擇器**（`.todo-item.is-editing > .todo-title` 等）。若日後有人在標題外多包一層 wrapper，隱藏會**靜默失效**（畫面出現重複的標題），不會報錯。
7. **對比數值來自我自寫的 OKLCH 轉換器**。稽核 agent 的轉換器曾以 Chromium 實際繪製像素回讀驗證 9/9 完全吻合，我最終驗證用的是另一份實作，數值與其獨立吻合（互證），但**沒有再做一次像素回讀驗證**。
8. **假陽性判定是我的判斷**。`cramped-padding`、`text-occlusion` 我以量測反駁 detector，若 main 不同意應自行重新量測，別直接採信。
9. **`role="menu"` 的移除沒有經過真實螢幕閱讀器測試**。DOM/AX tree 的違規是確認的，但 NVDA/JAWS/VoiceOver 各自如何降級未測（環境無 AT）。移除 role 是我依 ARIA 規範的判斷，不是實測結論。
10. **critique 的 `NO_PRODUCT_MD` 降級**（第 2.1 節）可能讓「design specificity」那部分的判斷失去錨點。

---

## 8. 剩餘待決策議題（**尚未更動**）

### 8.1 需要改動路由行為（超出本次核准範圍）

1. **標籤篩選在每個動作後被丟掉**。`app.py` 四處 redirect（新增 todo / 編輯 / 刪除 / 切換狀態）都不帶 `tag_id`，且 `.add-form` 的標籤下拉永遠預設「無標籤」——在篩選頁新增的待辦連自己都看不到。**`v3-tags-return.md` 第 17 行明文記載「第一版不保留跨操作的篩選狀態——使用者已同意此 KISS 取捨」**，所以這在 v3 是**刻意決定**，不是 bug。要決策的是：v4 是否推翻它。
2. **沒有伺服器端刪除確認，也沒有 undo**（承第 7 節第 2 點）。選項：維持現狀（接受 JS 失效即無保護）／改成兩段式刪除（軟刪 + 復原）／加 `POST` 確認頁。這是產品決策。
3. **雙擊「進行中」造成兩次 POST**。`[量測]` `base.html` 的 `dataset.popped` 守衛讓第二次點擊跳過 320ms 動畫路徑直接原生送出，狀態會連跳兩格。需要 debounce 或送出後 disable。

### 8.2 品牌識別議題（detector 命中屬實，但屬設計決策）

4. **`cream-palette` ×9**。impeccable SKILL.md 明文把奶油/米色底列為 2026 年的 AI 預設值，連 `--paper` 命名都算 tell。但這是 `design.md` 鎖定的品牌底色，與字體同一性質。**要不要動，與第 3 節第 1 點是同一類決定。**
5. **`overused-font` ×5**。已定案保留（第 3 節），此處僅為留檔，勿重新審議。
6. **`marquee` ×7 / `pulsing-dot` ×7**。兩者都是 `design.md` 明載的刻意設計，且 `[量測]` 完整支援 `prefers-reduced-motion`（開啟後 `document.getAnimations()` 回傳 `[]`）。列出僅供知悉。

### 8.3 視覺決定（我刻意沒有動）

7. **裝飾泡泡透明度 0.5 vs `design.md` 記載的 6–10%**。`[量測]` 在 375/768px 會壓到 wordmark。我把落差記進 `design.md` 而**沒有改視覺**——改透明度或改位置都會動到外觀，應由你看過再決定。
8. **錯誤訊息位置**。顏色已修正為 coral，但仍在卡片上方約 120px 處，視覺上與表單脫節。

### 8.4 技術債（有量測、未修）

9. **Logo 是 1024×1024 資產渲染在 33×33 槽位**。`[量測]` `naturalWidth/Height = 1024×1024`，實際 33×33，檔案 23,480 bytes；且 `width="24" height="24"` 屬性與 CSS 算出的 33px 不一致，保留框錯誤。建議出一張 66×66 WebP。
10. **`admin.html` 沒有跟上 v3 標籤功能**。admin 後台看不到任何標籤資訊。屬功能缺口，需確認是否在範圍內。
11. **零 dark mode 準備度**。`[量測]` 兩個 stylesheet 共 **0** 個 `@media (prefers-color-scheme: dark)`，62 個 token 只在 `:root` 定義一次。`tokens.css` 的 `color-scheme: light` 是誠實的 opt-out 而非壞掉的深色主題，但主題切換今天不可能。
12. **跑馬燈接縫差 8px**。`[量測]` track 1688.53px、兩個 span 各 836.27px、`gap: 16px`；`translateX(-50%)` 位移 844.27px 但內容週期 852.27px → 每 30 秒可見跳動一次。
13. **四個無限動畫每幀觸發一次 style recalc**。`[量測]` CDP `Performance.getMetrics` 4 秒：`ΔRecalcStyleCount = 238 over 238 frames`，取消動畫後為 **1**；`ΔLayoutCount = 0`（無 layout thrash），headless 下 0 掉幀。低階手機上是否掉幀未測。
14. **死 CSS**：`.btn--cyan` / `.btn--coral` / `.btn--mint` / `.bubble-mark` 及其 `@keyframes bubble-breathe` 在所有樣板中 0 次使用。coral 變體正好是刪除選單項的合理臉孔，可考慮接上而非刪除。

### 8.5 需要你確認的「順帶更動」

15. **第 5 節「順帶更動」四項超出原核准清單**（移除 `role="menu"`、aria-label 帶標題、編輯表單加取消/Esc、標籤 `is-active` 狀態）。都已套用。若你認為超出範圍應回退，請明示哪幾項。

---

## 9. 結束條件與接手方式

**本份 return 的完成定義**：P0/P1 已修並通過量測驗證、detector 由 48 降至 16 且剩餘皆為已知設計決策、`design.md` 與實作對帳完畢、開放議題完整列出。**已達成。**

**建議 main 的下一步**（依序）：

1. 起真實 Flask server，實跑第 7 節第 1 點列出的四條流程，確認 flash 分類正確。
2. 針對第 7 節第 3/4/5 點各補一次驗證（`:has()` fallback、真實資料溢出、相鄰命中區重疊）。
3. 第 8 節逐項裁決，需要落 ticket 的照本 repo 慣例開在 `issues/`（現有編號至 `25-backend-admin-login-redirect.md`，建議由 26 起）。
4. 裁決結果回寫 `map.md`（本 repo 的 wayfinder map，記錄所有拍板決策的權威檔）的 `Decisions so far` 段落。

**不需要 main 做的**：重跑 detector（v4.0.4 結果已在第 6 節，且環境已補齊 parser 依賴）、重新審議第 3 節三項已定案事項。
