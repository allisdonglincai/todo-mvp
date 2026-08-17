# Design — Todo (Bubble)

A locked design system for this app. Every page redesign reads this file before
emitting code. Do not regenerate per page — extend or amend this file when the
system needs to grow.

Produced by `hallmark redesign templates/ --mood bubble` on 2026-08-13.
This is a small Flask CRUD app (register / login / todo list / admin), not a
marketing site — every page is an **app page**. The multi-page rule applies:
consistency wins over per-page variety. All four templates share one header,
one footer voice, one token set.

## Genre
playful

## Theme
**Hum** (catalog) — the playful genre's only catalog theme, tuned toward a
"soft, round, alive" **Bubble** register: cream paper, three accents (pear ·
sky-cyan · coral) plus a mint success colour, rounded-sans type, big radii,
soft lifting shadows, one small reacting mark (the bubble beside the
wordmark), a bubble-pop micro-celebration when a todo is completed.

- Paper band: light (cream, `L 97%`)
- Display style: rounded-sans (Plus Jakarta Sans)
- Accent hue: multi (pear `H 95` / cyan `H 235` / coral `H 18` / mint `H 150`)

## Macrostructure family

This app has no marketing pages, so the landing-page macrostructure catalog
doesn't apply directly. Every page uses the same **App Shell** — a
Workbench-adjacent, function-first shape: fixed-voice header, single-column
content well (max 640px, widens to a 2-up card grid only on the admin
roster), no hero, no marketing copy.

