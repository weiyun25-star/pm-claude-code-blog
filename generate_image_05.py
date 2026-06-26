"""
05 篇插圖：複製 vs 共用——多專案工具管理示意圖（深色背景版）
上傳到 WordPress 並插入草稿文章 1546（第一個 H2 前），不正式發佈
"""

import requests, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm
from pathlib import Path

WP_URL      = "https://blog.codefarm.com.tw"
WP_USER     = "weiyun"
WP_APP_PASS = "LgWn IvQn mkmS JxlK AKVN Wask"
POST_ID     = 1546
IMG_PATH    = Path(__file__).parent / "shared-agent-hero.png"

CJK = [f for f in fm.findSystemFonts() if "NotoSansCJK" in f and "Regular" in f]
if CJK:
    fm.fontManager.addfont(CJK[0])
    FTC = fm.FontProperties(fname=CJK[0]).get_name()
else:
    FTC = "DejaVu Sans"

BG          = "#1a1a2e"
PROJ_COLORS = ["#74c0fc", "#69db7c", "#ffa94d"]
PROJ_BG     = ["#0d1f35", "#0d2412", "#2d1800"]
AGENT_COLOR = "#da77f2"
AGENT_BG    = "#1e0a2a"
projects    = ["insurance/", "learnhub/", "pm-workspace/"]

fig, axes = plt.subplots(1, 2, figsize=(14, 6.2))
fig.patch.set_facecolor(BG)

for ax in axes:
    ax.set_facecolor(BG)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

# 分隔線
fig.add_artist(plt.Line2D([0.5, 0.5], [0.05, 0.95],
                          transform=fig.transFigure,
                          color="#333355", lw=1.5))

# ──────────────────────────────────────────────────────────────
# 左側：各自複製一份（BAD）
# ──────────────────────────────────────────────────────────────
ax = axes[0]
ax.text(3, 5.88, "× 各自複製一份", ha="center", fontsize=18,
        fontweight="bold", color="#ff6b6b", fontfamily=FTC)
ax.text(3, 5.42, "改了一份，其他份沒更新——三份開始長歪",
        ha="center", fontsize=13, color="#adb5bd", fontfamily=FTC)

for i, (proj, pc, pb) in enumerate(zip(projects, PROJ_COLORS, PROJ_BG)):
    y = 3.75 - i * 1.35
    box = FancyBboxPatch((0.25, y), 2.3, 1.1,
                         boxstyle="round,pad=0.07",
                         facecolor=pb, edgecolor=pc, linewidth=1.6)
    ax.add_patch(box)
    ax.text(1.4, y + 0.58, proj, ha="center", fontsize=13,
            fontweight="bold", color=pc, fontfamily=FTC)

    ab = FancyBboxPatch((3.1, y + 0.14), 2.5, 0.82,
                        boxstyle="round,pad=0.05",
                        facecolor=AGENT_BG, edgecolor="#aa66cc",
                        linewidth=1.2, linestyle="dashed")
    ax.add_patch(ab)
    ax.text(4.35, y + 0.55, "簡報 agent（副本）",
            ha="center", fontsize=12, color="#cc99ee", fontfamily=FTC)

    ax.annotate("", xy=(3.08, y + 0.55), xytext=(2.57, y + 0.55),
                arrowprops=dict(arrowstyle="-|>", color="#666688", lw=1.5))

warn = FancyBboxPatch((0.2, 0.22), 5.6, 0.82,
                      boxstyle="round,pad=0.07",
                      facecolor="#2d0a0a", edgecolor="#ff6b6b", linewidth=1.2)
ax.add_patch(warn)
ax.text(3, 0.63, "三份副本各自獨立——其中一份更新了，其他兩份不知道",
        ha="center", fontsize=12, color="#ff9999", fontfamily=FTC)

# ──────────────────────────────────────────────────────────────
# 右側：共用一份（GOOD）
# ──────────────────────────────────────────────────────────────
ax = axes[1]
ax.text(3, 5.88, "○ 集中維護，共用一份", ha="center", fontsize=18,
        fontweight="bold", color="#69db7c", fontfamily=FTC)
