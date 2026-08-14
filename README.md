<br />
<div align="center">
  <h1 align="center">
    <a href="https://github.com/allisdonglincai/todo-mvp"><img src="assets/logo.webp" alt="Todo App" width="64" valign="middle" /></a> Todo App <sup>v1 MVP</sup>
  </h1>
</div>

<p align="center">
  <a href=".scratch/todo-mvp-wrapup/v1-contract.md">路由 / schema 契約</a>
  &middot;
  <a href="#architecture">Architecture</a>
  &middot;
  <a href=".scratch/todo-mvp-wrapup/map.md">Wayfinder Map</a>
</p>

<!-- PROJECT SHIELDS -->
<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white" alt="Flask" /></a>
  <a href="https://www.sqlite.org/"><img src="https://img.shields.io/badge/sqlite3-stdlib%2C%20no%20ORM-003B57?style=flat&logo=sqlite&logoColor=white" alt="SQLite" /></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/docker-single%20Dockerfile-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-yellow?style=flat" alt="License: MIT" /></a>
</p>

---

<img src="assets/cover.png" alt="Todo App v1 MVP — server-rendered 的 Flask + SQLite Todo app，帶登入驗證、per-user 資料隔離、三態狀態循環與 admin 後台，單一 Dockerfile 部署" width="100%">

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#features">Features</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#testing">Testing</a></li>
      </ul>
    </li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

一個刻意保持小巧的 Todo app：註冊、登入、per-user 的待辦清單、三態狀態循環、admin 後台。伺服器端渲染的 Flask + SQLite，單一 Dockerfile 部署，沒有前端框架、沒有 ORM。

