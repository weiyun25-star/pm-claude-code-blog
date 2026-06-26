"""
02 篇插圖：本機資料夾 vs GitHub 倉庫對照表示意圖
上傳到 WordPress 並插入文章 1510
"""

import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.font_manager import FontProperties
import matplotlib.font_manager as fm
from pathlib import Path
import re

WP_URL      = "https://blog.codefarm.com.tw"
WP_USER     = "weiyun"
WP_APP_PASS = "LgWn IvQn mkmS JxlK AKVN Wask"
POST_ID     = 1510
IMG_PATH    = Path(__file__).parent / "folder-repo-diagram.png"

# ── 字體 ──────────────────────────────────────────────────────
CJK_PATHS = [f for f in fm.findSystemFonts() if "NotoSansCJK" in f and "Regular" in f]
if CJK_PATHS:
    fm.fontManager.addfont(CJK_PATHS[0])
    FONT_TC = fm.FontProperties(fname=CJK_PATHS[0]).get_name()
else:
    FONT_TC = "DejaVu Sans"

# ── 繪圖 ───────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5.8))
fig.patch.set_facecolor("#f8f9fc")
ax.set_facecolor("#f8f9fc")
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.8)
ax.axis("off")

# 標題
ax.text(6, 5.45, "本機資料夾 vs GitHub 倉庫——整理前後對比",
        ha="center", va="center", fontsize=14, fontweight="bold",
        color="#1a1a2e", fontfamily=FONT_TC)

# ── 整理前（左欄）────────────────────────────────────────────
ax.text(2.2, 4.95, "整理前", ha="center", fontsize=12,
        fontweight="bold", color="#c0392b", fontfamily=FONT_TC)

messy = [
    ("project/insurance",         "#ffeaea", "#e57373"),
    ("complete-course/learnhub",  "#ffeaea", "#e57373"),
    ("舊資料/SHOP-APP",            "#fff3e0", "#ffb74d"),
    ("舊資料/shop-app（重複）",    "#fff3e0", "#ffb74d"),
    ("Desktop/pm-workspace",      "#ffeaea", "#e57373"),
    ("找不到 coffee-quiz 在哪...", "#f5f5f5", "#bdbdbd"),
]
for i, (name, bg, border) in enumerate(messy):
    y = 4.35 - i * 0.62
    box = FancyBboxPatch((0.25, y - 0.22), 3.9, 0.44,
                         boxstyle="round,pad=0.04",
                         facecolor=bg, edgecolor=border, linewidth=1.2)
    ax.add_patch(box)
    ax.text(2.2, y, name, ha="center", va="center",
            fontsize=9.5, color="#444", fontfamily=FONT_TC)

# ── 中間箭頭 ──────────────────────────────────────────────────
ax.annotate("", xy=(6.8, 2.5), xytext=(5.2, 2.5),
            arrowprops=dict(arrowstyle="-|>", color="#3b5bdb", lw=2.5))
ax.text(6.0, 2.78, "整理後", ha="center", fontsize=10.5,
        color="#3b5bdb", fontweight="bold", fontfamily=FONT_TC)

# ── 整理後（右欄）────────────────────────────────────────────
ax.text(9.8, 4.95, "整理後", ha="center", fontsize=12,
        fontweight="bold", color="#2f9e44", fontfamily=FONT_TC)

clean = [
    ("repos/insurance",             "insurance",           "#e8f5e9", "#66bb6a"),
    ("repos/learnhub",              "learnhub",            "#e8f5e9", "#66bb6a"),
    ("repos/shop-app",              "shop-app",            "#e8f5e9", "#66bb6a"),
    ("repos/pm-workspace",          "pm-workspace",        "#e8f5e9", "#66bb6a"),
    ("repos/coffee-personality-quiz","coffee-personality-quiz","#e8f5e9","#66bb6a"),
]
for i, (local, repo, bg, border) in enumerate(clean):
    y = 4.35 - i * 0.62
    box = FancyBboxPatch((6.85, y - 0.22), 4.9, 0.44,
                         boxstyle="round,pad=0.04",
                         facecolor=bg, edgecolor=border, linewidth=1.2)
    ax.add_patch(box)
    ax.text(7.15, y, local, ha="left", va="center",
            fontsize=9.5, color="#2e7d32", fontfamily=FONT_TC)

# ── 底部原則說明 ──────────────────────────────────────────────
banner = FancyBboxPatch((0.25, 0.1), 11.5, 0.52,
                        boxstyle="round,pad=0.04",
                        facecolor="#eef0ff", edgecolor="#c5cfee", linewidth=1)
ax.add_patch(banner)
ax.text(6, 0.365,
        "資料夾命名 ＝ 倉庫名稱　→　你自己、同事、AI agent 看到名稱就知道它對應哪個倉庫",
        ha="center", va="center", fontsize=10, color="#3b5bdb",
        fontfamily=FONT_TC, fontweight="bold")

plt.tight_layout(pad=0.3)
fig.savefig(IMG_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"PNG 已生成：{IMG_PATH}")

# ── 上傳到 WordPress ──────────────────────────────────────────
print("上傳圖片...")
with open(IMG_PATH, "rb") as f:
    media_resp = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        auth=(WP_USER, WP_APP_PASS),
        headers={
            "Content-Disposition": 'attachment; filename="folder-repo-diagram.png"',
            "Content-Type": "image/png",
        },
        data=f, timeout=30,
    )

if media_resp.status_code not in (200, 201):
    print(f"❌ 上傳失敗：{media_resp.text[:200]}")
    exit(1)

image_url = media_resp.json()["source_url"]
image_id  = media_resp.json()["id"]
print(f"✅ 上傳成功 ID：{image_id}，URL：{image_url}")

# ── 讀取文章，插入圖片 ────────────────────────────────────────
r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
                 auth=(WP_USER, WP_APP_PASS), timeout=20)
content = r.json()["content"]["rendered"]

img_block = (
    f'\n<figure class="wp-block-image size-large" '
    f'style="margin:2em 0;text-align:center;">'
    f'<img src="{image_url}" '
    f'alt="本機資料夾與 GitHub 倉庫整理前後對比——PM的AI應用旅程系列" '
    f'style="max-width:100%;border-radius:12px;'
    f'box-shadow:0 2px 12px rgba(0,0,0,0.08);"/>'
    f'<figcaption style="font-size:0.85em;color:#888;margin-top:8px;">'
    f'整理前：資料夾名稱亂、巢狀深　→　整理後：全部在 repos/ 底下，名稱直接對應倉庫</figcaption>'
    f'</figure>\n'
)

# 插入第一個 <h2> 前
target = "<h2>"
updated = content.replace(target, img_block + target, 1)

resp = requests.post(
    f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
    auth=(WP_USER, WP_APP_PASS),
    json={"content": updated, "featured_media": image_id},
    timeout=30,
)
if resp.status_code in (200, 201):
    print(f"✅ 文章更新成功：{resp.json()['link']}")
else:
    print(f"❌ 更新失敗：{resp.text[:200]}")
