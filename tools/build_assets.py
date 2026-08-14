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
    "9.48.58": "shot_buddha",      # 洞窟邪佛
    "9.45.40": "shot_boss",        # 榕樹妖登場
    "9.45.25": "shot_bride_talk",  # 紅嫁衣對話
    "9.46.35": "shot_hall",        # 紅嫁衣大廳
    "9.44.17": "shot_forest",      # 森林小徑
    "9.48.44": "shot_ritual",      # 圓形法陣
    "9.45.46": "shot_banyan",      # 大榕樹墳場
    "9.49.23": "shot_square",      # 邪佛廣場
    "9.46.08": "shot_ghosts",      # 鬼魂房間
}


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


def convert(src, dst_name, width, quality, keep_alpha=False, trim=True):
    im = Image.open(src)
    im = im.convert("RGBA" if keep_alpha else "RGB")
    if trim and not keep_alpha:
        im = trim_black_bars(im)
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
        base = os.path.basename(f)
        key = next((k for k in SHOT_MAP if k in base), None)
        if key is None:
            skipped.append(base)
            continue
        convert(f, SHOT_MAP[key], SHOT_WIDTH, SHOT_QUALITY)
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