這個 repo 真正的目的不是 Todo app 本身，而是拿它當載體，練習「在時間盒內用結構化方式與 agent 協作交付」——用 [wayfinder](.scratch/todo-mvp-wrapup/map.md) 拆解決策、用 4 個獨立的 Claude Code session（1 個 coordinator + backend / frontend / devops 三個 worker）平行開發，細節見 [Architecture](#architecture)。

<!-- FEATURES -->
## Features

<table>
<tr>
<td width="50%" valign="middle">

### 開放註冊

任何人都能自建帳號——帳號 3–30 碼英數字或底線、密碼至少 8 碼，畫面上直接標出規則；送出後後端會再驗一次，不是只靠前端擋。

[路由契約 →](.scratch/todo-mvp-wrapup/v1-contract.md#輸入驗證規則前端-html5-屬性--後端二次驗證都要)

</td>
<td width="50%">
  <img src="assets/register.png" alt="註冊頁，帳號與密碼欄位下方標著格式規則" width="100%" />
</td>
</tr>
<tr>
<td width="50%" valign="middle">

### 登入保護

沒登入進不了 `/`——每個頁面過場都會先擋一次，登入態走 Flask 內建 session，不是裝飾用的假保護。

</td>
<td width="50%">
  <img src="assets/login.png" alt="登入頁，帳號密碼表單" width="100%" />
</td>
</tr>
<tr>
<td width="50%" valign="middle">

### Per-user 三態待辦

新增、查詢都只看得到自己的資料；狀態不是打勾了事，是「未處理 → 進行中 → 已完成」點一下循環一格，三色一眼分辨。

</td>
<td width="50%">
  <img src="assets/todos.png" alt="待辦清單頁，四筆待辦分別是已完成、進行中、待處理三種狀態" width="100%" />
</td>
</tr>
<tr>
<td width="50%" valign="middle">

### Admin 後台

admin 帳號在部署時用環境變數指定，不能自己升級自己；登入後可以看到所有帳號跟各自的待辦，一眼掌握全站狀態。

本地 demo container 的登入資訊：帳號 `admin`／密碼 `admin_password_123`（即 `docker run` 時傳入的 `ADMIN_USERNAME`／`ADMIN_PASSWORD`，僅供本機 demo）。

</td>
<td width="50%">
  <img src="assets/admin.png" alt="Admin 後台，並排顯示 admin 與 demo_user 兩個帳號各自的待辦" width="100%" />
</td>
</tr>
</table>

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* Docker
  ```sh
  docker --version
  ```

### Installation

1. Clone 這個 repo
   ```sh
   git clone <this-repo> && cd allis0813-claude-code-basic
   ```
2. Build image
   ```sh
   docker build -t todo-mvp .
   ```
3. 帶著三個必要的環境變數啟動（缺任何一個 app 會啟動失敗，不會用假值蓋掉忘記設定的問題）
   ```sh
   docker run -d --name todo-mvp \
     -p 5000:5000 \
     -e SECRET_KEY=change-me \
     -e ADMIN_USERNAME=admin \
     -e ADMIN_PASSWORD=change-me-too \
     todo-mvp
   ```
4. 打開 [http://localhost:5000/](http://localhost:5000/)，未登入會直接被導到 `/login`

### Testing

本地跑測試：

```sh
pytest test_app.py
```

端對端驗證（build → 註冊 → 登入 → 新增 → 三態循環 → admin 檢視 → 重啟後資料仍在）：

```sh
bash scripts/verify_deploy.sh
```

完整的路由/schema/驗證規則契約在 [`v1-contract.md`](.scratch/todo-mvp-wrapup/v1-contract.md)。

<!-- ARCHITECTURE -->
## Architecture

**執行期**：Flask 單一 process，server-rendered，session 登入態 + Werkzeug 密碼雜湊 + SQLite，如下圖。

<p align="center">
  <img src="assets/architecture.png" alt="Todo App Architecture 圖：瀏覽器直接請求單一 Flask process，經 Werkzeug 密碼雜湊與 Flask Session 驗證後，由 Jinja2 render_template 產生 HTML，靜態資源為 Bubble design system；資料讀寫 SQLite3；整包包在單一 Dockerfile 的 Docker Container 裡，啟動時注入三個必要環境變數。" width="100%">
</p>

**開發期（Multi-Agent Workflow）**：v1 的登入/驗證/admin/三態範圍用 4 個獨立的 Claude Code session 平行開發，各自在獨立的 git worktree 裡工作、檔案互不重疊，main 獨立驗證通過才合併回 master：

* **`main` / coordinator** — 不改程式碼，只 dispatch、驗證、合併
* **`backend`**（`app.py`, `test_app.py`）— `/goal` + `pytest`
* **`frontend`**（`templates/`, `static/`）— `/goal` + 靜態檢查與瀏覽器操作
* **`devops`**（`Dockerfile`, `requirements.txt`, `scripts/`）— `/goal` + `scripts/verify_deploy.sh`

決策記錄與協作規則都在 [`.scratch/todo-mvp-wrapup/`](.scratch/todo-mvp-wrapup/)（[`map.md`](.scratch/todo-mvp-wrapup/map.md)、[`v1-contract.md`](.scratch/todo-mvp-wrapup/v1-contract.md)、[`coordinator-protocol.md`](.scratch/todo-mvp-wrapup/coordinator-protocol.md)）；UI 走 `hallmark` 產出的鎖定 design system（[`design.md`](design.md)：Bubble 主題）。

<!-- ROADMAP -->
## Roadmap

- [x] Todo CRUD 雛型（新增／查詢／狀態）+ SQLite 持久化
- [x] 登入 / 註冊 / 登出 + per-user 資料隔離
- [x] Admin 後台（帳號清單 + 各帳號 todo）
- [x] 三態狀態、loading 過渡、雙層輸入驗證
- [x] Docker 端對端驗證腳本
- [x] 編輯／刪除 todo（v2 CRUD 補完：`POST /edit/<id>`、`POST /delete/<id>` + inline 編輯表單、`confirm()` 刪除）
- [ ] 期限（due date）、標籤 — 曾經在候選清單上，目前沒有排入範圍
- [ ] 正式 WSGI server（目前仍是 Flask dev server）— 明確決議維持現狀，見 [Ticket 01](.scratch/todo-mvp-wrapup/issues/01-mvp-hardening-scope.md)

<!-- LICENSE -->
## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Getting started with loops](https://www.anthropic.com) / [Loop Engineering](https://addyosmani.com/blog/loop-engineering/) — 這次 4-session AFK dispatch 設計的思維來源
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template) — 這份 README 的架構範本
* [Flask](https://flask.palletsprojects.com/) / [Werkzeug](https://werkzeug.palletsprojects.com/) 文件
* `orca-ide` — 驅動這次 4 個 session 平行協作的 terminal/worktree/orchestration 工具
