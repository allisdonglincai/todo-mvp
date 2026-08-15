# V4 Return — Container 容器架構（泡泡 × wordmark 響應式議題收斂）

> 本檔為 container 討論 session 的 return，交 main/coordinator 對抗式審核後開 ticket。
> 對接文件：`v4-container-dispatch.md`。本 session 未改任何 repo 檔案、未碰 git。
> 驗證 artifact（使用者已確認視覺）：https://claude.ai/code/artifact/8902ea72-871e-47f4-85b8-3d353fbeca1d

## 1. 拍板結果（使用者於 2026-08-15 確認）

**方案 B：inner 錨定** —— header 的 `.bubble-field` 從 `.site-header` 直下移進既有的
`.site-header__inner`，泡泡座標改相對 shell；氛圍外溢用負偏移、由滿版 `.site-header`
的 `overflow:hidden` 在視窗邊緣裁切。**透明度契約收斂為單一值 0.08**（原 design.md
6–10% 區間的中值；0.5 vs 6–10% 缺口就此關閉）。

盤點關鍵事實（收斂依據）：四個區塊中**只有 header 是滿版座標裝飾**。auth-wrap 的第二組
bubble-field 掛在 `.auth-wrap`（已在 `.shell--narrow.page-main` 內）＝**本來就是內容錨定**，
從無壓字問題；main 與 footer 無裝飾層（marquee track 已被 `.shell` 包）。方案 B 是讓
header 收斂到 codebase 既有慣例，不是發明新慣例。

## 2. 最終規格（實作 ticket 的內容）

### 2.1 `templates/base.html`

`.bubble-field` 那個 div（連同三個 span）從 `header.site-header` 直下、移到
`.site-header__inner` 的第一個子元素位置。其餘結構不動；shell 修飾詞沿用 inner 既有的
Jinja 判斷（不新增第三次計算）。

### 2.2 `static/css/app.css`

```css
/* .bubble-field：移除（或不再依賴）自身 overflow:hidden——外溢交給 .site-header 裁；
   position:absolute; inset:0 不變，錨點變成 __inner（shell 內容盒） */
.bubble-field { overflow: visible; }          /* header 那組 */
.bubble-field span { opacity: 0.08; }          /* 契約值，全站單一（含 auth-wrap 那組） */

.bubble-field span:nth-child(1) { width:88px;  height:88px;  left:calc(100% - 16px); top:-22px; }  /* cyan，右外溢 */
.bubble-field span:nth-child(2) { width:46px;  height:46px;  left:46%;               top:10px;  }  /* coral，wordmark 與 nav 間空檔 */
.bubble-field span:nth-child(3) { width:130px; height:130px; left:-104px;            top:38%;   }  /* mint，左外溢 */

.wordmark, .site-nav { position: relative; z-index: var(--z-raised); }
```

注意：`.bubble-field` 是 header 與 auth-wrap 共用 class。實作時確認 auth-wrap 那組的
**座標不動**（其三顆泡泡若目前依賴共用座標規則，需拆成 header 專屬 selector，例如
`.site-header .bubble-field span:nth-child(n)`；transparency 0.08 則兩組共用）。
auth-wrap 那組的 `overflow:hidden` 保留與否由實作者依視覺判斷（外層無滿版裁切容器，
建議保留 hidden 避免溢出頁面）。

### 2.3 `design.md` 契約增補

- 裝飾層規則：「裝飾 bubble-field 一律錨定在該區塊的 shell 寬容器內（`absolute; inset:0`），
  允許負偏移外溢、由滿版外層容器的 overflow 裁切；**禁止以視窗座標（滿版百分比）定位裝飾**。」
- 透明度：0.5 與 6–10% 的缺口記載改寫為「契約值 **0.08**，全站單一」。
- **不新增任何裝飾用斷點**（座標系統一後碰撞在幾何上不存在；原甲案的 56rem 不需出生）。

## 3. 被否決方案與原因

| 方案 | 內容 | 否決原因 |
|---|---|---|
| A（甲改良） | 保留滿版座標＋`(max-width:56rem)` 降透明度、推導公式寫進 design.md | 兩套座標系永久存在；斷點語意是碰撞幾何非內容；每次改 shell 寬/泡泡座標都要重算；與 auth-wrap 慣例持續不一致 |
| 乙原案（site-header__canvas） | header 內加一層與 shell 同寬的新容器 | 方案 B 用既有 `__inner` 達成同一目的，少一個 div，且 shell 修飾詞免傳遞（乙需第三次 Jinja 計算） |
| C（全站 middle-container） | 三層容器慣例套 header/main/footer/auth-wrap | 盤點後受益區塊只有 header（auth-wrap 已符合、main/footer 無裝飾）；為單一使用點蓋全站抽象違反 KISS 與 dispatch §5 邊界 |

