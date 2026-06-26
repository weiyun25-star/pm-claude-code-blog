"""
生成 Git/Repo/GitHub 關係插圖（PNG），上傳到 WordPress，並更新文章 1502
"""

import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path

WP_URL      = "https://blog.codefarm.com.tw"
WP_USER     = "weiyun"
WP_APP_PASS = "LgWn IvQn mkmS JxlK AKVN Wask"
POST_ID     = 1502
IMG_PATH    = Path(__file__).parent / "git-repo-github-diagram.png"

# ── 繪製插圖 ──────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 5.2))
fig.patch.set_facecolor("#f8f9fc")
ax.set_facecolor("#f8f9fc")
ax.set_xlim(0, 11)
ax.set_ylim(0, 5.2)
ax.axis("off")

# 字體設定（fallback 處理）
import matplotlib.font_manager as fm
FONT_TC = "DejaVu Sans"
CJK_PATHS = [f for f in fm.findSystemFonts() if "NotoSansCJK" in f and "Regular" in f]
if CJK_PATHS:
    fm.fontManager.addfont(CJK_PATHS[0])
    FONT_TC = fm.FontProperties(fname=CJK_PATHS[0]).get_name()

def card(ax, x, y, w, h, bg, border, emoji, title, title_color, sub, lines):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                         linewidth=1.2, edgecolor=border, facecolor=bg)
    ax.add_patch(box)
    ax.text(x + w/2, y + h - 0.55, emoji, ha="center", va="center", fontsize=28)
    ax.text(x + w/2, y + h - 1.15, title, ha="center", va="center",
            fontsize=15, fontweight="bold", color=title_color, fontfamily=FONT_TC)
    ax.text(x + w/2, y + h - 1.6, sub, ha="center", va="center",
            fontsize=10, color="#555555", fontfamily=FONT_TC)
    ax.axhline(y=y + h - 1.85, xmin=(x + 0.18)/11, xmax=(x + w - 0.18)/11,
               color=border, linewidth=0.8, alpha=0.5)
    for i, line in enumerate(lines):
        ax.text(x + w/2, y + h - 2.35 - i*0.45, line, ha="center", va="center",
                fontsize=9.5, color="#666666", fontfamily=FONT_TC)

# 三張卡片
card(ax, 0.3, 0.7, 2.8, 3.8, "#ffffff", "#d0d7e8",
     "🔧", "Git", "#3b5bdb", "版本控制工具",
     ["記錄每次修改歷史", "追蹤誰改了什麼", "可回到之前版本"])

card(ax, 4.1, 0.7, 2.8, 3.8, "#ffffff", "#ffd8b0",
     "📁", "Repo", "#e67700", "本機資料夾",
     ["被 Git 追蹤的專案", "含隱藏的 .git 資料夾", "所有版本存在這裡"])

card(ax, 7.9, 0.7, 2.8, 3.8, "#ffffff", "#b2f2bb",
     "☁️", "GitHub", "#2f9e44", "雲端平台",
     ["備份 Repo 到雲端", "方便跨裝置協作", "電腦壞了東西還在"])

# 箭頭：Git → Repo（管理）
ax.annotate("", xy=(4.05, 2.6), xytext=(3.15, 2.6),
            arrowprops=dict(arrowstyle="-|>", color="#3b5bdb", lw=2))
ax.text(3.6, 2.78, "管理", ha="center", fontsize=10,
        color="#3b5bdb", fontweight="bold", fontfamily=FONT_TC)

# 箭頭：Repo → GitHub（push 同步）
ax.annotate("", xy=(7.85, 2.6), xytext=(6.95, 2.6),
            arrowprops=dict(arrowstyle="-|>", color="#2f9e44", lw=2))
ax.text(7.4, 2.78, "push", ha="center", fontsize=10,
        color="#2f9e44", fontweight="bold", fontfamily=FONT_TC)

# 底部說明橫幅
banner = FancyBboxPatch((0.3, 0.05), 10.4, 0.58,
                        boxstyle="round,pad=0.04",
                        linewidth=1, edgecolor="#c5cfee", facecolor="#eef0ff")
ax.add_patch(banner)
ax.text(5.5, 0.355,
        "commit ＝ 存檔（只存本機）　　push ＝ 上傳雲端（同步到 GitHub）　　兩個動作分開，commit 完不會自動 push",
        ha="center", va="center", fontsize=9.5, color="#444444", fontfamily=FONT_TC)

# 主標題
ax.text(5.5, 4.88, "Git ／ Repo ／ GitHub 的關係",
        ha="center", va="center", fontsize=14, fontweight="bold",
        color="#1a1a2e", fontfamily=FONT_TC)

plt.tight_layout(pad=0.3)
fig.savefig(IMG_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"PNG 已生成：{IMG_PATH}")

# ── 上傳到 WordPress Media Library ──────────────────────────
print("正在上傳圖片到 WordPress...")
with open(IMG_PATH, "rb") as f:
    media_resp = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        auth=(WP_USER, WP_APP_PASS),
        headers={
            "Content-Disposition": 'attachment; filename="git-repo-github-diagram.png"',
            "Content-Type": "image/png",
        },
        data=f,
        timeout=30,
    )

if media_resp.status_code not in (200, 201):
    print(f"❌ 上傳失敗（HTTP {media_resp.status_code}）：{media_resp.text[:300]}")
    exit(1)

media_data = media_resp.json()
image_url  = media_data["source_url"]
image_id   = media_data["id"]
print(f"✅ 圖片上傳成功！ID：{image_id}")
print(f"   URL：{image_url}")

# ── 讀取現有文章內容 ─────────────────────────────────────────
print("正在讀取現有文章內容...")
post_resp = requests.get(
    f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
    auth=(WP_USER, WP_APP_PASS),
    timeout=30,
)
if post_resp.status_code != 200:
    print(f"❌ 讀取文章失敗：{post_resp.text[:200]}")
    exit(1)

existing_content = post_resp.json()["content"]["rendered"]

# ── 插圖塊：置於第一個 <h2> 之前 ────────────────────────────
img_block = (
    f'\n<figure class="wp-block-image size-large" '
    f'style="margin:2em 0;text-align:center;">'
    f'<img src="{image_url}" '
    f'alt="Git、Repo、GitHub 三者關係示意圖——PM的AI應用旅程系列" '
    f'style="max-width:100%;border-radius:12px;'
    f'box-shadow:0 2px 12px rgba(0,0,0,0.08);"/>'
    f'<figcaption style="font-size:0.85em;color:#888;margin-top:8px;">'
    f'Git ＝ 工具、Repo ＝ 本機專案資料夾、GitHub ＝ 雲端備份平台</figcaption>'
    f'</figure>\n'
)

if "<h2>" in existing_content:
    updated_content = existing_content.replace("<h2>", img_block + "<h2>", 1)
else:
    updated_content = img_block + existing_content

# ── 更新文章 ─────────────────────────────────────────────────
print("正在更新文章...")
update_resp = requests.post(
    f"{WP_URL}/wp-json/wp/v2/posts/{POST_ID}",
    auth=(WP_USER, WP_APP_PASS),
    json={
        "content":        updated_content,
        "featured_media": image_id,
    },
    timeout=30,
)

if update_resp.status_code in (200, 201):
    print(f"✅ 文章更新成功！連結：{update_resp.json()['link']}")
else:
    print(f"❌ 更新失敗（HTTP {update_resp.status_code}）：{update_resp.text[:300]}")
