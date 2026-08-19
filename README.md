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
│   ├── index.html       ← 首頁（HTML/CSS/JS 全寫在裡面，單一檔案）
│   ├── devlog.html      ← 開發日誌頁（由腳本產生，不要手改）
│   ├── assets/          ← 壓縮過的圖（WebP）
│   ├── video/
│   │   ├── teaser.mp4   ← 預告片（已加 faststart）
│   │   └── dev0*.mp4    ← 開發日誌的三段里程碑影片
│   ├── _headers         ← Cloudflare Pages 的 HTTP 標頭設定
│   ├── robots.txt
│   ├── sitemap.xml
│   ├── favicon.ico
│   ├── apple-touch-icon.png
│   └── icon-512.png
│
├── 遊戲內資源/            ← 原始素材（不會上網，只是留著當來源）
│   ├── 截圖/
│   ├── 影片/
│   ├── 血統/              ← 各血統的角色立繪（透明底）
│   ├── 遊戲內圖片/         ← 標題 logo 等遊戲內美術元件
│   └── 開發日誌/
│
├── tools/
│   ├── dev-server.js         ← 本地預覽伺服器（npm run dev）
│   ├── build_assets.py       ← 把 遊戲內資源/截圖/ 壓成 public/assets/
│   ├── build_devlog.py       ← 從主專案 git 紀錄產生 public/devlog.html
│   └── devlog_template.html  ← 開發日誌的版型與里程碑文案
│
├── package.json
│
├── .gitignore
└── README.md
```

**最重要的一條規則：要出現在網路上的東西，一律放 `public/`。**
其他資料夾（原始素材、腳本、這份 README）只存在你的電腦和 GitHub 上，不會被發布。

---

## 本地預覽

```bash
npm run dev
```

**就這樣，不用記網址、不用 `npm install`。** 它會自己：

- 從 `public/` 提供網站
- 找一個沒被佔用的埠（預設 8000，被佔就往上找 8001、8002…）
- 自動用預設瀏覽器打開

停止：`Ctrl + C`。改完檔案重新整理瀏覽器即可，沒有建置步驟。

伺服器是 `tools/dev-server.js`，**零依賴、只用 Node 內建模組**，所以不需要 `node_modules`。
它支援 Range 請求（Safari 才能正常拖曳影片進度條），HTML 一律 `no-store`（改完一定看得到新版）。

> 不要直接按兩下開 `index.html`。`file://` 模式下影片播放、favicon、語言記憶都會出問題。

### 其他指令

```bash
npm run assets   # 重新壓縮 遊戲內資源/截圖/ → public/assets/
npm run devlog   # 從主專案 git 紀錄重新產生 public/devlog.html
```

---

## 更新截圖

1. 新截圖丟進 `遊戲內資源/截圖/`
2. 打開 `tools/build_assets.py`，在 `SHOT_MAP` 加一行：`"檔名片段": "shot_名字"`
3. 跑腳本：

```bash
npm run assets
```

4. 到 `public/index.html` 加對應的區塊：

**武器**（橫向卷軸，`<div class="wrail">` 裡面）：

```html
<article class="wcard"><img src="assets/w_名字.webp" alt="" loading="lazy">
  <div class="wmeta"><h3 data-zh="中文名" data-en="English"></h3>
  <p data-zh="中文一句話" data-en="English one-liner"></p></div></article>
```

**場景**（交錯排版，`<div class="scenes">` 裡面）：
偶數順位要加 `alt` 這個 class 才會左右交錯，編號也要接續。

```html
<div class="scene rv">
  <div class="scene-img"><img src="assets/sc_名字.webp" alt="" loading="lazy"></div>
  <div class="scene-txt">
    <div class="idx">05</div>
    <h3 data-zh="中文名" data-en="English"></h3>
    <p data-zh="中文描述" data-en="English description"></p>
  </div>
</div>
```

腳本會自動壓成 WebP、裁掉截圖邊緣的黑色信箱框。需要 Pillow：`pip3 install Pillow`

---

## 換標題 logo

