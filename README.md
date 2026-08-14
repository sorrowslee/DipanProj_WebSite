# LAMPBLACK 官方網站

《燃燈劫》/ **LAMPBLACK: Rebirth of Ruin** 的官方宣傳網站。

- 正式網址：**https://thelampblack.com**（2026-08-14 上線）
- 主機：Cloudflare **Worker（靜態資源模式）**，專案名 `dipanproj-website`
- 臨時網址：`dipanproj-website.kazusa1000.workers.dev`
- 網域：Cloudflare Registrar

> 🧯 **遇到怪問題、或做任何 Cloudflare 設定之前，先讀 [PROBLEMS.md](PROBLEMS.md)。**
> 之後每踩到一個新坑，也請在那裡加一則（症狀 → 原因 → 解法）。

---

## 資料夾結構

```
DipanProj_WebSite/
├── public/              ← ★ 只有這個資料夾會被發布上網
│   ├── index.html       ← 網站本體（HTML/CSS/JS 全寫在裡面，單一檔案）
│   ├── assets/          ← 壓縮過的圖（WebP）
│   ├── video/
│   │   └── teaser.mp4   ← 預告片（已加 faststart）
│   ├── _headers         ← Cloudflare Pages 的 HTTP 標頭設定
│   ├── robots.txt
│   ├── sitemap.xml
│   ├── favicon.ico
│   ├── apple-touch-icon.png
│   └── icon-512.png
│
├── 遊戲內資源/            ← 原始素材（不會上網，只是留著當來源）
│   ├── 截圖/
│   └── 影片/
│
├── tools/
│   └── build_assets.py  ← 把 遊戲內資源/截圖/ 壓成 public/assets/
│
├── .gitignore
└── README.md
```

**最重要的一條規則：要出現在網路上的東西，一律放 `public/`。**
其他資料夾（原始素材、腳本、這份 README）只存在你的電腦和 GitHub 上，不會被發布。

---

## 本地預覽

**要從 `public/` 目錄啟動伺服器**，不然路徑會對不上：

```bash
cd ~/Documents/workspaces/myProject/DipanProj_WebSite/public
python3 -m http.server 8000
```

然後開 http://localhost:8000

停止：`Ctrl + C`。改完檔案重新整理即可，沒有建置步驟。

> 不要直接按兩下開 `index.html`。`file://` 模式下影片播放、favicon、localStorage 都會出問題。

---

## 更新截圖

1. 新截圖丟進 `遊戲內資源/截圖/`
2. 打開 `tools/build_assets.py`，在 `SHOT_MAP` 加一行：`"檔名片段": "shot_名字"`
3. 跑腳本：

```bash
python3 tools/build_assets.py
```

4. 到 `public/index.html` 的 `<div class="grid">` 區塊加一行：

```html
<figure><img src="assets/shot_名字.webp" alt="" loading="lazy"></figure>
```

腳本會自動壓成 WebP、裁掉截圖邊緣的黑色信箱框。需要 Pillow：`pip3 install Pillow`

---

## 換預告片

新影片放進 `遊戲內資源/影片/`，然後：

```bash
ffmpeg -i "遊戲內資源/影片/新影片.mp4" -c copy -movflags +faststart public/video/teaser.mp4
```

`-movflags +faststart` 會把索引資訊搬到檔頭，讓瀏覽器不用等整個檔下載完就能開始播，**不加的話點播放會先卡住好幾秒**。`-c copy` 是直接複製串流不重新編碼，所以無損也很快。

換封面圖：

```bash
ffmpeg -ss 10 -i public/video/teaser.mp4 -frames:v 1 /tmp/poster.png
# 再轉成 public/assets/teaser_poster.webp
```

⚠️ Cloudflare Pages **單一檔案上限 25MB**，影片超過要先壓縮，或改用 YouTube 嵌入。

---

## 部署

**改檔案 → commit → push 到 `main`，Cloudflare 會自動重新部署**，約一分鐘生效。
不用進後台，不用手動打包。

```bash
git add .
git commit -m "調整某某"
git push
```

### 目前的線上設定（建立時填過一次，平常不用動）

| 項目 | 值 |
|---|---|
| GitHub repo | `sorrowslee/DipanProj_WebSite` |
| Production branch | `main` |
| Build command | （留空） |
| Deploy command | `npx wrangler deploy` |
| Root directory | `/` |
| 發布資料夾 | `public` |

⚠️ **「發布 `public/`」這個設定只存在 Cloudflare 後台，沒有寫進 repo**（詳見 PROBLEMS.md W3）。
如果哪天要重建專案，記得重設，否則會把整個 repo 含原始素材一起發布出去。

### 自訂網域

在 Worker 頁面**上方的 Domains 分頁**（不是 Settings）→ `Add Domain`。

- `thelampblack.com` — 綁定 Worker（DNS 記錄型別顯示為 `Worker`）
- `www.thelampblack.com` — CNAME（Proxied）＋ Redirect Rule 做 301 轉址到根網域
  （**兩步都要做，只加 DNS 會 522**，詳見 PROBLEMS.md W2）

---

## 網域的 email 防偽造設定

這個網域**不寄信**，所以加了三筆 TXT 記錄防止有人偽造 `@thelampblack.com` 的寄件地址：

| Name | Type | Content | 作用 |
|---|---|---|---|
| `@` | TXT | `v=spf1 -all` | 宣告沒有任何伺服器有資格用這個網域寄信 |
| `_dmarc` | TXT | `v=DMARC1; p=reject; sp=reject;` | 要求收信方直接拒收驗證失敗的信 |
| `*._domainkey` | TXT | `v=DKIM1; p=` | 宣告所有 DKIM 金鑰無效，堵住繞過手法 |

**刻意沒有加 Null MX**（`MX` 指向 `.`）。那筆會讓網域完全無法收信，
但之後 Steam 上架要填聯絡信箱、媒體和玩家也要能寄信給你，加了會很麻煩。
上面三筆只擋「偽造寄信」，完全不影響「收信」。

### 之後想要 contact@thelampblack.com 的話

用 **Cloudflare Email Routing**（免費），可以把信自動轉到 Gmail，
不用另外開信箱。設定時它會自動處理 MX 和 SPF。

⚠️ 如果之後改成**真的要用這個網域寄信**（不只是轉信），
記得回頭把第一筆 SPF 的 `-all` 改掉，否則你自己寄的信會被當成偽造退回。

---

## 待辦

- [ ] Steam 願望清單連結（`public/index.html` 搜尋「加入願望清單」，目前是 `href="#"`）
- [ ] 開發日誌連結（同上）
- [ ] 英文標題 logo 重製（遊戲內 `TitlePanel_EN.png` 仍寫著舊名 Burning Lamp）
- [ ] 之後若要自架字體，把 Google Fonts 換成本地檔案（現在依賴外部 CDN）
- [ ] 驗證 `_headers` 在 Workers 靜態資源模式下是否真的生效
- [ ] 補一份 wrangler 設定檔，把「發布 `public/`」寫進版控

---

## 給接手的人／AI

- 動 Cloudflare 設定前先讀 [PROBLEMS.md](PROBLEMS.md)，裡面是實際踩過的坑
- 網站是**單一 HTML 檔**，CSS 和 JS 都內嵌在 `public/index.html` 裡，沒有框架、沒有建置流程
- 雙語靠 HTML 屬性 `data-zh` / `data-en` ＋ 底部一小段 JS 切換，加新文字時**兩個屬性都要寫**
- 改完務必用本機伺服器實測（見上面「本地預覽」），不要只看編輯器
