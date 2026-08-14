# 官網踩坑記錄

> 格式沿用主專案 `readme/PROBLEMS.md`：**症狀 → 原因 → 解法**。
> 每遇到一個新坑就在這裡加一則，避免下次（或接手的人／AI）重踩。
>
> 代號：`W` = Website。

---

## W1　Cloudflare 後台找不到「加自訂網域」的地方

**症狀**
在 Worker 的 **Settings** 分頁裡翻遍了，只找到「Trigger events」，而且顯示
`Triggers cannot be added to a Worker that only has static assets`，看起來像是不支援。

**原因**
那句話講的是 **cron 排程、Queue 訊息**這類「觸發程式執行」的事件，跟網域無關。
純靜態網站沒有程式碼要跑，所以顯示不支援——這是正常的。
自訂網域被 Cloudflare 獨立到另一個分頁了。

**解法**
用 Worker 頁面**最上方那排分頁**的 **Domains**（位置在 `Observability` 和 `Settings` 中間）
→ `Custom Domains and Routes` → **Add Domain**。

---

## W2　根網域可以連，`www.` 開頭連不上（要兩個步驟才會通）

**症狀**
`https://thelampblack.com` 正常，`https://www.thelampblack.com` 打不開。

**原因**
在 DNS 的世界裡 `thelampblack.com` 和 `www.thelampblack.com` 是**兩個不同的主機名**，
Cloudflare 不會自動替你補。而且**只加 DNS 記錄還不夠**——見下面第二步。

**排查時看錯誤碼就知道卡在哪一關**

| 錯誤 | 卡在哪 |
|---|---|
| `Name or service not known` | DNS 根本沒有這筆記錄 |
| **`522 連線逾時`** | DNS 通了，但 Cloudflare 不知道該把請求交給誰 |
| 正常回應 | 完成 |

**為什麼加了 DNS 還會 522**

根網域那筆記錄的類型是 **Worker**（Cloudflare 的特殊型別，意思是「這個主機名交給 Worker 處理」）。
把 www 用 CNAME 指向根網域時，**這個 Worker 綁定不會沿著 CNAME 繼承下來**。
所以 Cloudflare 收到 www 的請求後去找後端伺服器，找不到，逾時回 522。

**解法（兩步都要做）**

**第一步 — 建 DNS 記錄**
Domains → `thelampblack.com` → DNS → Add record

| 欄位 | 值 |
|---|---|
| Type | `CNAME` |
| Name | `www` |
| Target | `thelampblack.com` |
| Proxy status | **Proxied（橘色雲朵，必須開）** |

**第二步 — 建 301 轉址規則**
Rules → Redirect Rules → Create rule

| 欄位 | 值 |
|---|---|
| Rule name | `www to apex` |
| If incoming requests match | Custom filter expression |
| Field / Operator / Value | `Hostname` / `equals` / `www.thelampblack.com` |
| Then → Type | **Dynamic** |
| Expression | `concat("https://thelampblack.com", http.request.uri.path)` |
| Status code | **301** |
| Preserve query string | ✅ |

用 **Dynamic** 而不是 Static，是為了讓路徑跟著帶過去
（`www.../sitemap.xml` → `thelampblack.com/sitemap.xml`，而不是被丟回首頁）。

轉址規則跑在 Cloudflare 邊緣，**在連後端之前就回應了**，所以能繞過 522。

**替代做法**
不想轉址、想讓兩個網址都直接提供內容的話，可以改用 Domains 分頁的
**Add Route**，規則填 `www.thelampblack.com/*`。
這樣不會跳轉，但會有兩個網址提供相同內容
（SEO 上靠 `index.html` 裡的 `<link rel="canonical">` 指明正版，不至於出問題）。

**測試時的注意事項 → 見 W11，無痕視窗沒有用**

---

## W3　repo 裡沒有 wrangler 設定檔，發布設定只存在後台

**症狀**
專案裡找不到 `wrangler.toml` / `wrangler.jsonc`，但部署卻正常運作。

**原因**
建立專案時是用 Cloudflare 後台的精靈設定的，「Build output directory = `public`」
這類設定存在 Cloudflare 伺服器端，沒有寫進 repo。

**影響與解法**
目前運作完全正常（已驗證線上只服務 `public/`：`/robots.txt` 回正確內容、`/README.md` 回 404）。

但要知道：**這個設定不在版控裡**。如果哪天要重建專案、或換帳號，
必須記得回去把「發布 `public/` 資料夾」重設一次，否則會把整個 repo（含 16MB 原始素材）發布出去。

想更保險的話，可以在 repo 根目錄補一份 wrangler 設定檔把它寫進版控。

---

## W4　本地預覽時影片不能播、favicon 不出現、語言切換不記憶

**症狀**
直接用 Finder 按兩下 `public/index.html` 打開，畫面看得到但功能怪怪的。

**原因**
`file://` 協定下，瀏覽器（尤其 Safari）會擋掉 `localStorage`，
影片載入和絕對路徑的 favicon（`/favicon.ico`）也解析不到。

**解法**
一律用本機伺服器，而且**要從 `public/` 目錄啟動**：

```bash
cd ~/Documents/workspaces/myProject/DipanProj_WebSite/public
python3 -m http.server 8000
```

然後開 http://localhost:8000

---

## W5　影片點了播放要等好幾秒才動