首頁的中英文標題都是**遊戲內的火焰書法圖**，不是網頁文字。

新的 logo PNG（透明底）丟進 `遊戲內資源/遊戲內圖片/`，
在 `tools/build_assets.py` 的 `LOGO_MAP` 加一行，然後 `npm run assets`。

腳本會裁到實際筆畫邊界（alpha bbox）再等比縮放，所以原始檔的留白多少都沒關係。

⚠️ **中英文兩張的長寬比不一樣**（中文約 2.67、英文約 3.45，因為英文字母多所以更扁）。
用同一個寬度的話英文會矮一截，所以 `index.html` 裡是**分開給寬度**的：

```css
.mark-img.zh{width:min(560px,84vw)}
.mark-img.en{width:min(625px,88vw)}
```

換了 logo 之後如果比例變了，這兩個數字要重算，目標是讓兩者的**視覺高度**一致。

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

## 更新開發日誌

開發日誌頁 `public/devlog.html` 是**自動產生的，不要直接手改**（下次重跑會被覆蓋）。

```bash
npm run devlog
```

它會讀取 `../DipanProj` 的 git 紀錄（唯讀，只跑 `git log --no-optional-locks`，
不會在主專案裡留下任何東西），濾掉純文件與雜項提交，然後套版產生頁面。

要改的地方：

| 想改什麼 | 改哪裡 |
|---|---|
| 頁面版型、色彩 | `tools/devlog_template.html` 的 `<style>` |
| 開頭三段里程碑影片的標題與敘述 | `tools/devlog_template.html` 的 `<article class="mile">` |
| 哪些提交要被濾掉 | `tools/build_devlog.py` 的 `NOISE` / `NOISE_PREFIX` |

⚠️ 腳本預期 **DipanProj 與 DipanProj_WebSite 放在同一層**。搬動資料夾要同步改 `GAME_REPO`。

里程碑影片同樣要壓過（原檔 9–31MB，壓完 0.9–5.7MB）：

```bash
ffmpeg -i 原檔.mp4 -vf scale=1280:-2 -c:v libx264 -crf 26 -preset slow \
  -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart public/video/devXX.mp4
```

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

- [ ] Steam 頁面上線後，把 `public/index.html` 的 `#wishBtn` 從 `<button>` 換回 `<a href="Steam網址">`
      （目前點下去只會浮出「Steam 頁面籌備中」提示）
- [x] ~~英文標題 logo 重製~~
      → 2026-08-19 完成。新的火焰書法 LAMPBLACK 放在
      `遊戲內資源/遊戲內圖片/TitlePanel_Title.png`，`npm run assets` 會壓成
      `public/assets/logo_en.webp`。中英文標題現在都是圖，不再是 CSS 排的字。
- [ ] 之後若要自架字體，把 Google Fonts 換成本地檔案（現在依賴外部 CDN）
- [x] ~~驗證 `_headers` 在 Workers 靜態資源模式下是否真的生效~~
      → 確定生效。2026-08-18 換圖後線上還是舊圖，正是因為裡面的 `max-age=86400`
      真的被套用了（見 PROBLEMS.md W7）。Cloudflare 靜態資源的預設值本來就是
      `max-age=0, must-revalidate`，現在改回等同預設。
- [ ] 補一份 wrangler 設定檔，把「發布 `public/`」寫進版控

---

## 給接手的人／AI

- 動 Cloudflare 設定前先讀 [PROBLEMS.md](PROBLEMS.md)，裡面是實際踩過的坑
- 網站是**單一 HTML 檔**，CSS 和 JS 都內嵌在 `public/index.html` 裡，沒有框架、沒有建置流程
- 雙語靠 HTML 屬性 `data-zh` / `data-en` ＋ 底部一小段 JS 切換，加新文字時**兩個屬性都要寫**
- **不要讓遊戲截圖可以點擊放大**（原本有燈箱，後來移除了）——原圖解析度不夠，放大會露出破綻
- 改完務必用本機伺服器實測（見上面「本地預覽」），不要只看編輯器
