# LAMPBLACK 官方網站

《燃燈劫》/ **LAMPBLACK: Rebirth of Ruin** 的官方宣傳網站。

- 正式網址：https://thelampblack.com
- 主機：Cloudflare Pages（免費方案，流量無上限）
- 網域：Cloudflare Registrar

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

接上 GitHub 之後，**`git push` 就會自動部署**，不用做任何額外動作。

Cloudflare Pages 專案設定（建立時填一次）：

| 欄位 | 值 |
|---|---|
| Framework preset | None |
| Build command | （留空） |
| Build output directory | `public` |
| Root directory | `/` |

因為是純靜態網站沒有建置步驟，Build command 一定要留空。

---

## 待辦

- [ ] Steam 願望清單連結（`public/index.html` 搜尋「加入願望清單」）
- [ ] 開發日誌連結
- [ ] 英文標題 logo 重製（遊戲內 `TitlePanel_EN.png` 仍寫著舊名 Burning Lamp）
- [ ] 之後若要自架字體，把 Google Fonts 換成本地檔案
