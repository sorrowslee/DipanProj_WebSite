#!/usr/bin/env python3
"""
從原始素材產生網站用的壓縮圖（WebP）到 assets/。

用法：
    npm run assets          （等同 python3 tools/build_assets.py）

需要 Pillow：
    pip3 install Pillow

要調整品質或尺寸，改下面的 SHOT_WIDTH / SHOT_QUALITY。
"""

import os
import re
import sys
import glob

try:
    from PIL import Image
except ImportError:
    sys.exit("找不到 Pillow，請先執行：pip3 install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS_DIR = os.path.join(ROOT, "遊戲內資源", "截圖")
OUT_DIR = os.path.join(ROOT, "public", "assets")

# --- 調整這裡 ---
SHOT_WIDTH = 1400      # 遊戲截圖輸出寬度（px）
SHOT_QUALITY = 74      # WebP 品質 0-100，越高越清楚也越大
# ----------------

# 原始截圖檔名（不含副檔名） -> (輸出檔名, 底部裁切比例)
# 新增截圖時在這裡加一行，再到 index.html 加對應的區塊（見 README）。
SHOT_MAP = {
    # 場景（用在「祂指過的地方」交錯排版區）
    "場景-初始森林":   ("sc_forest",   0.00),
    "場景-紅嫁衣":     ("sc_bride",    0.22),
    "場景-邪佛廣場":   ("sc_square",   0.22),
    "場景-邪佛":       ("shot_buddha", 0.20),  # 世界觀區塊的背景
    # 介面
    "介面-抽取武器":   ("shot_gacha",  0.00),
    # 武器（用在橫向卷軸區）
    "武器-幽冥鬼火":   ("w_ghostfire", 0.24),
    "武器-凍氣飛劍":   ("w_frost",     0.24),
    "武器-反彈彎刀":   ("w_bounce",    0.24),
    "武器-地裂之戟":   ("w_earth",     0.24),
    "武器-死字咒":     ("w_deathword", 0.24),
    "武器-喚靈水晶":   ("w_summon",    0.24),
    "武器-蟲洞":       ("w_wormhole",  0.24),
    "武器-青冥鏡":     ("w_mirror",    0.24),
}
# 註：第二個數字是「從底部裁掉的比例」，用來切掉遊戲的 HUD 操控列。
#     場景-初始森林 沒有 HUD 所以是 0。
#
# ⚠️ 右邊的輸出名稱必須和 public/index.html 裡 <img src="assets/…"> 用的檔名一致，
#    否則你更新了原始截圖、跑完腳本，網站上還是舊圖（而且不會有任何錯誤訊息）。
#    改動這裡之後，用這行檢查有沒有對上：
#      grep -oE 'assets/[a-z_0-9]+\.webp' public/index.html | sort -u


def trim_black_bars(im, threshold=10):
    """裁掉截圖邊緣純黑的信箱框。只裁「整列/整行都近乎全黑」的部分。"""
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    step = max(1, w // 160)          # 抽樣，避免逐像素太慢

    def row_black(y):
        return all(px[x, y] <= threshold for x in range(0, w, step))

    def col_black(x):
        return all(px[x, y] <= threshold for y in range(0, h, step))

    top = 0
    while top < h - 1 and row_black(top):
        top += 1
    bottom = h - 1
    while bottom > top and row_black(bottom):
        bottom -= 1
    left = 0
    while left < w - 1 and col_black(left):
        left += 1
    right = w - 1
    while right > left and col_black(right):
        right -= 1

    if (right - left) < w * 0.5 or (bottom - top) < h * 0.5:
        return im                    # 裁過頭就放棄，保留原圖
    return im.crop((left, top, right + 1, bottom + 1))


def convert(src, dst_name, width, quality, keep_alpha=False, trim=True, crop_bottom=0.0):
    im = Image.open(src)
    im = im.convert("RGBA" if keep_alpha else "RGB")
    if trim and not keep_alpha:
        im = trim_black_bars(im)
    if crop_bottom > 0:                       # 切掉底部的遊戲 HUD
        im = im.crop((0, 0, im.width, int(im.height * (1 - crop_bottom))))
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    dst = os.path.join(OUT_DIR, dst_name + ".webp")
    im.save(dst, "WEBP", quality=quality, method=6)
    kb = os.path.getsize(dst) // 1024
    print(f"  {dst_name}.webp  {im.width}x{im.height}  {kb}KB")


# ---------- 血統設定圖 ----------
# 這些是透明底的角色立繪，三隻要「等高」並排才好看，
# 所以走另一條處理路徑（依高度縮放），不套用上面的 SHOT_WIDTH。
BLOOD_DIR = os.path.join(ROOT, "遊戲內資源", "血統")
BLOOD_HEIGHT = 560
BLOOD_QUALITY = 86
# 第三個欄位 hidden=True 代表「這一階還不公開」，會輸出成剪影而不是原圖。
# 網站上對應的名稱要一起改成 ???（見 index.html 的 .bl-unknown）。
# 之後要公開就把 True 改成 False，重跑 npm run assets——輸出檔名不變，
# 所以 index.html 的 <img src> 不用動。
BLOOD_MAP = {
    # 資料夾名稱: [(來源檔名（不含副檔名）, 輸出名, 是否隱藏), ...]
    "殭屍": [
        ("1.殭屍", "bl_zombie1", False),
        ("2.毛殭", "bl_zombie2", True),
        ("3.旱魃", "bl_zombie3", True),
    ],
}

SIL_FILL = (14, 11, 9)        # 剪影本體的顏色。不是純黑——純黑在深色底上會整團消失
SIL_RIM = (255, 132, 60)      # 邊緣餘燼光的顏色
SIL_GROW = 9                  # 邊緣光往外擴幾像素
SIL_BLUR = 3


def to_silhouette(im):
    """把角色立繪壓成剪影：整片填暗色，外圍描一圈餘燼光。

    只用 alpha 通道當遮罩，所以原圖的任何細節（毛色、發光紋路）都不會殘留。
    ——試過「保留一點內部明暗」的版本，結果二階的白毛和三階的紋路還是看得出來，
       等於沒藏，所以這裡走完全填色。
    """
    from PIL import ImageFilter, ImageChops
    a = im.split()[3]

    body = Image.new("RGBA", im.size, SIL_FILL + (0,))
    body.putalpha(a)

    # alpha 外擴後減掉原本的 alpha = 一圈輪廓，再模糊成光暈
    edge = ImageChops.subtract(a.filter(ImageFilter.MaxFilter(SIL_GROW)), a)
    edge = edge.filter(ImageFilter.GaussianBlur(SIL_BLUR))
    edge = edge.point(lambda v: min(255, int(v * 0.88)))
    glow = Image.new("RGBA", im.size, SIL_RIM + (0,))
    glow.putalpha(edge)

    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(glow)     # 光在下
    out.alpha_composite(body)     # 身體在上
    return out


def build_bloodlines():
    if not os.path.isdir(BLOOD_DIR):
        return
    print("\n血統設定圖：")
    for folder, items in BLOOD_MAP.items():
        src_dir = os.path.join(BLOOD_DIR, folder)
        if not os.path.isdir(src_dir):
            print(f"  （找不到 {folder}/，略過）")
            continue
        for src_name, out_name, hidden in items:
            src = os.path.join(src_dir, src_name + ".png")
            if not os.path.isfile(src):
                print(f"  （找不到 {folder}/{src_name}.png，略過）")
                continue
            im = Image.open(src).convert("RGBA")
            im = im.crop(im.getbbox())          # 去掉四周多餘的透明區
            w = round(im.width * BLOOD_HEIGHT / im.height)
            im = im.resize((w, BLOOD_HEIGHT), Image.LANCZOS)
            if hidden:
                im = to_silhouette(im)
            dst = os.path.join(OUT_DIR, out_name + ".webp")
            im.save(dst, "WEBP", quality=BLOOD_QUALITY, method=6)
            tag = "  ← 剪影（未公開）" if hidden else ""
            print(f"  {out_name}.webp  {im.width}x{BLOOD_HEIGHT}  "
                  f"{os.path.getsize(dst)//1024}KB{tag}")


# ---------- 標題 logo ----------
# 遊戲內的火焰書法標題，透明底。首頁 hero 用。
# 中英文兩張的「留白比例」不一樣，所以這裡一律裁到實際筆畫邊界（alpha bbox），
# 版面那邊才好用一個寬度值把兩張的視覺高度對齊。
LOGO_DIR = os.path.join(ROOT, "遊戲內資源", "遊戲內圖片")
LOGO_WIDTH = 1250        # 輸出寬度；網頁上顯示約 625px，2 倍供高解析螢幕用
LOGO_QUALITY = 86
LOGO_MAP = {
    # 來源檔名（不含副檔名）: 輸出名
    "TitlePanel_Title": "logo_en",
}
# ⚠️ 中文的 logo.webp 沒有走這條路徑——它的原始檔不在這個 repo 裡，
#    是 2026-08 手動轉好直接放進 public/assets/ 的。
#    哪天要重做中文標題，記得把原始 PNG 也丟進 遊戲內圖片/ 並在上面加一行。


def build_logos():
    if not os.path.isdir(LOGO_DIR):
        return
    print("\n標題 logo：")
    for src_name, out_name in LOGO_MAP.items():
        src = os.path.join(LOGO_DIR, src_name + ".png")
        if not os.path.isfile(src):
            print(f"  （找不到 {src_name}.png，略過）")
            continue
        im = Image.open(src).convert("RGBA")
        im = im.crop(im.getbbox())      # 裁到實際筆畫邊界
        h = round(im.height * LOGO_WIDTH / im.width)
        im = im.resize((LOGO_WIDTH, h), Image.LANCZOS)
        dst = os.path.join(OUT_DIR, out_name + ".webp")
        im.save(dst, "WEBP", quality=LOGO_QUALITY, method=6)
        print(f"  {out_name}.webp  {LOGO_WIDTH}x{h}  {os.path.getsize(dst)//1024}KB")


def main():
    if not os.path.isdir(SHOTS_DIR):
        sys.exit(f"找不到截圖資料夾：{SHOTS_DIR}")
    os.makedirs(OUT_DIR, exist_ok=True)

    files = sorted(glob.glob(os.path.join(SHOTS_DIR, "*.png"))) \
          + sorted(glob.glob(os.path.join(SHOTS_DIR, "*.jpg")))

    if not files:
        sys.exit(f"{SHOTS_DIR} 裡沒有圖片")

    print(f"來源：{SHOTS_DIR}")
    print(f"輸出：{OUT_DIR}\n")

    done, skipped = 0, []
    for f in files:
        base = os.path.splitext(os.path.basename(f))[0]
        # 用完全比對，避免「場景-紅嫁衣」誤配到「場景-紅嫁衣2」
        entry = SHOT_MAP.get(base)
        if entry is None:
            skipped.append(base)
            continue
        name, cut = entry
        convert(f, name, SHOT_WIDTH, SHOT_QUALITY, crop_bottom=cut)
        done += 1

    print(f"\n完成 {done} 張。")
    if skipped:
        print("\n以下檔案沒有對應的輸出名稱，已略過：")
        for s in skipped:
            print(f"  - {s}")
        print("\n若要納入網站，請到本腳本的 SHOT_MAP 加一行，"
              "再到 index.html 加對應區塊（見 README「更新截圖」）。")

    build_bloodlines()
    build_logos()


if __name__ == "__main__":
    main()