ax.text(3, 5.42, "改一次，所有案子馬上用到最新版",
        ha="center", fontsize=13, color="#adb5bd", fontfamily=FTC)

ca = FancyBboxPatch((1.5, 2.2), 3.0, 1.2,
                    boxstyle="round,pad=0.09",
                    facecolor=AGENT_BG, edgecolor=AGENT_COLOR, linewidth=2.2)
ax.add_patch(ca)
ax.text(3, 2.98, "presentation-templates/", ha="center",
        fontsize=12.5, fontweight="bold", color=AGENT_COLOR, fontfamily=FTC)
ax.text(3, 2.48, "共用簡報 agent（唯一一份）",
        ha="center", fontsize=12, color="#cc99ee", fontfamily=FTC)

proj_positions = [(0.45, 4.18), (2.0, 0.72), (3.75, 4.18)]
for (px, py), proj, pc, pb in zip(proj_positions, projects, PROJ_COLORS, PROJ_BG):
    box = FancyBboxPatch((px, py), 2.1, 0.95,
                         boxstyle="round,pad=0.07",
                         facecolor=pb, edgecolor=pc, linewidth=1.6)
    ax.add_patch(box)
    ax.text(px + 1.05, py + 0.48, proj, ha="center", fontsize=13,
            fontweight="bold", color=pc, fontfamily=FTC)

    cx, cy = 3.0, 2.80
    ex, ey = px + 1.05, py + (0.0 if py > 2 else 0.95)
    ax.annotate("", xy=(cx, cy), xytext=(ex, ey),
                arrowprops=dict(arrowstyle="-|>", color=AGENT_COLOR,
                                lw=1.8, connectionstyle="arc3,rad=0.08"))
    ax.text((cx + ex) / 2 + 0.12, (cy + ey) / 2,
            "引用", fontsize=11, color=AGENT_COLOR,
            fontfamily=FTC, ha="center")

ok = FancyBboxPatch((0.2, 0.22), 5.6, 0.82,
                    boxstyle="round,pad=0.07",
                    facecolor="#0d2412", edgecolor="#69db7c", linewidth=1.2)
ax.add_patch(ok)
ax.text(3, 0.63, "更新一次 → 三個案子同時用到最新版，不用各自複製",
        ha="center", fontsize=12, color="#99ee99", fontfamily=FTC)

plt.tight_layout(pad=0.5)
fig.savefig(IMG_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"圖片生成：{IMG_PATH}")

# ── 上傳 ─────────────────────────────────────────────────────
with open(IMG_PATH, "rb") as f:
    mr = requests.post(f"{WP_URL}/wp-json/wp/v2/media",
                       auth=(WP_USER, WP_APP_PASS),
                       headers={"Content-Disposition": 'attachment; filename="shared-agent-hero.png"',
                                "Content-Type": "image/png"},
                       data=f, timeout=30)
if mr.status_code not in (200, 201):
    print(f"上傳失敗：{mr.text[:200]}"); exit(1)
img_url = mr.json()["source_url"]
img_id  = mr.json()["id"]
print(f"上傳成功 ID：{img_id}")

# ── 移除舊圖，插入新圖（維持 draft）─────────────────────────
r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
                 auth=(WP_USER, WP_APP_PASS), timeout=20)
content = r.json()["content"]["rendered"]
clean = re.sub(r'\n?<figure[^>]*class="wp-block-image[^"]*"[^>]*>.*?</figure>\n?',
               '', content, count=1, flags=re.DOTALL)

img_block = (
    f'\n<figure class="wp-block-image size-large" style="margin:0 0 2em;text-align:center;">'
    f'<img src="{img_url}" alt="複製 vs 共用 agent——PM的AI應用旅程系列" '
    f'style="max-width:100%;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.15);"/>'
    f'</figure>\n'
)
final = clean.replace("<h2>", img_block + "<h2>", 1)

resp = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
                     auth=(WP_USER, WP_APP_PASS),
                     json={"content": final, "featured_media": img_id},
                     timeout=30)
if resp.status_code in (200, 201):
    print(f"草稿更新完成（狀態：{resp.json()['status']}）")
else:
    print(f"失敗：{resp.text[:200]}")
