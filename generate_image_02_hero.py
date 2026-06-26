"""
02 篇：
- 把現有對照圖移到「步驟教學」H2 前
- 新畫一張散亂資料夾底圖，插到文章第一個 H2 前並設為特色圖片
"""

import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm
import matplotlib.transforms as mtransforms
import numpy as np
import re
from pathlib import Path

WP_URL      = "https://blog.codefarm.com.tw"
WP_USER     = "weiyun"
WP_APP_PASS = "LgWn IvQn mkmS JxlK AKVN Wask"
POST_ID     = 1510
DIAGRAM_URL = "https://blog.codefarm.com.tw/wp-content/uploads/2026/06/folder-repo-diagram.png"
HERO_PATH   = Path(__file__).parent / "folder-chaos-hero.png"

# ── 字體 ──────────────────────────────────────────────────────
CJK_PATHS = [f for f in fm.findSystemFonts() if "NotoSansCJK" in f and "Regular" in f]
if CJK_PATHS:
    fm.fontManager.addfont(CJK_PATHS[0])
    FONT_TC = fm.FontProperties(fname=CJK_PATHS[0]).get_name()
else:
    FONT_TC = "DejaVu Sans"

# ── 繪製散亂資料夾底圖 ────────────────────────────────────────
np.random.seed(42)
fig, ax = plt.subplots(figsize=(12, 5.5))
fig.patch.set_facecolor("#1e1e2e")
ax.set_facecolor("#1e1e2e")
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.5)
ax.axis("off")

# 資料夾卡片資料（名稱、x、y、旋轉角、顏色組）
folders = [
    ("project/",          0.5,  4.0, -12, "#ff6b6b", "#2d1b1b"),
    ("Desktop/舊資料/",    2.2,  3.5,   8, "#ffa94d", "#2d2010"),
    ("complete-course/",   4.5,  4.2,  -5, "#74c0fc", "#0d1f2d"),
    ("SHOP-APP/",          1.8,  1.8,  15, "#ff6b6b", "#2d1b1b"),
    ("shop-app/（重複）",   6.8,  3.8,  -9, "#ff6b6b", "#2d1b1b"),
    ("insurance/",         9.2,  4.1,   6, "#ffa94d", "#2d2010"),
    ("docs2_final/",       3.2,  2.6,  -7, "#a9e34b", "#1a2410"),
    ("tmp_backup/",        7.5,  1.9,  11, "#da77f2", "#1e0d2a"),
    ("learnhub copy/",     5.6,  2.0,  -4, "#ff6b6b", "#2d1b1b"),
    ("pm-workspace/",     10.2,  2.8,  -8, "#74c0fc", "#0d1f2d"),
    ("resume-grace/",      0.8,  2.4,   5, "#a9e34b", "#1a2410"),
    ("???/",              10.8,  4.5,  13, "#868e96", "#1a1a1a"),
    ("coffee-quiz copy2/", 8.5,  3.1,  -6, "#ffa94d", "#2d2010"),
]

for name, x, y, angle, fg, bg in folders:
    # 資料夾本體（圓角矩形）
    w, h = 2.0, 0.68
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.06",
                         facecolor=bg, edgecolor=fg,
                         linewidth=1.4, zorder=3)
    t = mtransforms.Affine2D().rotate_deg_around(x, y, angle) + ax.transData
    box.set_transform(t)
    ax.add_patch(box)

    # 資料夾耳朵（小矩形在上方）
    ear = FancyBboxPatch((x - w/2, y + h/2 - 0.04), w * 0.38, 0.18,
                          boxstyle="round,pad=0.02",
                          facecolor=fg, edgecolor=fg,
                          linewidth=0, alpha=0.7, zorder=2)
    ear.set_transform(t)
    ax.add_patch(ear)

    ax.text(x, y, name, ha="center", va="center",
            fontsize=12, color=fg, fontfamily=FONT_TC,
            fontweight="bold", zorder=4,
            transform=t)

# 散落的小檔案點
for _ in range(35):
    rx, ry = np.random.uniform(0.3, 11.7), np.random.uniform(0.4, 5.1)
    rc = np.random.choice(["#ff6b6b","#ffa94d","#74c0fc","#a9e34b","#da77f2","#868e96"])
    ax.plot(rx, ry, ".", color=rc, alpha=0.35, markersize=4, zorder=1)

# 中央標題文字
ax.text(6.0, 0.85, "同一個專案，可能同時藏在三個地方都找不到",
        ha="center", va="center", fontsize=12,
        color="#adb5bd", fontfamily=FONT_TC, style="italic")

plt.tight_layout(pad=0)
fig.savefig(HERO_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"底圖已生成：{HERO_PATH}")

# ── 上傳底圖 ──────────────────────────────────────────────────
print("上傳底圖...")
with open(HERO_PATH, "rb") as f:
    media_resp = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        auth=(WP_USER, WP_APP_PASS),
        headers={
            "Content-Disposition": 'attachment; filename="folder-chaos-hero.png"',
            "Content-Type": "image/png",
        },
        data=f, timeout=30,
    )
if media_resp.status_code not in (200, 201):
    print(f"❌ 上傳失敗：{media_resp.text[:200]}")
    exit(1)
hero_url = media_resp.json()["source_url"]
hero_id  = media_resp.json()["id"]
print(f"✅ 底圖上傳成功 ID：{hero_id}")

# ── 讀取現有文章內容 ──────────────────────────────────────────
r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
                 auth=(WP_USER, WP_APP_PASS), timeout=20)
content = r.json()["content"]["rendered"]

# 替換 hero 圖 src（避免重複插圖）
hero_src = re.search(r'src="([^"]*folder-chaos-hero[^"]*)"', content)
if hero_src:
    final_content = content.replace(hero_src.group(1), hero_url)
else:
    # 首次插入：移除舊圖、重新排版
    fig_pattern = r'\n?<figure[^>]*class="wp-block-image[^"]*"[^>]*>.*?</figure>\n?'
    content_clean = re.sub(fig_pattern, '', content, count=1, flags=re.DOTALL)
    diagram_block = (
        '\n<figure class="wp-block-image size-large" style="margin:2em 0;text-align:center;">'
        f'<img src="{DIAGRAM_URL}" alt="本機資料夾與 GitHub 倉庫整理前後對比" '
        'style="max-width:100%;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.08);"/>'
        '</figure>\n'
    )
    content_with_diagram = re.sub(
        r'(<h2[^>]*>步驟教學[^<]*</h2>)',
        diagram_block + r'\1', content_clean, count=1,
    )
    hero_block = (
        '\n<figure class="wp-block-image size-large" style="margin:0 0 2em;text-align:center;">'
        f'<img src="{hero_url}" alt="散亂的專案資料夾示意圖——PM的AI應用旅程系列" '
        'style="max-width:100%;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.15);"/>'
        '</figure>\n'
    )
    final_content = content_with_diagram.replace("<h2>", hero_block + "<h2>", 1)

# ── 更新文章 ──────────────────────────────────────────────────
resp = requests.post(
    f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
    auth=(WP_USER, WP_APP_PASS),
    json={"content": final_content, "featured_media": hero_id},
    timeout=30,
)
if resp.status_code in (200, 201):
    print(f"✅ 文章更新成功：{resp.json()['link']}")
else:
    print(f"❌ 更新失敗：{resp.text[:300]}")