**症狀**
換了新影片之後，按播放鍵畫面卡住不動，等一陣子才開始播。

**原因**
MP4 的索引資訊（`moov` atom）預設放在檔案**尾端**，
瀏覽器必須把整個檔案下載完才知道怎麼解碼。

**解法**
轉檔時加 `-movflags +faststart`，把索引搬到檔頭：

```bash
ffmpeg -i 原始影片.mp4 -c copy -movflags +faststart public/video/teaser.mp4
```

`-c copy` 是直接複製串流不重新編碼，所以**無畫質損失、速度也快**。

驗證方式（`moov` 的位置要小於 `mdat`）：

```bash
python3 -c "
d=open('public/video/teaser.mp4','rb').read(200000)
print('moov', d.find(b'moov'), 'mdat', d.find(b'mdat'))"
```

---

## W6　單一檔案不能超過 25MB

**症狀**
放了比較長或高畫質的影片，部署失敗。

**原因**
Cloudflare Workers 靜態資源 / Pages 的**單檔上限是 25 MiB**。

**解法**
- 影片先壓過再放（降位元率或解析度）
- 或改用 YouTube 嵌入（外部託管，不佔這個額度）

目前 `teaser.mp4` 是 5.9MB，還很安全。

---

## W7　換了圖但線上還是舊的

**症狀**
更新了某張截圖、推上去也部署成功了，但瀏覽器看到的還是舊圖。

**原因**
`public/_headers` 裡設定了 `/assets/*` 快取一天（`max-age=86400`）。
Cloudflare 邊緣節點在每次部署後會自己更新，但**訪客瀏覽器裡的舊檔案還沒過期**。

**解法**
- 自己看：`Cmd + Shift + R` 強制重新整理
- 要讓所有訪客立刻看到：**換檔名**（例如 `shot_boss.webp` → `shot_boss2.webp`），
  順便改 `index.html` 裡的引用。改名等於是新的網址，一定不會撞到快取。

---

## W8　Cowork 橋接器不能覆寫也不能刪檔

**症狀**
（這則是給 AI 助手看的）
用 `device_bash` 解壓縮 tar 到專案資料夾，所有既有檔案都報 `Cannot open: File exists`；
用 `zip` 打包報 `Operation not permitted`。

**原因**
Cowork 的遠端掛載點是**唯建立**的：可以新增檔案、可以 `mv`，但不能覆寫、不能刪除。

**解法**
- 要更新既有檔案 → 用 `device_commit_files`（帶 `force: true`），它可以覆寫
- 要建立新檔或搬移 → `device_bash` 可以
- 要清垃圾 → 只能 `mv` 進 `_to_delete/`，再請使用者手動刪掉

---

## W9　卍字符號在西方的誤讀風險

**症狀**
（尚未發生，預先記錄）

**原因**
佛教左旋卍與納粹符號方向相反、也沒有旋轉 45 度，但在**小尺寸**下
（瀏覽器分頁 icon、Steam 膠囊圖縮圖、社群頭像）西方使用者往往分不出來。

**現況與判斷**
- 網站內文有兩處卍字（世界觀分隔符、頁尾），**大尺寸、佛教語境明確，判定沒問題**
- **favicon 刻意改用火焰書法的「燈」字**，避開小尺寸誤讀
- 遊戲內的卍字離場特效同理：在遊戲情境中很清楚，但若之後要做 Steam 膠囊圖或社群頭像，建議別用

---

## W11　DNS 設定改好了，但自己的電腦還是打不開（無痕視窗沒有用）

**症狀**
DNS 記錄和轉址規則都設定好了，別的裝置也開得起來，
但自己的 Mac 上 Chrome 一直顯示 `DNS_PROBE_FINISHED_NXDOMAIN`。
**開無痕視窗也一樣**。

**原因**
`NXDOMAIN` 是 **DNS 層**的錯誤，不是瀏覽器層的。
在網域還不存在的時候查詢過，系統會把「這個網域不存在」這個**否定結果快取起來**
（negative caching，通常存一小時左右），之後就直接回舊答案，根本不會再去問。

**無痕視窗只清 cookie 和頁面快取，碰不到 DNS 快取**——
DNS 快取在作業系統和 ISP 那一層，比瀏覽器更底層。

**解法（由快到慢）**

1. 清 macOS 的 DNS 快取：

```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

2. 清 Chrome 自己那一份：網址列輸入 `chrome://net-internals/#dns` → 按 **Clear host cache**

3. 什麼都不做，等一小時讓否定快取自然過期

**驗證是否真的修好了：用手機關掉 Wi-Fi、改用行動網路開。**
行動網路走電信商的 DNS，跟家裡的完全無關，沒有被污染的快取，
所以手機打得開就代表設定本身沒問題，剩下的只是自己電腦的快取問題。

---

## W10　抓取工具回報 www 可用，但實際不可用

**症狀**
（這則是給 AI 助手看的）
用 WebFetch 測 `https://www.thelampblack.com` 回報網站正常載入，
但使用者用真實瀏覽器打不開。

**原因**
抓取工具似乎會把主機名正規化，實際抓到的是根網域的內容，造成誤判。

**解法**
判斷 DNS 是否生效，**以使用者的真實瀏覽器測試為準**。
要用工具驗證的話，抓一個明確的子路徑（例如 `/robots.txt`）比抓首頁可靠——
DNS 真的沒解析時會直接回 `Name or service not known`。
