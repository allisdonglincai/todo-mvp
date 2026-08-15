# V4 Dispatch — Container 容器架構討論（泡泡裝飾 × wordmark 響應式議題的上升）

> 寫給**負責 container 架構討論的新 session**（design/discussion session，不是 implement session）。你的任務：理解現有介面的容器設計 → 評估「內容與容器分離」 → 與使用者討論收斂新的容器與斷點設計 → 用該設計回答「泡泡裝飾壓到 wordmark 時的響應式透明度處理」 → 產出 return 文件交回 main/coordinator。**不寫程式碼進 repo、不碰 git、不開 worktree。**

## 0. 開工前必讀

- [operating-principles.md](operating-principles.md)（KISS/SRP、切勿假設應該沒問題）
- `design.md`（repo 根目錄）— Bubble 設計系統權威，含本次相關的「泡泡透明度 0.5 vs 文件 6–10% 已知缺口」記載
- [v3-design-audit-return.md](v3-design-audit-return.md) §8.3-7 — 本議題出處（量測：375/768px 泡泡壓 wordmark）
- 已有的兩份互動 artifact（先看，避免重做）：
  - 裁決頁（透明度滑桿 + 寬度模擬）：https://claude.ai/code/artifact/c7a53e59-4707-4209-98b3-a4e9056310e9
  - 甲/乙方案滿版實作比較（拖視窗看斷點行為）：https://claude.ai/code/artifact/3273cab2-0beb-42ea-918f-d428a31756c8

## 1. 議題背景與現況結論

- 稽核量測：頁首裝飾泡泡（opacity 0.5）在 375/768px 會壓到 wordmark；design.md 記載透明度應為 6–10%，與實作 0.5 有落差（已誠實記為缺口，視覺未動）。
- coordinator 已提出兩案並做成上面第二個 artifact：
  - **甲（響應式透明度）**：`@media (max-width:56rem){ .bubble-field span{opacity:0.08} }`，3 行 CSS、不動結構；治標——泡泡與內容仍是兩套座標系。
  - **乙（canvas 容器分離）**：header 內加一層與 shell 同寬的 `.site-header__canvas`（relative），bubble-field 移入、座標改相對 shell、重調進文字空檔；治本但寬螢幕 header 兩側變素色。
- 使用者判斷：這不只是 header 的局部修補，**應上升為整個專案的 container 設計討論**——先確立內容與容器分離的架構，再用新架構回答泡泡議題。這就是你這個 session 存在的原因。
- 相關已完結事項：稽核 §8.3-8（錯誤訊息位置）已定案 B 並實作（flash 移進表單卡片，`templates/_flash.html` partial，master `f8d99b6`），與本議題無耦合。

## 2. 現有容器設計盤點（截至 master `f8d99b6`）

### 2.1 Shell 系統（`static/css/app.css` + `static/css/tokens.css`）

```
--shell-narrow: 26rem   /* auth 卡片頁 */
--shell:        40rem   /* todo 列表頁 */
--shell-wide:   58rem   /* admin roster */
--page-gutter:  clamp(1rem, 4vw, 1.5rem)

.shell { width:100%; max-width:var(--shell); margin-inline:auto; padding-inline:var(--page-gutter) }
.shell--narrow / .shell--wide 覆寫 max-width
```

**shell 修飾詞由 template 依登入狀態/endpoint 決定**（`base.html`）：未登入 → `shell--narrow`；admin → `shell--wide`；其他 → 預設。頁面主體是 `.shell.page-main`，header 內容是 `.site-header__inner.shell(--narrow)`——同一頁的 header 與 main 用同一種 shell 寬。

### 2.2 頁面骨架（`base.html`）

```
body（flex column, min-height 100dvh）
├─ header.site-header          ← 滿版色帶：paper-2 底 + border-bottom，position:relative，overflow:hidden
│  ├─ .bubble-field            ← absolute inset:0 ＝「滿版」座標系，z-index 1，3 顆泡泡百分比定位
│  └─ .site-header__inner.shell ← 置中 max-width 內容，z-index 10（wordmark + nav/登出）
├─ .shell.page-main            ← 主內容容器（flex:1）
│  └─ main → 各頁 content block
└─ footer.site-footer          ← 滿版：登入前 footer-line、登入後 marquee 跑馬燈（.marquee.shell 包 track）
```

另外 **auth 頁（login/register）自己還有一組 bubble-field**：`content block` 裡的 `.auth-wrap > .bubble-field`（同樣 absolute 滿 auth-wrap）。討論容器架構時別漏掉這組。

### 2.3 問題核心：兩套座標系

泡泡用「滿版寬百分比」（b1 88px @ left 6%、b2 46px @ 84%、b3 130px @ 70%），wordmark 在置中 shell 內，左緣 = `max(gutter, (視窗寬−shell)/2 + gutter)` 隨視窗寬右移。碰撞是兩條線的交叉：

| 版型 | 必壓區間（解不等式） |
|---|---|
| 登入後（shell 40rem） | 視窗 < 約 893px |
| 登入前（narrow 26rem） | 視窗 < 約 640px |

