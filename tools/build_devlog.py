#!/usr/bin/env python3
"""
從主遊戲專案 (DipanProj) 的 git 紀錄產生 public/devlog.html。

用法（在網站專案根目錄執行）：
    python3 tools/build_devlog.py

它會做三件事：
 1. 讀取 ../DipanProj 的 commit 紀錄（唯讀，只跑 git log，不會動到那個 repo）
 2. 濾掉純文件／雜項提交，並合併連續重複的訊息
 3. 套用 tools/devlog_template.html，輸出 public/devlog.html

要改頁面版型或前面三段里程碑影片的文案 → 改 tools/devlog_template.html
要改哪些提交要濾掉 → 改下面的 NOISE / 要改影片 → 見 README
"""

import os
import re
import sys
import html
import itertools
import subprocess
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_REPO = os.path.abspath(os.path.join(ROOT, "..", "DipanProj"))
TEMPLATE = os.path.join(ROOT, "tools", "devlog_template.html")
OUTPUT = os.path.join(ROOT, "public", "devlog.html")

# 這些提交訊息不會出現在日誌上（純文件、雜項、無意義訊息）
NOISE = {
    "test", "補文件", "補上文件", "寫入文件“", "修正警告", "first commit",
    "修正錯誤", "修改錯誤", "加入readme", "更新gotignore", "推上文件紀錄",
    "統一文件存放位置", "移除用不到的檔案", "修正過時文件內容",
}
# 開頭符合這些的也濾掉
NOISE_PREFIX = ("docs:", "Merge branch", "Merge pull", "補上文件", "補充文件")

MONTH_ZH = {1:"一月",2:"二月",3:"三月",4:"四月",5:"五月",6:"六月",
            7:"七月",8:"八月",9:"九月",10:"十月",11:"十一月",12:"十二月"}
MONTH_EN = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
            7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}


def read_git_log():
    if not os.path.isdir(os.path.join(GAME_REPO, ".git")):
        sys.exit(f"找不到主專案的 git repo：{GAME_REPO}\n"
                 f"（本腳本預期 DipanProj 與 DipanProj_WebSite 放在同一層）")
    # --no-optional-locks：避免 git 在別人的 repo 裡建立 index.lock
    cmd = ["git", "--no-optional-locks", "-C", GAME_REPO, "log",
           "--reverse", "--date=short", "--pretty=%ad\t%s"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit("git log 執行失敗：\n" + res.stderr)
    return res.stdout.splitlines()


def clean(lines):
    rows, prev = [], None
    for line in lines:
        line = line.rstrip()
        if not line.strip():
            continue
        date, _, subject = line.partition("\t")
        subject = subject.strip()
        if not subject or subject in NOISE:
            continue
        if subject.startswith(NOISE_PREFIX):
            continue
        if subject == prev:          # 連續重複的訊息只留一筆
            continue
        prev = subject
        rows.append((date, subject))
    return rows


def build_timeline(rows):
    out = []
    for ym, group in itertools.groupby(rows, key=lambda r: r[0][:7]):
        group = list(group)
        y, m = int(ym[:4]), int(ym[5:7])
        out.append('<section class="tl-month rv">')
        out.append(
            '<header class="mhead">'
            f'<span class="mnum">{y} / {m:02d}</span>'
            f'<span class="mname" data-zh="{MONTH_ZH[m]}" data-en="{MONTH_EN[m]}"></span>'
            f'<span class="mcount">{len(group)}</span>'
            "</header>"
        )
        for day, entries in itertools.groupby(group, key=lambda r: r[0]):
            entries = list(entries)
            label = f"{int(day[5:7]):02d} / {int(day[8:10]):02d}"
            out.append('<div class="tl-day">')
            out.append(f'<div class="dchip">{label}</div>')
            out.append('<ul class="dlist">')
            for _, subject in entries:
                out.append(f"<li>{html.escape(subject)}</li>")
            out.append("</ul></div>")
        out.append("</section>")
    return "\n".join(out)


def main():
    rows = clean(read_git_log())
    if not rows:
        sys.exit("清理後沒有任何提交紀錄，請檢查 NOISE 設定")

    first = datetime.date.fromisoformat(rows[0][0])
    last = datetime.date.fromisoformat(rows[-1][0])

    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()

    page = (page
            .replace("<!--TIMELINE-->", build_timeline(rows))
            .replace("{{COUNT}}", str(len(rows)))
            .replace("{{DAYS}}", str((last - first).days))
            .replace("{{FIRST}}", first.strftime("%Y.%m.%d"))
            .replace("{{LAST}}", last.strftime("%Y.%m.%d")))

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(page)

    print(f"完成：{OUTPUT}")
    print(f"  {len(rows)} 則紀錄　{first} → {last}　共 {(last-first).days} 天")


if __name__ == "__main__":
    main()