- Utility pages (todo list, admin roster): App Shell + card-list body.
- Auth pages (login, register): App Shell + a single off-centre auth card,
  no page nav (user isn't signed in yet).

## Theme
- `--color-paper`      oklch(97% 0.012 95)   cream
- `--color-paper-2`    oklch(94% 0.016 95)   tinted band
- `--color-paper-3`    oklch(91% 0.020 95)   deeper hover
- `--color-ink`        oklch(20% 0.012 250)
- `--color-ink-2`      oklch(40% 0.014 250)  secondary text
- `--color-ink-3`      oklch(50% 0.012 250)  muted / timestamps (5.50:1 on paper)
- `--color-rule`       oklch(88% 0.018 95)   hairlines, decorative only
- `--color-rule-strong` oklch(64% 0.020 95)  form-control + popover borders (3.08:1, WCAG 1.4.11)
- `--color-link`       oklch(50% 0.18 235)   body-text links (4.98:1 on paper)
- `--color-link-hover` oklch(40% 0.16 235)   hover goes *darker*, never lighter
- `--color-accent`     oklch(86% 0.18 95)    pear — primary action
- `--color-accent-2`   oklch(66% 0.18 235)   sky-cyan — links / in-progress
- `--color-accent-3`   oklch(68% 0.24 18)    coral — danger / one pop moment
- `--color-mint`       oklch(80% 0.16 150)   success / done
- `--color-lavender`   oklch(74% 0.16 305)   admin accent (sparing)
- `--color-focus`      oklch(60% 0.18 235)

## Typography
- Display: Plus Jakarta Sans, weight 700, style normal
- Body:    Plus Jakarta Sans, weight 400 (500 for emphasis)
- Mono:    JetBrains Mono, weight 400/500 — timestamps + task-count chip only
- CJK fallback: Noto Sans TC (the UI copy is Traditional Chinese; Plus Jakarta
  Sans has no Han coverage, so Noto Sans TC — a compatible rounded-humanist
  register — carries every CJK glyph)
- Display tracking: -0.02em
- Type scale anchor: 1.25 ratio, 16px body

## Spacing
4-point named scale, values in `tokens.css`. Pages use named tokens
(`var(--space-md)`), never raw values.

## Motion
- Easings: `--ease-out`, `--ease-in`, `--ease-in-out` (state), `--ease-spring`
  (card lift only), `--ease-snap` (button press)
- Reveal pattern: none on page load (a CRUD app doesn't need entrance
  choreography) — motion is reserved for direct-response feedback (button
  press, card hover, status change)
- Character moment: a small pear-yellow bubble beside the wordmark pulses
  gently at rest; when a todo is marked "done" it bursts into three small
  bubbles (mint) from the status button and fades — the app's one moment of
  delight
- Reduced-motion fallback: opacity-only, ≤150ms; the character mark stops
  pulsing; the bubble-pop is skipped entirely

## Microinteractions stance
- Silent success — saving a todo, cycling its status: no toast, the UI
  update *is* the confirmation
- Flash messages (from the Flask backend) render as rounded pills instead of
  a bare list — errors in coral, confirmations in mint. Every `flash()` call
  in `app.py` **must** pass a category (`"error"` / `"success"`); Flask's
  uncategorised default renders neutral grey on purpose, so a miscategorised
  error can never be painted as a success.
- "Silent success" applies to the *inline* state change (a status pill
  cycling, a title saving in place). Actions with no visible result on the
  page — creating or deleting a tag, deleting a row — do flash, because
  otherwise nothing confirms them.
- Hover delay 800ms / focus delay 0ms on anything with a tooltip (none yet)
- Optimistic-feel button press: the primary button's coloured edge shrinks on
  `:active`, like a physical push

## CTA voice
- Primary CTA: `.btn--pear` push style — solid pear fill, a solid colour
  edge (not a blurred shadow) + soft cast shadow, lifts on hover, presses
  down on active
- Secondary CTA: `.btn--soft` — flat tinted fill, no edge
- Destructive / sign-out: `.btn--soft` in neutral ink, never coral (signing
  out isn't destructive)

## Per-page allowances
- All pages: typography + the shared component system (buttons, cards,
  status pills, the bubble mark). No enrichment beyond Tier-A CSS bubble
  shapes (decorative, ≤ 3 per page, low opacity, purely atmospheric).
- Auth pages may show the floating-bubble background treatment behind the
  card; the todo list and admin roster keep it to a single quiet cluster
  behind the header only, so it never competes with task content.

## What pages MUST share
- The wordmark, identical placement. As of the logo drop this is the
  `logo.webp` mark in `static/img/` (`.wordmark-logo`), not the original
  pure-CSS `.bubble-mark`; the CSS breathing pulse retired with it.
- The accent palette and its semantic mapping (pear = primary action, cyan =
  in-progress / links, coral = danger / the one pop moment, mint = done /
  success).
- The button system verbatim (`.btn`, `.btn--pear`, `.btn--soft`,
  `.btn--outline`).
- Card radius (20px), pill radius (999px), input radius (12px).
- The header voice (N7 Brutal-slab, rounded variant) and footer voice
  (Ft8 marquee on utility pages; a quiet single line on auth pages).

## What pages MAY differ on
- Content width (todo list / admin stay at a centred 640–920px well; auth
  pages narrow to a 400px card).
- Footer treatment (full marquee vs. quiet single line) — both share type,
  colour, and the middot separator.
- Admin roster uses the cyan tint for its cards (viewing *other* users' data)
  where the todo list uses plain paper cards (viewing *your own* data).

## Nav + footer archetypes
- Nav: **N7 Brutal slab**, rounded variant per the playful genre's
  "acceptable also (rounded)" allowance — full-width coloured band, bold
  wordmark, no hairline, generous rounded pill actions instead of the sharp
  brutal edge. `N5 Floating pill` is explicitly banned for the playful genre
  (fights the register) and was not used.
- Footer: **Ft8 Marquee scroll** on the todo list + admin roster (a slow,
  reduced-motion-aware repeating line). Auth pages use a quiet one-line
  variant instead of the full marquee, since a sign-in screen shouldn't move.

## Hard floors (added after the v3 tags/menu drop)
These are not style preferences; the v3 features shipped without them and it
cost two P0 bugs.
- **Pointer targets ≥ 44px** on every interactive control, including icon-only
  ones. Use a transparent hit area (`width/height` + negative `margin`) when
  the visual footprint must stay small.
- **Never build a confirm dialog by interpolating user content into a JS
  string literal.** Entity decoding happens before JS parsing, so an
  apostrophe in a todo title silently removes the dialog. Put the message in
  `data-confirm` and read it via `dataset`.
- **Popovers must not live inside a transformed ancestor.** `transform`
  creates a stacking context and will bury the popover behind later siblings.
- **`z-index` comes from the scale** (`--z-base` / `--z-raised` / `--z-sticky`
  / `--z-modal`). No literals.
- **No global `overflow-x: clip`.** It converts "the user can scroll to the
  button" into "the button does not exist". Contain overflow where it is
  produced.
- **Don't declare `role="menu"`** unless the full APG keyboard contract
  (roving focus, arrow keys, Home/End) is implemented. A plain popover of
  `<button>`s with `aria-expanded` is honest and fully accessible.
- **Header 寬度恆定**：site-header 內容容器在登入後全站恆定（`--shell`
  40rem），**不**跟隨頁面 shell 變體（admin 的 `--shell-wide` 只作用於
  page-main）。理由：跨頁導航時 wordmark/nav 不跳位、泡泡錨點穩定；頁內
  邊緣不對齊由滿版 header 色帶吸收。
- **斷點必須有語意**：`≥80rem` 時 `--shell-wide: 66rem`——語意是 roster
  密度型內容的桌機收益，屬 max-width 調整而非裝置階梯；其他 shell 檔位
  （26/40rem）**禁止**仿照加裝置斷點。

## Enrichment
Tier-A pure-CSS floating bubbles — flat circles in the accent hues,
positioned behind the header and (on auth pages) behind the card. No
illustration library, no SVG import, no photography — the app has no product
shots to show.

Decorative-layer contract (v4 container 收斂，2026-08 拍板)：

- **裝飾錨定在 shell 內容盒**：裝飾 `bubble-field` 一律錨定在該區塊的 shell
  寬容器內（`position: absolute; inset: 0`），允許負偏移外溢、由滿版外層容器
  （如 `.site-header`）的 `overflow: hidden` 裁切；**禁止以視窗座標（滿版
  百分比）定位裝飾**。
- **透明度契約值 `0.08`，全站單一**：原「shipped 0.5 vs spec 6–10%」的已知
  缺口已收斂關閉——所有 `.bubble-field span` 統一 `opacity: 0.08`。
- **不新增任何裝飾用斷點**：座標系統一後，泡泡與 wordmark 的碰撞在幾何上不
  存在，無需（也不允許）為裝飾層新增 media query。

## Exports

### tokens.css
See [`static/css/tokens.css`](static/css/tokens.css) — the canonical token
file every template links to. Not duplicated here to avoid drift between two
copies of the same values.