z 軸上泡泡墊在文字後（1 vs 10），實害是 0.5 透明度色塊當背景噪音干擾 wordmark 對比，不是遮擋。

### 2.4 既有斷點盤點（app.css 全部 media query）

- `(hover:hover) and (pointer:fine)` — todo-item hover 位移（P0-B 修正後選單開啟時 transform:none）
- `(max-width: 40rem)` — add-form/edit-form 換行（flex-wrap，稽核 P0-C 修正）
- `(max-width: 30rem)` — todo-title 自成一行（order:-1）
- `(prefers-reduced-motion: reduce)` — 動畫全關
- **目前沒有任何為裝飾層設的斷點**；甲案提議的 56rem（896px）會是第一個

## 3. 「內容與容器分離」的評估框架（給討論定錨，非結論）

逐項評估以下維度，跟使用者對齊價值排序後再收斂：

1. **座標系一致性**：裝飾與內容是否必須共用同一座標系（乙的核心主張）？還是允許裝飾活在滿版層、以斷點管理衝突（甲）？判準：未來還會不會加裝飾元素／改 shell 寬度——每次都要重算碰撞區間的維護成本 vs 一次性結構改動。
2. **滿版氛圍 vs 內容錨定**：Bubble 設計系統的泡泡是「撒滿色帶」的氛圍裝飾（design.md 記載 atmospheric）。錨定到 shell 後寬螢幕兩側變素色——這是視覺身分的取捨，需要使用者拍板，不是技術題。
3. **container 層級的職責切分**：若分離，建議的層級是「外層滿版 container（底色/邊界/overflow）→ 中層 middle container（= shell 寬、置中、relative、裝飾錨點）→ 內層 content」。要討論：middle container 是 header 專用（`site-header__canvas`）還是升級為全站慣例（main、footer marquee、auth-wrap 都套用）？後者影響面大，逐一盤點 2.2 的四個區塊值不值得。
4. **shell 修飾詞的傳遞**：narrow/wide 由 template 狀態決定且 header 與 main 同步。容器分離後修飾詞要上移到 middle container——確認 Jinja 的傳遞點不會重複計算（現在 base.html 已經算兩次：header 一次、page-main 一次）。
5. **斷點語意**：56rem 是「碰撞幾何」推出來的值，不是內容斷點。若採乙（座標系統一）則此斷點根本不需要存在；若採甲，斷點值要寫進 design.md 成為契約（含推導方式，shell 或泡泡座標改動時要重算）。
6. **透明度契約收斂**：無論哪案，design.md 的「0.5 vs 6–10%」缺口都要在這輪寫成單一明確契約（固定值、或分斷點值）。使用者曾提過寬螢幕拉到 1.0 的想法，未定案——裁決頁滑桿可以拉給他看。

## 4. 你的任務（依序）

1. **理解**：讀完第 0 節 + 實際看 `templates/base.html`、`static/css/app.css`（93–110 shell、138–195 bubble-field、196–260 header）、`static/css/tokens.css`（84–93 z/shell tokens），開 `localhost:5000` 縮放視窗實際看壓字情境。
2. **提案**：以第 3 節框架產出 2–3 個 container 架構方案（至少涵蓋「甲改良」與「乙全站化 vs 乙僅 header」的光譜），每案含：層級圖、shell 修飾詞傳遞方式、泡泡座標策略、斷點清單（或說明為何不需要）、design.md 契約寫法、與 2.2 四區塊（header/main/footer/auth-wrap）的關係、取捨聲明。
3. **討論收斂**：與使用者來回，拍板一案。
4. **Artifact 驗證**：把收斂案做成可拖視窗的互動 artifact（參考既有兩份的做法：滿版實作 + 即時寬度徽章），使用者確認視覺效果。
5. **Return 文件**：寫 `.scratch/todo-mvp-wrapup/v4-container-return.md`——最終容器架構規格、斷點與透明度契約、被否決方案與原因、給 coordinator 的 ticket 驗收條件（frontend 可瀏覽器自動化驗證的具體斷言，如「895px 時 wordmark 區域內無 opacity>0.1 的泡泡」）。交回 main/coordinator 對抗式審核後開 ticket。

## 5. 邊界

- 只設計與討論：不改 repo 檔案（return 文件與筆記除外，一律寫在 master 主 checkout 的 `.scratch/todo-mvp-wrapup/`）、不 commit、不 push、不開 worktree。
- KISS：不為「未來可能的裝飾」預蓋抽象；全站化 middle container 只有在盤點確認多個區塊真的受益時才提。
- 已定案勿翻案：flash 位置（B，已實作）、字體/cream-palette/marquee（品牌決策）、稽核 §3 三項。
- 卡住或要動到 v1-contract 既有行為，停下標明問題交 coordinator 裁決。

## 6. 環境備忘（沿用本 repo 慣例）

- demo container `todo-mvp-demo` 在 `localhost:5000`，admin 帳密 `admin` / `admin_password_123`。
- 瀏覽器自動化用 orca-ide `tab create`/`goto`/`eval`（`snapshot`/`screenshot`/`terminal wait` 在這台機器壞的，不要用）；eval JS 全用單引號，回傳值在 `.result.result`。
- Artifact 發布後把連結寫進 return 文件。
