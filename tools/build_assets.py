#!/usr/bin/env python3
"""
從原始素材產生網站用的壓縮圖（WebP）到 assets/。

用法：
    python3 tools/build_assets.py

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

# 截圖檔名（片段） -> 輸出檔名。新增截圖時在這裡加一行，
# 然後到 index.html 的 <div class="grid"> 裡加對應的 <figure>。
SHOT_MAP = {
    # 場景（用在「祂指過的地方」交錯排版區）
    "場景-初始森林":   ("sc_forest",   0.00),
    "場景-紅嫁衣2":    ("sc_bride",    0.22),
    "場景-紅嫁衣":     ("sc_bride2",   0.22),
    "場景-邪佛廣場":   ("sc_square",   0.22),
    "場景-競技場":     ("sc_arena",    0.22),
    "場景-邪佛":       ("shot_buddha", 0.20),  # 全螢幕圖版用
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
              "再到 index.html 的 grid 區塊加 <figure>。")


if __name__ == "__main__":
    main()
