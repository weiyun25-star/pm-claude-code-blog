"""
03 篇插圖：Token 洩漏警示示意圖
上傳到 WordPress 並插入文章 1521（第一個 H2 前）
"""

import requests, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path

WP_URL      = "https://blog.codefarm.com.tw"
WP_USER     = "weiyun"
WP_APP_PASS = "LgWn IvQn mkmS JxlK AKVN Wask"
POST_ID     = 1521
IMG_PATH    = Path(__file__).parent / "token-leak-hero.png"

# ── 字體 ─────────────────────────────────────────────────────
CJK = [f for f in fm.findSystemFonts() if "NotoSansCJK" in f and "Regular" in f]
if CJK:
    fm.fontManager.addfont(CJK[0])
    FTC = fm.FontProperties(fname=CJK[0]).get_name()
else:
    FTC = "DejaVu Sans"

# ── 繪圖 ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5.5))
fig.patch.set_facecolor("#1a1a2e")
ax.set_facecolor("#1a1a2e")
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.5)
ax.axis("off")

# ── 終端機視窗外框 ────────────────────────────────────────────
win = FancyBboxPatch((0.5, 0.7), 11, 4.1,
                     boxstyle="round,pad=0.08",
                     facecolor="#0d0d1a", edgecolor="#333355",
                     linewidth=1.5)
ax.add_patch(win)

# 視窗頂列
bar = FancyBboxPatch((0.5, 4.45), 11, 0.35,
                     boxstyle="round,pad=0.04",
                     facecolor="#222240", edgecolor="none")
ax.add_patch(bar)
for i, c in enumerate(["#ff5f57","#febc2e","#28c840"]):
    ax.add_patch(plt.Circle((1.1 + i*0.32, 4.62), 0.1, color=c, zorder=5))
ax.text(6, 4.62, "Terminal — bash", ha="center", va="center",
        fontsize=9, color="#888", fontfamily=FTC)

# ── 指令行 ───────────────────────────────────────────────────
lines = [
    (1.0, 3.95, "$ git remote -v", "#7ec8e3", 10.5, "normal"),
    (1.0, 3.35,
     "origin  https://ghp_Ab3xK7mNqR2sT9vW1yZ0pL4uJ6cF8dE5iG:x-oauth-basic@github.com/weiyun/pm-workspace.git",
     "#ff6b6b", 10, "normal"),
    (1.0, 2.85,
     "                                    ↑ Token 就這樣明文夾在網址裡",
     "#ffb74d", 9.5, "italic"),
]
for lx, ly, txt, col, fs, sty in lines:
    ax.text(lx, ly, txt, ha="left", va="center",
            fontsize=fs, color=col, fontfamily=FTC,
            style=sty, fontweight="bold" if col=="#ff6b6b" else "normal")

# ── 警告框 ───────────────────────────────────────────────────
warn = FancyBboxPatch((0.85, 1.0), 10.3, 1.55,
                      boxstyle="round,pad=0.08",
                      facecolor="#2a1010", edgecolor="#ff4444",
                      linewidth=1.8)
ax.add_patch(warn)
ax.text(1.35, 2.32, "⚠", fontsize=20, color="#ff4444", va="center")
ax.text(1.9, 2.38, "任何看到這行網址的人，都能用你的身份操作 GitHub",
        fontsize=11, color="#ff8888", fontfamily=FTC, va="center", fontweight="bold")
ax.text(1.9, 1.88,
        "立即處理：GitHub → Settings → Developer settings → Personal access tokens → Revoke",
        fontsize=9, color="#ffb3b3", fontfamily=FTC, va="center")
ax.text(1.9, 1.52,
        "撤銷後再請 AI agent 把所有 remote URL 改成安全的 HTTPS 或 SSH 格式",
        fontsize=9, color="#ffb3b3", fontfamily=FTC, va="center")

plt.tight_layout(pad=0)
fig.savefig(IMG_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"✅ 圖片生成：{IMG_PATH}")

# ── 上傳 ─────────────────────────────────────────────────────
with open(IMG_PATH, "rb") as f:
    mr = requests.post(f"{WP_URL}/wp-json/wp/v2/media",
                       auth=(WP_USER, WP_APP_PASS),
                       headers={"Content-Disposition": 'attachment; filename="token-leak-hero.png"',
                                "Content-Type": "image/png"},
                       data=f, timeout=30)
if mr.status_code not in (200, 201):
    print(f"❌ 上傳失敗：{mr.text[:200]}"); exit(1)
img_url = mr.json()["source_url"]
img_id  = mr.json()["id"]
print(f"✅ 上傳成功 ID：{img_id}")

# ── 插入文章第一個 H2 前 ──────────────────────────────────────
r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
                 auth=(WP_USER, WP_APP_PASS), timeout=20)
content = r.json()["content"]["rendered"]

img_block = (
    f'\n<figure class="wp-block-image size-large" style="margin:0 0 2em;text-align:center;">'
    f'<img src="{img_url}" alt="GitHub Token 洩漏在 git remote URL 的資安警示" '
    f'style="max-width:100%;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.2);"/>'
    f'</figure>\n'
)
final = content.replace("<h2>", img_block + "<h2>", 1)

resp = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
                     auth=(WP_USER, WP_APP_PASS),
                     json={"content": final, "featured_media": img_id},
                     timeout=30)
if resp.status_code in (200, 201):
    print(f"✅ 文章更新：{resp.json()['link']}")
else:
    print(f"❌ 失敗：{resp.text[:200]}")