乙原案的「寬螢幕兩側素色」代價在 B 中以負偏移外溢緩解（cyan 右溢、mint 左溢，
由滿版 header 裁切），使用者已在 artifact 上確認三種 shell 狀態的視覺。

## 4. Ticket 驗收條件（frontend 可瀏覽器自動化斷言）

環境：`localhost:5000`，orca-ide `eval`（單引號 JS，回傳在 `.result.result`；
snapshot/screenshot/terminal wait 壞，勿用）。

1. **結構**：登入後任一頁，`document.querySelector('.site-header__inner > .bubble-field')`
   非 null，且 `document.querySelector('.site-header > .bubble-field')` 為 null。
2. **透明度契約**：全部 `.bubble-field span` 的 computed `opacity` === `'0.08'`
   （header 與 auth 頁兩組都查）。
3. **無碰撞（核心斷言）**：於視窗寬 320 / 375 / 768 / 893px（登入後）與 320 / 375 / 640px
   （/login），wordmark 的 boundingClientRect 與任一 opacity > 0.1 的泡泡矩形**不相交**。
   （契約值 0.08 ≤ 0.1，此斷言等價於「wordmark 區域內無高於底紋等級的裝飾」；
   若日後契約值調高，斷言改為與全部泡泡不相交。）
4. **零新斷點**：`app.css` 全文無 `56rem` media query、無任何以裝飾為對象的新 media query。
5. **z 軸**：`elementFromPoint`（wordmark 中心）回傳 wordmark 或其子元素，非泡泡。
6. **auth-wrap 不回歸**：/login 的 `.auth-wrap > .bubble-field` 仍存在、座標與現行相同
   （僅 opacity 改 0.08）。
7. **design.md 對帳**：§2.3 三條契約已寫入；「0.5 vs 6–10% 已知缺口」段落移除或改寫為已收斂。

備註：座標草案（§2.2）已在 artifact 於 320–1100px、三種 shell 狀態下驗證無碰撞；
實作時泡泡漂移動畫（±14px/±8px）已被 coral 泡泡與 nav/wordmark 的最小間距吸收
（最窄 320px 時 coral 左緣 ≈147px、wordmark 右緣 ≈110px、登出鈕左緣 ≈248px），
但驗收斷言 3 應在動畫運行中取樣或加測 `prefers-reduced-motion` 靜態態各一次。

## 5. 相關 artifact 與素材

- 收斂案互動驗證（本輪產出，使用者已確認）：https://claude.ai/code/artifact/8902ea72-871e-47f4-85b8-3d353fbeca1d
- 先前裁決頁（透明度滑桿）：https://claude.ai/code/artifact/c7a53e59-4707-4209-98b3-a4e9056310e9
- 先前甲/乙比較：https://claude.ai/code/artifact/3273cab2-0beb-42ea-918f-d428a31756c8

## 6. 未動事項／給 coordinator

- 已定案未翻案：flash 位置 B、字體/cream-palette/marquee、稽核 §3 三項。
- 本 return 不含程式碼變更；實作請開 frontend ticket（現行 issues 編號接續），驗收用 §4。
- 無需 coordinator 裁決的懸置問題；§2.2 的 auth-wrap selector 拆分屬實作細節，由 frontend 判斷。

## 7. Coordinator 審核（對抗式，已通過，含 2 項裁決）

規格可執行（已核對 `__inner` 為 position:relative、overflow 行號 142/200）。裁決如下，ticket 以此為準：

1. **驗收斷言 3 改寫**：0.08 ≤ 0.1 使原斷言為空（永遠無測試對象）。改為對**全部泡泡**做幾何斷言，且用**圓形幾何**（rect 反算圓心/半徑）而非 bounding box——反算 §4 備註數據：mint 在 320px 時 bbox 與 wordmark 相交但圓不相交（誤殺），而 drift 極值（+8,-14）會使圓心距離 wordmark 左下角 ~53px < r65（真碰撞）。§2.2 座標定位為**草案**，frontend 須調整至「含 drift 極值」亦不相交；取樣含動畫中一次 + reduced-motion 靜態一次。
2. **overflow scope 釘死**：改動限定 `.site-header .bubble-field`（overflow:visible + 新座標）；共用 `.bubble-field` 規則只改 opacity 0.08；auth-wrap 組座標與 overflow:hidden 不動；`.site-header` 的 overflow:hidden 保留。
