"""
04 篇：
- 把結構圖移到「範本裡到底藏了哪些規則？」H2 前
- 新畫 PM 工作流底圖，插到第一個 H2 前並設為特色圖片
"""

import requests, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm
from pathlib import Path

WP_URL      = "https://blog.codefarm.com.tw"
WP_USER     = "weiyun"
WP_APP_PASS = "LgWn IvQn mkmS JxlK AKVN Wask"
POST_ID     = 1530
STRUCT_URL  = "https://blog.codefarm.com.tw/wp-content/uploads/2026/06/template-repo-hero-1.png"
HERO_PATH   = Path(__file__).parent / "pm-workflow-hero.png"

CJK = [f for f in fm.findSystemFonts() if "NotoSansCJK" in f and "Regular" in f]
if CJK:
    fm.fontManager.addfont(CJK[0])
    FTC = fm.FontProperties(fname=CJK[0]).get_name()
else:
    FTC = "DejaVu Sans"

# ── PM 工作流底圖 ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 5.5))
fig.patch.set_facecolor("#1a1a2e")
ax.set_facecolor("#1a1a2e")
ax.set_xlim(0, 13)
ax.set_ylim(0, 5.5)
ax.axis("off")

ax.text(6.5, 5.18, "PM 接案工作流——從接案到交付的固定路徑",
        ha="center", va="center", fontsize=13, fontweight="bold",
        color="#e8eaf6", fontfamily=FTC)

# 工作流步驟定義
steps = [
    ("接到案子",   "搞懂背景\n確認目標",    "#74c0fc", "#0d1f35"),
    ("使用者訪談", "訪談紀錄整理\n歸納痛點",  "#69db7c", "#0d2412"),
    ("寫 Spec",   "PRD / 需求文件\n版本控制", "#ffa94d", "#2d1800"),
    ("QA Review", "三角色審查\n壓力測試",    "#da77f2", "#1e0a2a"),
    ("交付",      "收案 checklist\n決策歸檔", "#ff6b6b", "#2d0a0a"),
]

n = len(steps)
card_w = 2.0
gap    = 0.42
start_x = (13 - n * card_w - (n - 1) * gap) / 2
card_y  = 1.1
card_h  = 2.9

for i, (title, desc, color, bg) in enumerate(steps):
    x = start_x + i * (card_w + gap)

    # 卡片
    box = FancyBboxPatch((x, card_y), card_w, card_h,
                         boxstyle="round,pad=0.08",
                         facecolor=bg, edgecolor=color, linewidth=1.8, zorder=3)
    ax.add_patch(box)

    # 步驟編號圓點
    ax.add_patch(plt.Circle((x + card_w / 2, card_y + card_h - 0.38),
                             0.28, color=color, zorder=4))
    ax.text(x + card_w / 2, card_y + card_h - 0.38, str(i + 1),
            ha="center", va="center", fontsize=12, fontweight="bold",
            color="#1a1a2e", zorder=5)

    # 標題
    ax.text(x + card_w / 2, card_y + card_h - 0.92, title,
            ha="center", va="center", fontsize=12, fontweight="bold",
            color=color, fontfamily=FTC, zorder=4)

    # 分隔線
    ax.plot([x + 0.18, x + card_w - 0.18],
            [card_y + card_h - 1.15, card_y + card_h - 1.15],
            color=color, lw=0.8, alpha=0.4, zorder=4)

    # 說明文字
    for j, line in enumerate(desc.split("\n")):
        ax.text(x + card_w / 2, card_y + card_h - 1.55 - j * 0.5, line,
                ha="center", va="center", fontsize=12, color="#cccccc",
                fontfamily=FTC, zorder=4)

    # 標籤（範本覆蓋提示）
    ax.text(x + card_w / 2, card_y + 0.28,
            "範本已涵蓋",
            ha="center", va="center", fontsize=12, color=color,
            fontfamily=FTC, alpha=0.75,
            bbox=dict(boxstyle="round,pad=0.2", facecolor=bg,
                      edgecolor=color, linewidth=0.8, alpha=0.9))

    # 箭頭
    if i < n - 1:
        ax.annotate("",
                    xy=(x + card_w + gap, card_y + card_h / 2),
                    xytext=(x + card_w, card_y + card_h / 2),
                    arrowprops=dict(arrowstyle="-|>", color="#555577", lw=1.8),
                    zorder=2)

# 底部說明
ax.text(6.5, 0.82,
        "每一步都有對應的 agent 規則和 SOP 範本——不用每次重新想，照著走就對了",
        ha="center", va="center", fontsize=12, color="#adb5bd",
        fontfamily=FTC, style="italic")

plt.tight_layout(pad=0)
fig.savefig(HERO_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"✅ 底圖生成：{HERO_PATH}")

# ── 上傳底圖 ─────────────────────────────────────────────────
with open(HERO_PATH, "rb") as f:
    mr = requests.post(f"{WP_URL}/wp-json/wp/v2/media",
                       auth=(WP_USER, WP_APP_PASS),
                       headers={"Content-Disposition": 'attachment; filename="pm-workflow-hero.png"',
                                "Content-Type": "image/png"},
                       data=f, timeout=30)
if mr.status_code not in (200, 201):
    print(f"❌ 上傳失敗：{mr.text[:200]}"); exit(1)
hero_url = mr.json()["source_url"]
hero_id  = mr.json()["id"]
print(f"✅ 底圖上傳 ID：{hero_id}")

# ── 讀取文章 ─────────────────────────────────────────────────
r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
                 auth=(WP_USER, WP_APP_PASS), timeout=20)
content = r.json()["content"]["rendered"]

# 移除現有 figure（結構圖，目前在第一個 H2 前）
fig_pat = r'\n?<figure[^>]*class="wp-block-image[^"]*"[^>]*>.*?</figure>\n?'
clean = re.sub(fig_pat, '', content, count=1, flags=re.DOTALL)

# 結構圖 block
struct_block = (
    '\n<figure class="wp-block-image size-large" style="margin:2em 0;text-align:center;">'
    f'<img src="{STRUCT_URL}" alt="pm-workspace 範本倉庫結構示意圖" '
    'style="max-width:100%;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.08);"/>'
    '</figure>\n'
)

# 底圖 block
hero_block = (
    '\n<figure class="wp-block-image size-large" style="margin:0 0 2em;text-align:center;">'
    f'<img src="{hero_url}" alt="PM 接案工作流示意圖——PM的AI應用旅程系列" '
    'style="max-width:100%;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.15);"/>'
    '</figure>\n'
)

# 把結構圖插到「範本裡到底藏了哪些規則？」H2 前
target_h2 = re.search(r'<h2[^>]*>範本裡到底藏了哪些規則', clean)
if target_h2:
    before = clean[:target_h2.start()]
    after  = clean[target_h2.start():]
    mid = before + struct_block + after
else:
    mid = clean
    print("⚠️ 找不到目標 H2，結構圖未插入")

# 底圖插到第一個 H2 前
final = mid.replace("<h2>", hero_block + "<h2>", 1)

resp = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
                     auth=(WP_USER, WP_APP_PASS),
                     json={"content": final, "featured_media": hero_id},
                     timeout=30)
if resp.status_code in (200, 201):
    print(f"✅ 文章更新：{resp.json()['link']}")
else:
    print(f"❌ 失敗：{resp.text[:200]}")
