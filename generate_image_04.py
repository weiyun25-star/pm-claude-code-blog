"""
04 篇插圖：範本倉庫結構示意圖（字體放大版）
移除文章中的重複圖片，只保留一張放在「範本裡到底藏了哪些規則？」前
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

fig, ax = plt.subplots(figsize=(13, 7.5))
fig.patch.set_facecolor("#f8f9fc")
ax.set_facecolor("#f8f9fc")
ax.set_xlim(0, 13)
ax.set_ylim(0, 7.5)
ax.axis("off")

ax.text(6.5, 7.2, "pm-workspace  範本倉庫結構",
        ha="center", va="center", fontsize=18, fontweight="bold",
        color="#1a1a2e", fontfamily=FTC)

outer = FancyBboxPatch((0.3, 0.5), 12.4, 6.4,
                       boxstyle="round,pad=0.12",
                       facecolor="#ffffff", edgecolor="#3b5bdb", linewidth=2)
ax.add_patch(outer)
ax.text(0.75, 6.62, "pm-workspace/", fontsize=13, fontweight="bold",
        color="#3b5bdb", fontfamily=FTC, va="center")


def card(ax, x, y, w, h, label, label_color, bg, border, rows):
    b = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0.06",
                       facecolor=bg, edgecolor=border, linewidth=1.4)
    ax.add_patch(b)
    ax.text(x + 0.18, y + h - 0.28, label,
            fontsize=12, fontweight="bold", color=label_color,
            fontfamily=FTC, va="center")
    ax.plot([x + 0.12, x + w - 0.12], [y + h - 0.48, y + h - 0.48],
            color=border, lw=0.7, alpha=0.5)
    row_y = y + h - 0.76
    for (main_txt, sub_txt) in rows:
        ax.text(x + 0.22, row_y, main_txt,
                fontsize=12, fontweight="bold", color="#333",
                fontfamily=FTC, va="center")
        if sub_txt:
            ax.text(x + 0.22, row_y - 0.30, sub_txt,
                    fontsize=12, color="#888", fontfamily=FTC, va="center")
        row_y -= 0.64 if sub_txt else 0.46


# 上排
card(ax, 0.55, 3.55, 3.7, 2.65,
     "CLAUDE.md", "#c0392b", "#fff5f5", "#ffaaaa",
     [("CLAUDE.md", "AI 閱讀的規則檔"),
      ("語言偏好、筆記位置", None),
      ("角色設定、輸出格式", None)])

card(ax, 4.65, 3.55, 3.7, 2.65,
     "agents/", "#2f9e44", "#f0fff4", "#88dd99",
     [("prd-writer.md", "PRD 撰寫規則與格式"),
      ("user-researcher.md", "訪談紀錄整理規則"),
      ("new-project-sop.md", "新案開案標準流程")])

card(ax, 8.75, 3.55, 3.7, 2.65,
     "sop/", "#e67700", "#fff8f0", "#ffcc88",
     [("新案開案.md", "每次接案的固定步驟"),
      ("收案 checklist.md", "結案前逐項確認清單"),
      ("review-template.md", "三角色 review 框架")])

# 下排
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

card(ax, 8.75, 0.85, 3.7, 2.45,
     "新案子使用方式", "#555555", "#f5f5f5", "#aaaaaa",
     [("① clone 這份範本", "git clone pm-workspace [案名]"),
      ("② 更新 CLAUDE.md", "填入這個案子的背景資訊"),
      ("③ 開始工作", "AI 自動依規則配合")])

banner = FancyBboxPatch((0.55, 0.54), 11.9, 0.28,
                        boxstyle="round,pad=0.03",
                        facecolor="#eef0ff", edgecolor="#c5cfee", linewidth=1)
ax.add_patch(banner)
ax.text(6.5, 0.68,
        "寫一次規則、建一套結構，之後每個新案子 clone 一份，AI 就能照同一套邏輯配合",
        ha="center", va="center", fontsize=12,
        color="#3b5bdb", fontfamily=FTC, fontweight="bold")

plt.tight_layout(pad=0.2)
fig.savefig(IMG_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"圖片生成：{IMG_PATH}")

# ── 上傳 ─────────────────────────────────────────────────────
with open(IMG_PATH, "rb") as f:
    mr = requests.post(f"{WP_URL}/wp-json/wp/v2/media",
                       auth=(WP_USER, WP_APP_PASS),
                       headers={"Content-Disposition": 'attachment; filename="template-repo-hero.png"',
                                "Content-Type": "image/png"},
                       data=f, timeout=30)
if mr.status_code not in (200, 201):
    print(f"上傳失敗：{mr.text[:200]}"); exit(1)
new_img_url = mr.json()["source_url"]
new_img_id  = mr.json()["id"]
print(f"上傳成功 ID：{new_img_id}")

# ── 移除所有舊的結構圖 figure，插入一張到正確位置 ──────────────
r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
                 auth=(WP_USER, WP_APP_PASS), timeout=20)
content = r.json()["content"]["rendered"]

# 移除所有含 template-repo-hero 的 figure
clean = re.sub(
    r'\n?<figure[^>]*>(?:(?!</figure>).)*template-repo-hero[^<]*</figure>\n?',
    '', content, flags=re.DOTALL
)

new_block = (
    '\n<figure class="wp-block-image size-large" style="margin:2em 0;text-align:center;">'
    f'<img src="{new_img_url}" alt="pm-workspace 範本倉庫結構示意圖" '
    'style="max-width:100%;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.08);"/>'
    '</figure>\n'
)

target = re.search(r'<h2[^>]*>範本裡到底藏了哪些規則', clean)
if target:
    final = clean[:target.start()] + new_block + clean[target.start():]
    print("結構圖插入「範本裡到底藏了哪些規則？」前")
else:
    final = clean
    print("找不到目標 H2，圖片未插入")

resp = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
                     auth=(WP_USER, WP_APP_PASS),
                     json={"content": final},
                     timeout=30)
if resp.status_code in (200, 201):
    print(f"文章更新完成：{resp.json()['link']}")
else:
    print(f"失敗：{resp.text[:200]}")
