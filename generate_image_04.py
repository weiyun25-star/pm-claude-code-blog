"""
04 篇插圖 v2：範本倉庫結構示意圖（修正文字重疊）
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
POST_ID     = 1530
IMG_PATH    = Path(__file__).parent / "template-repo-hero.png"

CJK = [f for f in fm.findSystemFonts() if "NotoSansCJK" in f and "Regular" in f]
if CJK:
    fm.fontManager.addfont(CJK[0])
    FTC = fm.FontProperties(fname=CJK[0]).get_name()
else:
    FTC = "DejaVu Sans"

fig, ax = plt.subplots(figsize=(13, 7.2))
fig.patch.set_facecolor("#f8f9fc")
ax.set_facecolor("#f8f9fc")
ax.set_xlim(0, 13)
ax.set_ylim(0, 7.2)
ax.axis("off")

# 主標題
ax.text(6.5, 6.9, "pm-workspace  範本倉庫結構",
        ha="center", va="center", fontsize=15, fontweight="bold",
        color="#1a1a2e", fontfamily=FTC)

# ── 外框 ────────────────────────────────────────────────────
outer = FancyBboxPatch((0.3, 0.5), 12.4, 6.1,
                       boxstyle="round,pad=0.12",
                       facecolor="#ffffff", edgecolor="#3b5bdb", linewidth=2)
ax.add_patch(outer)
ax.text(0.75, 6.28, "pm-workspace/", fontsize=11, fontweight="bold",
        color="#3b5bdb", fontfamily=FTC, va="center")

# ── helper functions ────────────────────────────────────────
def card(ax, x, y, w, h, label, label_color, bg, border, rows):
    """
    rows: list of (line1_bold, line2_gray)
    """
    b = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0.06",
                       facecolor=bg, edgecolor=border, linewidth=1.4)
    ax.add_patch(b)
    # 區塊標題
    ax.text(x + 0.18, y + h - 0.26, label,
            fontsize=9, fontweight="bold", color=label_color,
            fontfamily=FTC, va="center")
    # 分隔線
    ax.plot([x + 0.12, x + w - 0.12], [y + h - 0.44, y + h - 0.44],
            color=border, lw=0.7, alpha=0.5)
    # 內容列
    row_y = y + h - 0.72
    for (main_txt, sub_txt) in rows:
        ax.text(x + 0.22, row_y, main_txt,
                fontsize=9, fontweight="bold", color="#333",
                fontfamily=FTC, va="center")
        if sub_txt:
            ax.text(x + 0.22, row_y - 0.26, sub_txt,
                    fontsize=7.8, color="#999", fontfamily=FTC, va="center")
        row_y -= 0.58 if sub_txt else 0.42

# ── 上排三個卡片 ─────────────────────────────────────────────
card(ax, 0.55, 3.55, 3.7, 2.45,
     "CLAUDE.md", "#c0392b", "#fff5f5", "#ffaaaa",
     [("CLAUDE.md", "AI 閱讀的規則檔"),
      ("語言偏好、筆記位置", None),
      ("角色設定、輸出格式", None)])

card(ax, 4.65, 3.55, 3.7, 2.45,
     "agents/", "#2f9e44", "#f0fff4", "#88dd99",
     [("prd-writer.md", "PRD 撰寫規則與格式"),
      ("user-researcher.md", "訪談紀錄整理規則"),
      ("new-project-sop.md", "新案開案標準流程")])

card(ax, 8.75, 3.55, 3.7, 2.45,
     "sop/", "#e67700", "#fff8f0", "#ffcc88",
     [("新案開案.md", "每次接案的固定步驟"),
      ("收案 checklist.md", "結案前逐項確認清單"),
      ("review-template.md", "三角色 review 框架")])

# ── 下排三個卡片 ─────────────────────────────────────────────
card(ax, 0.55, 0.85, 3.7, 2.45,
     "knowledge/", "#6741d9", "#f5f0ff", "#c9b8ff",
     [("PRODUCT.md", "產品背景與目標"),
      ("PERSONAS.md", "使用者角色設定"),
      ("COMPETITIVE.md", "競品分析資料")])

card(ax, 4.65, 0.85, 3.7, 2.45,
     "progress/", "#0c8599", "#f0faff", "#88ccee",
     [("BRIEF.md", "案子摘要＋目前進度區塊"),
      ("decisions.md", "重要決策紀錄"),
      ("blockers.md", "卡關問題追蹤")])

# ── 使用說明卡（右下）───────────────────────────────────────
card(ax, 8.75, 0.85, 3.7, 2.45,
     "新案子使用方式", "#555555", "#f5f5f5", "#aaaaaa",
     [("① clone 這份範本", "git clone pm-workspace [案名]"),
      ("② 更新 CLAUDE.md", "填入這個案子的背景資訊"),
      ("③ 開始工作", "AI 自動依規則配合")])

# ── 底部說明橫幅 ─────────────────────────────────────────────
banner = FancyBboxPatch((0.55, 0.54), 11.9, 0.28,
                        boxstyle="round,pad=0.03",
                        facecolor="#eef0ff", edgecolor="#c5cfee", linewidth=1)
ax.add_patch(banner)
ax.text(6.5, 0.68,
        "寫一次規則、建一套結構，之後每個新案子 clone 一份，AI 就能照同一套邏輯配合",
        ha="center", va="center", fontsize=9.5,
        color="#3b5bdb", fontfamily=FTC, fontweight="bold")

plt.tight_layout(pad=0.2)
fig.savefig(IMG_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"✅ 圖片生成：{IMG_PATH}")

# ── 上傳並更新文章（取代舊圖）────────────────────────────────
with open(IMG_PATH, "rb") as f:
    mr = requests.post(f"{WP_URL}/wp-json/wp/v2/media",
                       auth=(WP_USER, WP_APP_PASS),
                       headers={"Content-Disposition": 'attachment; filename="template-repo-hero.png"',
                                "Content-Type": "image/png"},
                       data=f, timeout=30)
if mr.status_code not in (200, 201):
    print(f"❌ 上傳失敗：{mr.text[:200]}"); exit(1)

new_img_url = mr.json()["source_url"]
new_img_id  = mr.json()["id"]
print(f"✅ 上傳成功 ID：{new_img_id}")

# 把文章裡的舊圖 URL 換成新圖
r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
                 auth=(WP_USER, WP_APP_PASS), timeout=20)
content = r.json()["content"]["rendered"]

# 取代 figure 裡的 src
old_src_pat = r'src="https://blog\.codefarm\.com\.tw/wp-content/uploads/[^"]*template-repo-hero[^"]*"'
updated = re.sub(old_src_pat, f'src="{new_img_url}"', content)

resp = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
                     auth=(WP_USER, WP_APP_PASS),
                     json={"content": updated, "featured_media": new_img_id},
                     timeout=30)
if resp.status_code in (200, 201):
    print(f"✅ 文章圖片更新完成：{resp.json()['link']}")
else:
    print(f"❌ 失敗：{resp.text[:200]}")
