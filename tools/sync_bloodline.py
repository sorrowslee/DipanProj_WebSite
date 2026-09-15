#!/usr/bin/env python3
"""
從遊戲專案 DipanProj 抓每個血統的立繪來源圖，複製進 遊戲內資源/血統/<系列Key>/。

用法：
    python3 tools/sync_bloodline.py

抓的是每個血統 idle 動畫的**第一幀**（256×256 透明底），
也就是玩家在遊戲裡站著不動時看到的那一張。
複製完再跑 `npm run assets` 就會壓成 public/assets/bl_*.webp。

⚠ 這支腳本對遊戲專案是唯讀的，只複製檔案出來，不會寫回去。
⚠ 預期 DipanProj 與 DipanProj_WebSite 放在同一層；搬動資料夾要改 GAME_REPO。

血統有增減時，改下面的 SERIES（順序＝表A BloodlineSeriesTable.csv 的系列順序），
再到 tools/build_assets.py 的 BLOOD_MAP 與 public/index.html 補對應的區塊。
"""

import os
import glob
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_REPO = os.path.join(os.path.dirname(ROOT), "DipanProj")
SRC_ROOT = os.path.join(
    GAME_REPO, "DipanProj_Main", "Assets", "GameAssets", "Main",
    "Characters", "SequenceImage")
DST_ROOT = os.path.join(ROOT, "遊戲內資源", "血統")

# 系列 Key: [(遊戲裡的角色資料夾, 輸出檔名用的代號), ...]  ← 順序＝初階／中階／最終
# 左邊那個名字必須和遊戲 BloodlineTable.csv 的 SpriteFolder 後半一致（含空白）。
SERIES = {
    "Jiangshi":   [("Jiangshi", "Jiangshi"), ("Maojiang", "Maojiang"), ("Hanba", "Hanba")],
    "Bloodborn":  [("Bloodseeker", "Bloodseeker"), ("Crimson Count", "CrimsonCount"), ("Cain", "Cain")],
    "Feralborn":  [("Werewolf", "Werewolf"), ("Moonwatcher", "Moonwatcher"), ("Fenrir", "Fenrir")],
    "Gaiaborn":   [("Gargoyle", "Gargoyle"), ("MountainGiant", "MountainGiant"), ("Titan", "Titan")],
    "SpiritRoot": [("Foundation", "Foundation"), ("Nascent Soul", "NascentSoul"), ("Divine Form", "DivineForm")],
    "Cloudborn":  [("Jiao", "Jiao"), ("Chiwen", "Chiwen"), ("Yinglong", "Yinglong")],
    "Blazeborn":  [("Thrall", "Thrall"), ("Fafnir", "Fafnir"), ("Nidhogg", "Nidhogg")],
    "Swarmborn":  [("Parasite", "Parasite"), ("Ravager", "Ravager"), ("Swarm Emperor", "SwarmEmperor")],
}


def main():
    if not os.path.isdir(SRC_ROOT):
        sys.exit(f"找不到遊戲專案的序列圖資料夾：{SRC_ROOT}\n"
                 f"（預期 DipanProj 與本 repo 放在同一層）")

    done = 0
    for key, members in SERIES.items():
        dst_dir = os.path.join(DST_ROOT, key)
        os.makedirs(dst_dir, exist_ok=True)
        for stage, (folder, out) in enumerate(members, 1):
            frames = sorted(f for f in glob.glob(
                os.path.join(SRC_ROOT, key, folder, "idle", "*.png"))
                if not f.endswith(".meta"))
            if not frames:
                print(f"  ⚠ 找不到 {key}/{folder}/idle 的圖，略過")
                continue
            dst = os.path.join(dst_dir, f"{stage}_{out}.png")
            shutil.copyfile(frames[0], dst)
            print(f"  {key}/{stage}_{out}.png  ← {os.path.basename(frames[0])}")
            done += 1

    print(f"\n完成 {done} 張。接著跑：npm run assets")


if __name__ == "__main__":
    main()
