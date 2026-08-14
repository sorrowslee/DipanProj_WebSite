# LAMPBLACK 官方網站

《燃燈劫》/ **LAMPBLACK: Rebirth of Ruin** 的官方宣傳網站。

- 正式網址：https://thelampblack.com
- 主機：Cloudflare Pages（免費方案，流量無上限）
- 網域：Cloudflare Registrar

---

## 資料夾結構

```
DipanProj_WebSite/
├── index.html          ← 網站本體（單頁，HTML/CSS/JS 全部寫在裡面）
├── assets/             ← 網站實際使用的壓縮圖（WebP）
├── 截圖/                ← 遊戲截圖原始檔（來源，不會被網站直接讀取）
├── tools/
│   └── build_assets.py ← 從原始素材重新產生 assets/ 的壓縮腳本
├── .gitignore
└── README.md
```

**重點：`index.html` 只讀 `assets/` 裡的檔案。** `截圖/` 是原始素材保存區，改網站時不用動它。

---

## 本地預覽

因為是純靜態網站，直接用瀏覽器打開 `index.html` 就能看。

若要用本機伺服器（比較接近正式環境）：

```bash
python3 -m http.server 8000
# 然後開 http://localhost:8000
```

---

## 更新素材

把新的遊戲截圖丟進 `截圖/`，然後：

```bash
python3 tools/build_assets.py
```

腳本會自動壓成 WebP 放進 `assets/`。壓縮參數寫在腳本開頭，要調品質改那裡。

需要 Pillow：`pip3 install Pillow`

---

## 部署

（待補：Cloudflare Pages 接線完成後填入指令）

---

## 待辦

- [ ] Steam 願望清單連結（`index.html` 搜尋 `加入願望清單`）
- [ ] 開發日誌連結
- [ ] 英文標題 logo 重製（現有 `TitlePanel_EN.png` 仍寫著舊名 Burning Lamp）
- [ ] favicon
- [ ] 之後若要自架字體，把 Google Fonts 換成本地檔案
